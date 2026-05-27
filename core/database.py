"""
Persistência MySQL: estado da automação + catálogo Plune (subcentros).

Database dedicado: gebras_automacao (credenciais em .env).
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

import pymysql
from pymysql.cursors import DictCursor

from .config import (
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    PLUNE_PEDIDO_MODELO_ID,
    PLUNE_PEDIDO_SERIE,
)

# Seed único na 1ª criação do banco (não duplicar em gebras_defaults.py)
_SEED_PIPEDRIVE_FILIAL: tuple[tuple[str, str], ...] = (
    ("Matriz", "751"),
    ("Iribarrem San Martin", "790"),
    ("57", "751"),
    ("56", "790"),
)
_SEED_BRANCH_CONFIG: dict[str, dict[str, str]] = {
    "751": {
        "label": "Matriz",
        "subcentro_custo_id": "447",
        "parametro_contabil_recorrente": "1077",
        "parametro_contabil_implantacao": "1440",
        "pedido_serie": "1",
        "pedido_modelo_id": "01",
    },
    "790": {
        "label": "Iribarrem San Martin (ISM)",
        "subcentro_custo_id": "449",
        "parametro_contabil_recorrente": "1102",
        "parametro_contabil_implantacao": "1436",
        "pedido_serie": "0",
        "pedido_modelo_id": "01",
    },
}
_SEED_DEFAULT_BRANCH_ID = "790"

_SCHEMA_VERSION = 6
_initialized = False


class _ExecuteResult:
    def __init__(self, cursor: pymysql.cursors.Cursor) -> None:
        self._cursor = cursor

    def fetchone(self) -> dict[str, Any] | None:
        return self._cursor.fetchone()

    def fetchall(self) -> list[dict[str, Any]]:
        return list(self._cursor.fetchall())

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount


class DbConnection:
    """Adaptador estilo sqlite3.execute para PyMySQL + DictCursor."""

    def __init__(self, raw: pymysql.connections.Connection) -> None:
        self._raw = raw

    def execute(self, sql: str, params: tuple | list | None = None) -> _ExecuteResult:
        cur = self._raw.cursor(DictCursor)
        cur.execute(sql, params or ())
        return _ExecuteResult(cur)

    def commit(self) -> None:
        self._raw.commit()

    def rollback(self) -> None:
        self._raw.rollback()

    def close(self) -> None:
        self._raw.close()


def mysql_connect_kwargs(*, database: str | None = None) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": False,
    }
    if database is not None:
        kwargs["database"] = database
    return kwargs


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def db_conn() -> Iterator[DbConnection]:
    global _initialized
    if not MYSQL_HOST or not MYSQL_USER:
        raise RuntimeError(
            "MySQL não configurado: defina MYSQL_HOST, MYSQL_USER e MYSQL_PASSWORD no .env"
        )
    raw = pymysql.connect(**mysql_connect_kwargs(database=MYSQL_DATABASE))
    conn = DbConnection(raw)
    try:
        if not _initialized:
            _init_schema(conn)
            _seed_catalogo_inicial(conn)
            _initialized = True
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _init_schema(conn: DbConnection) -> None:
    statements = [
        """
        CREATE TABLE IF NOT EXISTS app_meta (
            `key` VARCHAR(128) PRIMARY KEY,
            value TEXT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS deals_processed (
            deal_id VARCHAR(32) NOT NULL,
            won_time VARCHAR(64) NOT NULL,
            processed_at VARCHAR(64) NOT NULL,
            PRIMARY KEY (deal_id, won_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS deals_legacy_block (
            deal_id VARCHAR(32) PRIMARY KEY,
            blocked_at VARCHAR(64) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS pedidos_plune_keys (
            pedido_key VARCHAR(128) PRIMARY KEY,
            created_at VARCHAR(64) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS envelopes_pending (
            deal_id VARCHAR(32) PRIMARY KEY,
            envelope_id VARCHAR(128) NOT NULL,
            envelope_name VARCHAR(512) NOT NULL,
            created_at VARCHAR(64) NOT NULL,
            pedidos_plune_criados TINYINT(1) NOT NULL DEFAULT 0,
            pedidos_plune_aprovados TINYINT(1) NOT NULL DEFAULT 0,
            pedido_plune_id VARCHAR(64) NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS pipedrive_filial (
            pipe_key VARCHAR(128) PRIMARY KEY,
            branch_id VARCHAR(16) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS branch_config (
            branch_id VARCHAR(16) PRIMARY KEY,
            label VARCHAR(255) NOT NULL,
            subcentro_custo_id VARCHAR(32) NOT NULL,
            parametro_contabil_recorrente VARCHAR(32) NOT NULL,
            parametro_contabil_implantacao VARCHAR(32) NOT NULL,
            pedido_serie VARCHAR(8) NOT NULL DEFAULT '0',
            pedido_modelo_id VARCHAR(8) NOT NULL DEFAULT '01'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS plune_subcentro (
            branch_id VARCHAR(16) NOT NULL,
            `level` INT NOT NULL,
            pipe_label VARCHAR(255) NOT NULL,
            plune_id VARCHAR(32) NOT NULL,
            plune_label VARCHAR(255) NULL,
            uso_count INT NOT NULL DEFAULT 0,
            updated_at VARCHAR(64) NOT NULL,
            PRIMARY KEY (branch_id, `level`, pipe_label)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE INDEX idx_plune_subcentro_lookup
            ON plune_subcentro (branch_id, `level`, pipe_label)
        """,
    ]
    for sql in statements:
        try:
            conn.execute(sql)
        except pymysql.err.OperationalError as exc:
            # Índice já existe em reexecução
            if exc.args[0] != 1061:
                raise
    conn.execute(
        "INSERT IGNORE INTO app_meta (`key`, value) VALUES (%s, %s)",
        ("schema_version", str(_SCHEMA_VERSION)),
    )
    _migrate_schema(conn)


def _migrate_schema(conn: DbConnection) -> None:
    row = conn.execute(
        "SELECT value FROM app_meta WHERE `key` = 'schema_version'"
    ).fetchone()
    try:
        version = int(row["value"]) if row else 0
    except (TypeError, ValueError):
        version = 0
    if version >= _SCHEMA_VERSION:
        return
    if version < 3:
        try:
            conn.execute(
                """
                ALTER TABLE branch_config
                ADD COLUMN pedido_serie VARCHAR(8) NOT NULL DEFAULT '0'
                """
            )
        except pymysql.err.OperationalError as exc:
            if exc.args[0] != 1060:
                raise
        conn.execute(
            "UPDATE branch_config SET pedido_serie = %s WHERE pedido_serie IS NULL OR pedido_serie = ''",
            (PLUNE_PEDIDO_SERIE,),
        )
    if version < 4:
        try:
            conn.execute(
                """
                ALTER TABLE branch_config
                ADD COLUMN pedido_modelo_id VARCHAR(8) NOT NULL DEFAULT '01'
                """
            )
        except pymysql.err.OperationalError as exc:
            if exc.args[0] != 1060:
                raise
        conn.execute(
            "UPDATE branch_config SET pedido_modelo_id = %s WHERE branch_id = %s",
            ("**", "751"),
        )
        conn.execute(
            "UPDATE branch_config SET pedido_modelo_id = %s WHERE branch_id = %s",
            ("01", "790"),
        )
        conn.execute(
            """
            UPDATE branch_config
            SET pedido_modelo_id = %s
            WHERE pedido_modelo_id IS NULL OR pedido_modelo_id = ''
            """,
            (PLUNE_PEDIDO_MODELO_ID,),
        )
    if version < 5:
        # Alinha com pedidos manuais de referência (6754 Matriz, 6764 ISM) e Venda.NotaConfig
        conn.execute(
            """
            UPDATE branch_config
            SET pedido_serie = %s, pedido_modelo_id = %s
            WHERE branch_id = %s
            """,
            ("1", "01", "751"),
        )
        conn.execute(
            """
            UPDATE branch_config
            SET pedido_serie = %s, pedido_modelo_id = %s
            WHERE branch_id = %s
            """,
            ("0", "01", "790"),
        )
    if version < 6:
        # Remove coluna que chegou a existir em versões intermediárias
        try:
            conn.execute("ALTER TABLE plune_subcentro DROP COLUMN resp_comercial")
        except pymysql.err.OperationalError as exc:
            # 1091 = Can't DROP ... check that column/key exists
            if exc.args[0] != 1091:
                raise
    conn.execute(
        "UPDATE app_meta SET value = %s WHERE `key` = 'schema_version'",
        (str(_SCHEMA_VERSION),),
    )


def _seed_catalogo_inicial(conn: DbConnection) -> None:
    """Popula filiais e branch_config só se as tabelas estiverem vazias."""
    n_filial = conn.execute("SELECT COUNT(*) AS c FROM pipedrive_filial").fetchone()["c"]
    if n_filial == 0:
        for pipe_key, branch_id in _SEED_PIPEDRIVE_FILIAL:
            conn.execute(
                "INSERT INTO pipedrive_filial (pipe_key, branch_id) VALUES (%s, %s)",
                (pipe_key, branch_id),
            )

    n_branch = conn.execute("SELECT COUNT(*) AS c FROM branch_config").fetchone()["c"]
    if n_branch == 0:
        for branch_id, cfg in _SEED_BRANCH_CONFIG.items():
            conn.execute(
                """
                INSERT INTO branch_config (
                    branch_id, label, subcentro_custo_id,
                    parametro_contabil_recorrente, parametro_contabil_implantacao,
                    pedido_serie, pedido_modelo_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(branch_id),
                    cfg["label"],
                    cfg["subcentro_custo_id"],
                    cfg["parametro_contabil_recorrente"],
                    cfg["parametro_contabil_implantacao"],
                    cfg.get("pedido_serie", PLUNE_PEDIDO_SERIE),
                    cfg.get("pedido_modelo_id", PLUNE_PEDIDO_MODELO_ID),
                ),
            )

    row = conn.execute(
        "SELECT value FROM app_meta WHERE `key` = 'default_branch_id'"
    ).fetchone()
    if not row:
        conn.execute(
            "INSERT INTO app_meta (`key`, value) VALUES (%s, %s)",
            ("default_branch_id", _SEED_DEFAULT_BRANCH_ID),
        )


# --- Filial Pipedrive -> Branch Plune ---


def default_branch_id() -> str:
    with db_conn() as conn:
        row = conn.execute(
            "SELECT value FROM app_meta WHERE `key` = 'default_branch_id'"
        ).fetchone()
    return str(row["value"]) if row else ""


def filial_branch_map() -> dict[str, str]:
    with db_conn() as conn:
        rows = conn.execute(
            "SELECT pipe_key, branch_id FROM pipedrive_filial ORDER BY pipe_key"
        ).fetchall()
    return {r["pipe_key"]: r["branch_id"] for r in rows}


def filial_tem_mapeamento(pipe_label: str, pipe_option_id: str) -> bool:
    return resolve_filial_branch(pipe_label, pipe_option_id) is not None


def resolve_filial_branch(pipe_label: str, pipe_option_id: str) -> str | None:
    with db_conn() as conn:
        for chave in (pipe_label, pipe_option_id):
            chave = (chave or "").strip()
            if not chave:
                continue
            row = conn.execute(
                "SELECT branch_id FROM pipedrive_filial WHERE pipe_key = %s",
                (chave,),
            ).fetchone()
            if row:
                return str(row["branch_id"])
    return None


def upsert_filial_branch(pipe_key: str, branch_id: str) -> None:
    pipe_key = pipe_key.strip()
    if not pipe_key:
        return
    with db_conn() as conn:
        conn.execute(
            """
            INSERT INTO pipedrive_filial (pipe_key, branch_id) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE branch_id = VALUES(branch_id)
            """,
            (pipe_key, str(branch_id)),
        )


def upsert_branch_config(
    branch_id: str,
    *,
    label: str,
    subcentro_custo_id: str,
    parametro_recorrente: str,
    parametro_implantacao: str,
    pedido_serie: str | None = None,
    pedido_modelo_id: str | None = None,
) -> None:
    serie = str(pedido_serie if pedido_serie is not None else PLUNE_PEDIDO_SERIE)
    modelo = str(
        pedido_modelo_id if pedido_modelo_id is not None else PLUNE_PEDIDO_MODELO_ID
    )
    with db_conn() as conn:
        conn.execute(
            """
            INSERT INTO branch_config (
                branch_id, label, subcentro_custo_id,
                parametro_contabil_recorrente, parametro_contabil_implantacao,
                pedido_serie, pedido_modelo_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                label = VALUES(label),
                subcentro_custo_id = VALUES(subcentro_custo_id),
                parametro_contabil_recorrente = VALUES(parametro_contabil_recorrente),
                parametro_contabil_implantacao = VALUES(parametro_contabil_implantacao),
                pedido_serie = VALUES(pedido_serie),
                pedido_modelo_id = VALUES(pedido_modelo_id)
            """,
            (
                str(branch_id),
                label,
                subcentro_custo_id,
                parametro_recorrente,
                parametro_implantacao,
                serie,
                modelo,
            ),
        )


# --- Deals processados ---


def carregar_deals_processados() -> tuple[set[str], set[str]]:
    with db_conn() as conn:
        eventos = {
            f"{r['deal_id']}|{r['won_time']}"
            for r in conn.execute(
                "SELECT deal_id, won_time FROM deals_processed"
            ).fetchall()
        }
        legado = {
            r["deal_id"]
            for r in conn.execute("SELECT deal_id FROM deals_legacy_block").fetchall()
        }
    return eventos, legado


def salvar_deal_processado(
    deal_id: str, won_time_str: str, *, conn: DbConnection | None = None
) -> None:
    deal_id = str(deal_id)
    won_raw = str(won_time_str).strip()

    def _write(c: DbConnection) -> None:
        c.execute(
            """
            INSERT IGNORE INTO deals_processed (deal_id, won_time, processed_at)
            VALUES (%s, %s, %s)
            """,
            (deal_id, won_raw, _utc_now()),
        )

    if conn is not None:
        _write(conn)
    else:
        with db_conn() as c:
            _write(c)


# --- Pedidos Plune (chave PedidoIntegracao) ---


def carregar_pedidos_plune_criados() -> set[str]:
    with db_conn() as conn:
        return {
            r["pedido_key"]
            for r in conn.execute("SELECT pedido_key FROM pedidos_plune_keys").fetchall()
        }


def salvar_pedido_plune_key(
    pedido_key: str, *, conn: DbConnection | None = None
) -> None:
    pedido_key = str(pedido_key).strip()
    if not pedido_key:
        return

    def _write(c: DbConnection) -> None:
        c.execute(
            """
            INSERT IGNORE INTO pedidos_plune_keys (pedido_key, created_at)
            VALUES (%s, %s)
            """,
            (pedido_key, _utc_now()),
        )

    if conn is not None:
        _write(conn)
    else:
        with db_conn() as c:
            _write(c)


# --- Envelopes pendentes ---


def _load_envelopes(conn: DbConnection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT deal_id, envelope_id, envelope_name, created_at,
               pedidos_plune_criados, pedidos_plune_aprovados, pedido_plune_id
        FROM envelopes_pending
        ORDER BY created_at
        """
    ).fetchall()
    return [
        {
            "deal_id": r["deal_id"],
            "envelope_id": r["envelope_id"],
            "envelope_name": r["envelope_name"],
            "created_at": r["created_at"],
            "pedido_plune_criado": bool(r["pedidos_plune_criados"]),
            "pedidos_plune_criados": bool(r["pedidos_plune_criados"]),
            "pedidos_plune_aprovados": bool(r["pedidos_plune_aprovados"]),
            "pedido_plune_aprovado": bool(r["pedidos_plune_aprovados"]),
            "pedido_plune_id": r["pedido_plune_id"],
        }
        for r in rows
    ]


def salvar_envelope_pendente(deal_id: str, envelope_id: str, envelope_name: str) -> None:
    deal_id = str(deal_id)
    with db_conn() as conn:
        conn.execute(
            """
            REPLACE INTO envelopes_pending (
                deal_id, envelope_id, envelope_name, created_at,
                pedidos_plune_criados, pedidos_plune_aprovados, pedido_plune_id
            ) VALUES (%s, %s, %s, %s, 0, 0, NULL)
            """,
            (deal_id, envelope_id, envelope_name, _utc_now()),
        )


def buscar_por_envelope_id(envelope_id: str) -> dict | None:
    with db_conn() as conn:
        row = conn.execute(
            "SELECT deal_id FROM envelopes_pending WHERE envelope_id = %s",
            (envelope_id,),
        ).fetchone()
        if not row:
            return None
        for rec in _load_envelopes(conn):
            if rec.get("envelope_id") == envelope_id:
                return rec
    return None


def buscar_por_deal_id(deal_id: str) -> dict | None:
    deal_id = str(deal_id)
    with db_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM envelopes_pending WHERE deal_id = %s", (deal_id,)
        ).fetchone()
        if not row:
            return None
        for rec in _load_envelopes(conn):
            if str(rec.get("deal_id")) == deal_id:
                return rec
    return None


def marcar_pedido_criado(deal_id: str, pedido_id: str | None = None) -> None:
    deal_id = str(deal_id)
    with db_conn() as conn:
        conn.execute(
            """
            UPDATE envelopes_pending
            SET pedidos_plune_criados = 1,
                pedido_plune_id = COALESCE(%s, pedido_plune_id)
            WHERE deal_id = %s
            """,
            (str(pedido_id) if pedido_id is not None else None, deal_id),
        )


def marcar_pedidos_aprovados(deal_id: str) -> None:
    deal_id = str(deal_id)
    with db_conn() as conn:
        conn.execute(
            """
            UPDATE envelopes_pending
            SET pedidos_plune_aprovados = 1
            WHERE deal_id = %s
            """,
            (deal_id,),
        )


def listar_aguardando_pedido_plune() -> list[dict]:
    with db_conn() as conn:
        return [
            r
            for r in _load_envelopes(conn)
            if not r.get("pedidos_plune_aprovados")
            and not r.get("pedido_plune_aprovado")
        ]


# --- Catálogo subcentros ---


def upsert_subcentro(
    branch_id: str,
    level: int,
    pipe_label: str,
    plune_id: str,
    plune_label: str = "",
    *,
    conn: DbConnection | None = None,
) -> None:
    pipe_label = pipe_label.strip()
    if not pipe_label or not plune_id:
        return

    sql = """
        INSERT INTO plune_subcentro (
            branch_id, `level`, pipe_label, plune_id, plune_label, uso_count, updated_at
        ) VALUES (%s, %s, %s, %s, %s, 1, %s)
        ON DUPLICATE KEY UPDATE
            plune_id = VALUES(plune_id),
            plune_label = COALESCE(NULLIF(VALUES(plune_label), ''), plune_label),
            uso_count = uso_count + 1,
            updated_at = VALUES(updated_at)
    """
    args = (str(branch_id), level, pipe_label, str(plune_id), plune_label, _utc_now())

    if conn is not None:
        conn.execute(sql, args)
    else:
        with db_conn() as c:
            c.execute(sql, args)


def maps_por_branch(branch_id: str) -> dict:
    """Retorna regional_map e subcentro3_map no formato esperado por settings_por_branch."""
    branch_id = str(branch_id)
    regional: dict[str, str] = {}
    subcentro3: dict[str, str] = {}
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT `level`, pipe_label, plune_id
            FROM plune_subcentro
            WHERE branch_id = %s
            ORDER BY `level`, pipe_label
            """,
            (branch_id,),
        ).fetchall()
    for row in rows:
        if row["level"] == 2:
            regional[row["pipe_label"]] = str(row["plune_id"])
        elif row["level"] == 3:
            subcentro3[row["pipe_label"]] = str(row["plune_id"])
    return {"regional_map": regional, "subcentro3_map": subcentro3}


def branch_config(branch_id: str) -> dict | None:
    branch_id = str(branch_id)
    with db_conn() as conn:
        row = conn.execute(
            "SELECT * FROM branch_config WHERE branch_id = %s", (branch_id,)
        ).fetchone()
    if not row:
        return None
    maps = maps_por_branch(branch_id)
    serie = row.get("pedido_serie") or PLUNE_PEDIDO_SERIE
    modelo = row.get("pedido_modelo_id") or PLUNE_PEDIDO_MODELO_ID
    return {
        "subcentro_custo_id": row["subcentro_custo_id"],
        "parametro_recorrente": row["parametro_contabil_recorrente"],
        "parametro_implantacao": row["parametro_contabil_implantacao"],
        "pedido_serie": str(serie),
        "pedido_modelo_id": str(modelo),
        "regional_map": maps["regional_map"],
        "subcentro3_map": maps["subcentro3_map"],
    }


def resumo_estado_banco() -> dict:
    """Contagens das tabelas principais (para scripts e diagnóstico)."""
    with db_conn() as conn:
        def _count(table: str) -> int:
            return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]

        return {
            "deals_processados": _count("deals_processed"),
            "deals_legado": _count("deals_legacy_block"),
            "pedidos_plune": _count("pedidos_plune_keys"),
            "envelopes": _count("envelopes_pending"),
            "pipedrive_filial": _count("pipedrive_filial"),
            "branch_config": _count("branch_config"),
            "plune_subcentro": _count("plune_subcentro"),
            "default_branch_id": default_branch_id(),
        }


# --- Manutenção estado (CLI / ops) ---

_TABELAS_ESTADO = (
    "deals_processed",
    "deals_legacy_block",
    "pedidos_plune_keys",
    "envelopes_pending",
)


def detalhe_estado_deal(deal_id: str) -> dict:
    """Linhas de estado vinculadas a um deal_id (para diagnóstico)."""
    deal_id = str(deal_id).strip()
    with db_conn() as conn:
        return {
            "deal_id": deal_id,
            "deals_processed": conn.execute(
                "SELECT * FROM deals_processed WHERE deal_id = %s ORDER BY won_time",
                (deal_id,),
            ).fetchall(),
            "deals_legacy_block": conn.execute(
                "SELECT * FROM deals_legacy_block WHERE deal_id = %s",
                (deal_id,),
            ).fetchall(),
            "envelopes_pending": conn.execute(
                "SELECT * FROM envelopes_pending WHERE deal_id = %s",
                (deal_id,),
            ).fetchall(),
            "pedidos_plune_keys": conn.execute(
                """
                SELECT * FROM pedidos_plune_keys
                WHERE pedido_key = %s OR pedido_key LIKE %s
                ORDER BY pedido_key
                """,
                (deal_id, f"{deal_id}-%"),
            ).fetchall(),
        }


def limpar_estado_deal(deal_id: str) -> dict[str, int]:
    """Remove estado da automação para um deal (permite reprocessar)."""
    deal_id = str(deal_id).strip()
    if not deal_id:
        return {}
    stats: dict[str, int] = {}
    with db_conn() as conn:
        cur = conn.execute(
            "DELETE FROM deals_processed WHERE deal_id = %s", (deal_id,)
        )
        stats["deals_processed"] = cur.rowcount
        cur = conn.execute(
            "DELETE FROM deals_legacy_block WHERE deal_id = %s", (deal_id,)
        )
        stats["deals_legacy_block"] = cur.rowcount
        cur = conn.execute(
            "DELETE FROM envelopes_pending WHERE deal_id = %s", (deal_id,)
        )
        stats["envelopes_pending"] = cur.rowcount
        cur = conn.execute(
            """
            DELETE FROM pedidos_plune_keys
            WHERE pedido_key = %s OR pedido_key LIKE %s
            """,
            (deal_id, f"{deal_id}-%"),
        )
        stats["pedidos_plune_keys"] = cur.rowcount
    return stats


def limpar_todo_estado() -> dict[str, int]:
    """Remove todo o estado da automação (não mexe em catálogo Plune/filiais)."""
    stats: dict[str, int] = {}
    with db_conn() as conn:
        for table in _TABELAS_ESTADO:
            cur = conn.execute(f"DELETE FROM {table}")
            stats[table] = cur.rowcount
    return stats


def sincronizar_banco_completo(
    *,
    sync_subcentros: bool = True,
    force_subcentros: bool = True,
) -> dict:
    """
    Rotina única de manutenção do MySQL:
    1. Garante seed de filiais/branch_config
    2. Sincroniza subcentros níveis 1–3 via API Plune
    """
    from .plune_catalog import garantir_catalogo_inicializado, sincronizar_subcentros_de_pedidos

    resultado: dict = {"subcentros": 0, "resumo": {}}

    with db_conn() as conn:
        _seed_catalogo_inicial(conn)

    garantir_catalogo_inicializado()
    if sync_subcentros:
        resultado["subcentros"] = sincronizar_subcentros_de_pedidos(force=force_subcentros)

    resultado["resumo"] = resumo_estado_banco()
    return resultado
