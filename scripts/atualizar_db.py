"""
Atualiza catálogo no MySQL (atalho para `automacao_db sync`).

Uso:
  python scripts/atualizar_db.py
  python scripts/atualizar_db.py --sem-plune
"""
import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.config import MYSQL_DATABASE, MYSQL_HOST, MYSQL_PORT
from core.database import resumo_estado_banco, sincronizar_banco_completo


def main() -> int:
    parser = argparse.ArgumentParser(description="Atualiza MySQL gebras_automacao")
    parser.add_argument(
        "--sem-plune",
        action="store_true",
        help="Não chama API Plune para subcentros",
    )
    args = parser.parse_args()

    print(f"MySQL: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}\n")
    resultado = sincronizar_banco_completo(
        sync_subcentros=not args.sem_plune,
        force_subcentros=True,
    )

    if not args.sem_plune:
        print(f"Subcentros Plune: {resultado.get('subcentros', 0)} upserts")

    print("\nResumo do banco:")
    for chave, valor in (resultado.get("resumo") or resumo_estado_banco()).items():
        print(f"  {chave}: {valor}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
