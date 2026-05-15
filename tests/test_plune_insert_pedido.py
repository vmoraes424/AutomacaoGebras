"""
Teste: criar pedido Plune a partir de um deal_id Pipedrive.

  python tests/test_plune_insert_pedido.py <deal_id>
"""

import sys

from core.plune_pedido import PluneError, criar_pedido_plune


def main():
    if len(sys.argv) < 2:
        print("Uso: python tests/test_plune_insert_pedido.py <deal_id>")
        sys.exit(1)
    try:
        print(criar_pedido_plune(sys.argv[1]))
    except PluneError as exc:
        print(f"Erro: {exc}")
        sys.exit(2)


if __name__ == "__main__":
    main()
