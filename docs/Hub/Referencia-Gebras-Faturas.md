# HUB — Referência Gebras-Faturas

Código legado do desktop **Sole-Hub** (`Gebras-Faturas`). A automação Python replica o **insert** de pedido, não substitui a UI.

## Arquivos principais

| Arquivo | Papel |
|---------|--------|
| `ModulosGerais/Business/geral/PedidoServices.cs` | `Salvar`, `Validar`, Browse Plune |
| `ERP/Programas/Gebras/Forms/Pedidos/Editor.cs` | UI criação/edição |
| `ERP/Programas/Gebras/Forms/Pedidos/uc_Instalacao.cs` | Serviços 1–6, preço |
| `ERP/Programas/Gebras/Forms/Pedidos/GerenciadorDePedidos.cs` | Listagem / abrir pedido |
| `ModulosGerais/DTO/50 - Pedidos/Pedido.cs` | Modelo |
| `ModulosGerais/DTO/50 - Pedidos/Situacao.cs` | Enum situação |

## Convenções

Ver [`Gebras-Faturas/docs/Convenções Projeto.md`](../../../Gebras-Faturas/docs/Convenções%20Projeto.md) — banco `gebras` no RDS (credenciais só no `.env`, não versionar senha).

## Diferenças automação vs desktop

| Aspecto | Desktop | AutomacaoGebras |
|---------|---------|-----------------|
| SQL | Concatenação em `Salvar` | Parameterized queries em `hub_pedido.py` |
| Usuário | `CodigoUsuarioLogado` | `HUB_CODIGO_USUARIO_SISTEMA` |
| Tickets Sole/GQE | SPs após salvar | Não chamadas (ainda) |
| Situação inicial | NOVO | `codigoSituacao=0` |
