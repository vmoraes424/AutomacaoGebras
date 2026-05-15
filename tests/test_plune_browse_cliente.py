"""
Teste: buscar parceiro no Plune por CPF/CNPJ (UrlClientes.md).

  python tests/test_plune_browse_cliente.py 359.696.440-72
  python tests/test_plune_browse_cliente.py 52398605000186
"""

import sys

from core.plune_pedido import buscar_parceiro_plune_por_documento


def main():
    if len(sys.argv) < 2:
        print("Uso: python tests/test_plune_browse_cliente.py <documento> [razao_social_pipe]")
        sys.exit(1)

    documento = sys.argv[1]
    razao = sys.argv[2] if len(sys.argv) > 2 else ""

    parceiro = buscar_parceiro_plune_por_documento(documento, razao)
    if not parceiro:
        print("Nenhum parceiro encontrado no Plune para esse documento.")
        return

    print(f"ParceiroId={parceiro['id']}")
    print(f"Razão Social: {parceiro['razao_social']}")
    print(f"CNPJ/CPF: {parceiro.get('documento_formatado') or parceiro['documento']}")
    print(f"Endereço: {parceiro['endereco']}")
    print(f"Cidade: {parceiro['cidade']} / {parceiro['uf']}")


if __name__ == "__main__":
    main()
