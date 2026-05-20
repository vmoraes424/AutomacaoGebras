"""Gera docs/Plune/Plune-campos-fieldid.md a partir dos exports de colunas e uso no código."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "docs" / "Plune" / "Plune-campos-fieldid.md"

SOURCES = [
    {
        "class_id": "Venda.Pedido",
        "titulo": "Pedido (`Venda.Pedido`)",
        "path": ROOT / "docs" / "Plune" / "Pedidos" / "Pedido-colunas.md",
        "doc_ref": "docs/Plune/Pedidos/Pedido-colunas.md",
    },
    {
        "class_id": "Parceiro.tbParceiro",
        "titulo": "Parceiro / Cliente (`Parceiro.tbParceiro`)",
        "path": ROOT / "docs" / "Plune" / "Clientes" / "Clientes-colunas.md",
        "doc_ref": "docs/Plune/Clientes/Clientes-colunas.md",
    },
]

# Campos referenciados em core/plune_pedido.py (e testes relacionados)
AUTOMACAO: dict[str, dict[str, str]] = {
    "Venda.Pedido": {
        "CompanyId": "Insert base / defaults",
        "Aprovado": "Insert + aprovação pós-insert",
        "Status": "Insert base",
        "StatusPedido": "Insert (implantação vs recorrente)",
        "ModeloId": "Insert base",
        "NaturezaOperacaoServicoId": "Insert base",
        "Serie": "Insert base",
        "TipoContratoId": "Insert base",
        "CentroCustoId": "Insert base",
        "SubCentroCustoId": "Insert (env PLUNE_SUBCENTRO_CUSTO_ID)",
        "SubCentroCusto2Id": "Insert (Sub Centro Nível 2 Pipedrive)",
        "SubCentroCusto3Id": "Insert (Sub Centro Nível 3 Pipedrive)",
        "ParcelamentoAutomatico": "Insert base",
        "ComissaoManual": "Insert base",
        "PercentualComissao": "Insert (UCs Pipedrive / implantação)",
        "BranchId": "Defaults",
        "TipoOpId": "Defaults",
        "FreteporConta": "Defaults",
        "ClienteId": "Insert (parceiro resolvido)",
        "Descricao": "Insert",
        "PedidoIntegracao": "Insert + idempotência Browse",
        "DataEntrega": "Insert",
        "ParametroContabilId": "Insert (implantação vs recorrente)",
        "BaseComissao": "Insert",
        "ClienteNome": "Insert (cadastro Plune)",
        "ClienteNumero": "Insert",
        "ClienteEndereco": "Insert",
        "ClienteBairro": "Insert",
        "ClienteCityName": "Insert",
        "ClienteStateId": "Insert",
        "ClienteCep": "Insert",
        "x1_PrevisaoCobranca": "Insert (datas Pipedrive)",
        "Observacao": "Insert",
        "ObservacaoNF": "Insert",
        "x1_ObservacaoAnexo": "Insert",
        "Id": "Browse / aprovação",
    },
    "Venda.PedidoItem": {
        "CompanyId": "Insert item (slave)",
        "BranchId": "Insert item",
        "ProdutoId": "Insert item (PLUNE_PRODUTO_SOLE_ID)",
        "Quantidade": "Insert item",
        "Preco": "Insert item (valor deal)",
        "ClienteId": "Insert item",
    },
    "Parceiro.tbParceiro": {
        "EmpresaId": "Insert / Select / Browse filtro",
        "ParceiroId": "Browse / Select",
        "Ativo": "Browse filtro",
        "NumeroContribuinte": "Browse filtro + Insert",
        "NomRazaoSocial": "Browse + Insert",
        "NomFantasia": "Browse + Insert",
        "ECliente": "Browse filtro + Insert",
        "EFornecedor": "Browse filtro + Insert",
        "EnderecoPrincipal": "Browse + Insert",
        "BairroPrincipal": "Browse",
        "CidadePrincipalId": "Browse",
        "CidadePrincipalEx": "Browse + Insert",
        "UFPrincipalId": "Browse",
        "CEPPrincipal": "Browse + Insert (Pipedrive FIELD_CEP, obrigatório)",
        "ContatoNome": "Browse + Insert (Pipedrive)",
        "EMail": "Browse",
        "EmProspeccao": "Insert",
        "EmAprovacao": "Insert",
        "ERepresentante": "Insert",
        "Transportadora": "Insert",
        "RecebeEmala": "Insert",
        "RecebeMalaCorreio": "Insert",
        "AcessoWeb": "Insert",
        "NumeroFiliais": "Insert",
        "VerificacaoFilial": "Insert",
        "ConsumidorFinal": "Insert",
        "ISSQNSubstituicaoTributaria": "Insert",
        "RegimeTributario": "Insert",
        "Obs": "Insert",
    },
}

TABLE_ROW_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*(\*|—|-)\s*\|\s*(.+?)\s*\|\s*Ver\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*`([^`]+)`\s*\|$"
)


def parse_colunas_md(path: Path) -> list[dict]:
    rows: list[dict] = []
    section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        match = TABLE_ROW_RE.match(line.strip())
        if not match:
            continue
        campo, nn, descricao, inc, alt, tipo = match.groups()
        rows.append(
            {
                "campo": campo.strip(),
                "nn": nn.strip() == "*",
                "descricao": descricao.strip().replace("\\|", "|"),
                "inc": inc.strip(),
                "alt": alt.strip(),
                "tipo": tipo.strip(),
                "secao": section,
            }
        )
    return rows


def esc_md(text: str) -> str:
    return (text or "").replace("|", "\\|")


def build_section(class_id: str, titulo: str, doc_ref: str, fields: list[dict]) -> list[str]:
    uso_map = AUTOMACAO.get(class_id, {})
    lines = [
        f"## {titulo}",
        "",
        f"**ClassId:** `{class_id}` · **Fonte:** [{doc_ref}]({doc_ref}) · **Campos:** {len(fields)}",
        "",
        "| Descrição (Plune) | Campo | FieldId API | Tipo | NN | Uso automação |",
        "|---|---|---|:---:|:---:|---|",
    ]
    for field in sorted(fields, key=lambda f: f["campo"].lower()):
        campo = field["campo"]
        field_id = f"{class_id}.{campo}"
        nn = "Sim" if field["nn"] else "Não"
        uso = uso_map.get(campo, "")
        lines.append(
            f"| {esc_md(field['descricao'])} | `{campo}` | `{field_id}` | "
            f"{esc_md(field['tipo'])} | {nn} | {uso} |"
        )
    return lines


def build_pedido_item_section() -> list[str]:
    class_id = "Venda.PedidoItem"
    uso_map = AUTOMACAO[class_id]
    lines = [
        f"## Pedido — Itens (`{class_id}`)",
        "",
        "Tabela embutida no Insert do pedido. Não há export de colunas no repositório; "
        "lista abaixo = campos usados pela automação em `core/plune_pedido.py`.",
        "",
        "| Campo | FieldId API | Uso automação |",
        "|---|---|---|",
    ]
    for campo, uso in sorted(uso_map.items(), key=lambda x: x[0].lower()):
        lines.append(f"| `{campo}` | `{class_id}.{campo}` | {uso} |")
    return lines


def build_automacao_resumo() -> list[str]:
    lines = [
        "## Usados pela automação (resumo)",
        "",
        "Referência rápida dos FieldIds enviados pelo fluxo Pipedrive → Plune.",
        "",
    ]
    for class_id, uso_map in AUTOMACAO.items():
        lines.append(f"### `{class_id}`")
        lines.append("")
        lines.append("| Campo | FieldId API | Papel |")
        lines.append("|---|---|---|")
        for campo, papel in sorted(uso_map.items(), key=lambda x: x[0].lower()):
            lines.append(f"| `{campo}` | `{class_id}.{campo}` | {papel} |")
        lines.append("")
    return lines


def main() -> None:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    all_sections: list[str] = [
        "# Campos Plune — FieldId e nomes",
        "",
        f"Gerado em **{now}** a partir dos exports de colunas do Plune no repositório.",
        "",
        "No Plune, o identificador de campo na API é o **FieldId** no formato "
        "`Schema.Tabela.Campo` (ex.: `Venda.Pedido.ClienteId`). "
        "Não há hashes de 40 caracteres como no Pipedrive.",
        "",
        "## Índice",
        "",
    ]

    parsed: list[tuple[dict, list[dict]]] = []
    for source in SOURCES:
        fields = parse_colunas_md(source["path"])
        parsed.append((source, fields))
        anchor = source["class_id"].lower().replace(".", "")
        all_sections.append(f"- [{source['titulo']}](#{anchor})")

    all_sections.append("- [Pedido — Itens (`Venda.PedidoItem`)](#vendapedidoitem)")
    all_sections.append("- [Usados pela automação (resumo)](#usados-pela-automação-resumo)")
    all_sections.append("")

    total = sum(len(f) for _, f in parsed)
    all_sections.append(
        f"**Total catalogado:** {total} campos em pedido e parceiro, "
        f"+ {len(AUTOMACAO['Venda.PedidoItem'])} campos de item usados na automação."
    )
    all_sections.append("")

    for source, fields in parsed:
        all_sections.extend(
            build_section(
                source["class_id"],
                source["titulo"],
                source["doc_ref"],
                fields,
            )
        )
        all_sections.append("")

    all_sections.extend(build_pedido_item_section())
    all_sections.append("")
    all_sections.extend(build_automacao_resumo())

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(all_sections).rstrip() + "\n", encoding="utf-8")
    print(f"Escrito: {OUT_PATH} ({total} campos de tabela + item)")


if __name__ == "__main__":
    main()
