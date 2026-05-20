"""
Diagnóstico Plune → MySQL (sem dados locais próprios).

Equivalente a:
  python scripts/atualizar_db.py
  python scripts/ver_catalogo_db.py
"""
import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.database import sincronizar_banco_completo


def _listar_catalogo() -> int:
    path = Path(__file__).resolve().parent / "ver_catalogo_db.py"
    spec = importlib.util.spec_from_file_location("ver_catalogo_db", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.main()


def main() -> int:
    print("[*] Sincronizando subcentros via API Plune → MySQL ...\n")
    r = sincronizar_banco_completo(sync_subcentros=True, force_subcentros=True)
    print(f"Upserts: {r.get('subcentros', 0)}\n")
    return _listar_catalogo()


if __name__ == "__main__":
    sys.exit(main())
