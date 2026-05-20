# Campos Pipedrive (Deals) — hashes e nomes

Gerado em **19/05/2026 20:20** via `GET /api/v2/dealFields`. Total: **76** campos.

Fonte: API Pipedrive v2. Campos usados pela automação estão marcados na coluna *Uso no código*.

## Índice

- [Todos os campos](#todos-os-campos)
- [Somente custom fields](#somente-custom-fields)
- [Usados pela automação](#usados-pela-automação)

## Todos os campos

| Nome do campo | Hash (`field_code`) | Tipo | Custom | Uso no código |
|---|---|---|---|---|
| CEP | `6d3373f7ee86c7d2449824136baf3ee1938a8ef1` | varchar | Sim |  |
| CPF/CNPJ | `176d2a0d5167d1edc9b949c75f8b9a7597eabe91` | varchar | Sim | FIELD_DOCUMENTO |
| Código Cliente | `41a3157128d51e2fc803eeec4b242efafcb55b4e` | varchar | Sim | FIELD_NUMERO_CONTRATO_P2 |
| Código da Instalação | `14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b` | varchar | Sim | FIELD_NUMERO_CONTRATO_P1 |
| Dados da Contratante | `28d491e0263008b437e28fc55bbad8302c4646c8` | text | Sim | FIELD_NOME_CLIENTE |
| Data de Implantação | `f40caca58878f19aefba960b87127753b7b932ca` | varchar | Sim |  |
| Data de Pagamento da Implantação | `2b8f62a107891e26390459cfa4048b3eedade11b` | date | Sim | FIELD_DATA_IMPLANTACAO |
| Data de Pagamento da Primeira Cobrança Mensal | `f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2` | date | Sim | FIELD_DATA_PRIMEIRA_COBRANCA |
| E-mail Assinante do Contrato | `a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6` | varchar | Sim | SIGNER: Contato Principal |
| E-mail Coordenador | `92359b129485b08fd024b8c28ef022e7635419a3` | varchar | Sim | SIGNER: Coordenador Principal |
| E-mail Diretor | `35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2` | varchar | Sim | SIGNER: Diretor Principal |
| E-mail Gestor Contratante | `3002b2df87f0577585ebaec394fd09a38ca8778f` | varchar | Sim | FIELD_CONTATO_CONTRATANTE |
| E-mail Gestor GEBRAS | `ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b` | varchar | Sim | FIELD_CONTATO_GESTOR / SIGNER: Gestor Gebras |
| Email Financeiro Contratante | `722da69afe31c1f8fa4f5457a223e2a952ae0978` | varchar | Sim | FIELD_CONTATO_FINANCEIRO |
| Endereço | `81566ac6e038bb0ba3adfa122c798b3e497b7538` | address | Sim | FIELD_ENDERECO |
| Filial | `be20f11317ac66845bf97695f43e57795e26d01d` | enum | Sim | FIELD_FILIAL -> BranchId Plune |
| Gestão ACL - Mercado Livre de Energia | `8f998d4877d478b3905c126d8b23f205d0686b77` | double | Sim |  |
| Gestão da Qualidade de Energia | `ffb2d5aec9acdee5a242ca19683bbf4caa24cd53` | double | Sim | FIELD_INDICADORES_QUALIDADE |
| Gestão Usina Fotovoltaica | `1ba1794470354856aaca3e784349cd5f9f4d074e` | double | Sim |  |
| Inscrição Estadual | `c3e623cfa197040b778400a8977ae2c8a8386024` | varchar | Sim |  |
| Município/Estado | `2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5` | address | Sim | FIELD_CIDADE |
| Observações (Detalhes) | `4fba2f9323c64acdcac770e38f2c0cdb840796bc` | varchar | Sim |  |
| Porcentagem de Exito | `225005fe8384d97183e5480781ea8ea82982301e` | enum | Sim |  |
| Quantidade de UC's | `c6d1c300a1d070c1a54494a246f6330beabe36aa` | varchar | Sim |  |
| Sole Consultoria | `c0a23912d889e00f51ed5bd08a55856a7e5dc930` | double | Sim | FIELD_QUALIDADE_ENERGIA |
| SOLE Web | `f9923cdce1274da8c10cec1b9ab561e024504620` | double | Sim | FIELD_QTD_SOLE |
| Sub Centro Nível 2 | `3b5fc4072a4bff3e5e24dce974d20e15c6ebaed6` | varchar | Sim | FIELD_REGIONAL (Sub Centro Nível 2) |
| Sub Centro Nível 3 | `4f6e152a7d4f89dbd6664ef97980531394721599` | varchar | Sim | FIELD_SUBCENTRO_NIVEL_3 -> SubCentroCusto3Id |
| Valor de Implantação | `015407d5106c321a227f1ca881f920fe2e1042ec` | monetary | Sim | FIELD_VALOR_IMPLANTACAO |
| Valor Recorrência | `2a331c4b62c9d46aae9451af25eca2d08a3fdf0a` | monetary | Sim | FIELD_VALOR_MENSAL |
| Atividades concluídas | `done_activities_count` | int | Não |  |
| Atividades para fazer | `undone_activities_count` | int | Não |  |
| Atualizado em | `update_time` | date | Não |  |
| Canal de origem | `channel` | enum | Não |  |
| Criado por | `creator_user_id` | user | Não |  |
| Data de fechamento esperada | `expected_close_date` | date | Não |  |
| Data de perda | `lost_time` | date | Não |  |
| Data e hora local de fechamento | `local_close_date` | date | Não |  |
| Data e hora local em que foi ganho | `local_won_date` | date | Não |  |
| Data e hora local em que foi perdido | `local_lost_date` | date | Não |  |
| E-mail Cco inteligente | `smart_bcc_email` | varchar | Não |  |
| Etapa | `stage_id` | stage | Não |  |
| Etiqueta | `label_ids` | set | Não |  |
| Funil | `pipeline_id` | double | Não |  |
| Ganho em | `won_time` | date | Não |  |
| Horário do arquivamento | `archive_time` | date | Não |  |
| ID | `id` | int | Não |  |
| ID de origem | `origin_id` | varchar | Não |  |
| ID do canal de origem | `channel_id` | varchar | Não |  |
| Last activity | `last_activity_id` | activity | Não |  |
| Motivo da perda | `lost_reason` | varchar_options | Não |  |
| Negócio criado em | `add_time` | date | Não |  |
| Negócio fechado em | `close_time` | date | Não |  |
| Next activity | `next_activity_id` | activity | Não |  |
| Número de anotações | `notes_count` | int | Não |  |
| Número de arquivos | `files_count` | int | Não |  |
| Número de mensagens de e-mail | `email_messages_count` | int | Não |  |
| Número de participantes | `participants_count` | int | Não |  |
| Número de produtos | `products_count` | int | Não |  |
| Número de seguidores | `followers_count` | int | Não |  |
| Organização | `org_id` | org | Não |  |
| Origem | `origin` | enum | Não |  |
| Pessoa de contato | `person_id` | people | Não |  |
| Primeira vez em que foi ganho | `first_won_time` | date | Não |  |
| Probabilidade | `probability` | int | Não |  |
| Proprietário | `owner_id` | user | Não |  |
| Status | `status` | status | Não |  |
| Status de arquivamento | `is_archived` | boolean | Não |  |
| Total de atividades | `activities_count` | int | Não |  |
| Título | `title` | varchar | Não |  |
| Valor | `value` | monetary | Não |  |
| Visível para | `visible_to` | visible_to | Não |  |
| É excluído | `is_deleted` | boolean | Não |  |
| Última alteração de etapa | `stage_change_time` | date | Não |  |
| Último e-mail enviado | `last_outgoing_mail_time` | date | Não |  |
| Último e-mail recebido | `last_incoming_mail_time` | date | Não |  |

## Somente custom fields

Total: **30** campos customizados.

| Nome do campo | Hash (`field_code`) | Tipo | Uso no código |
|---|---|---|---|
| CEP | `6d3373f7ee86c7d2449824136baf3ee1938a8ef1` | varchar |  |
| CPF/CNPJ | `176d2a0d5167d1edc9b949c75f8b9a7597eabe91` | varchar | FIELD_DOCUMENTO |
| Código Cliente | `41a3157128d51e2fc803eeec4b242efafcb55b4e` | varchar | FIELD_NUMERO_CONTRATO_P2 |
| Código da Instalação | `14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b` | varchar | FIELD_NUMERO_CONTRATO_P1 |
| Dados da Contratante | `28d491e0263008b437e28fc55bbad8302c4646c8` | text | FIELD_NOME_CLIENTE |
| Data de Implantação | `f40caca58878f19aefba960b87127753b7b932ca` | varchar |  |
| Data de Pagamento da Implantação | `2b8f62a107891e26390459cfa4048b3eedade11b` | date | FIELD_DATA_IMPLANTACAO |
| Data de Pagamento da Primeira Cobrança Mensal | `f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2` | date | FIELD_DATA_PRIMEIRA_COBRANCA |
| E-mail Assinante do Contrato | `a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6` | varchar | SIGNER: Contato Principal |
| E-mail Coordenador | `92359b129485b08fd024b8c28ef022e7635419a3` | varchar | SIGNER: Coordenador Principal |
| E-mail Diretor | `35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2` | varchar | SIGNER: Diretor Principal |
| E-mail Gestor Contratante | `3002b2df87f0577585ebaec394fd09a38ca8778f` | varchar | FIELD_CONTATO_CONTRATANTE |
| E-mail Gestor GEBRAS | `ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b` | varchar | FIELD_CONTATO_GESTOR / SIGNER: Gestor Gebras |
| Email Financeiro Contratante | `722da69afe31c1f8fa4f5457a223e2a952ae0978` | varchar | FIELD_CONTATO_FINANCEIRO |
| Endereço | `81566ac6e038bb0ba3adfa122c798b3e497b7538` | address | FIELD_ENDERECO |
| Filial | `be20f11317ac66845bf97695f43e57795e26d01d` | enum | FIELD_FILIAL -> BranchId Plune |
| Gestão ACL - Mercado Livre de Energia | `8f998d4877d478b3905c126d8b23f205d0686b77` | double |  |
| Gestão da Qualidade de Energia | `ffb2d5aec9acdee5a242ca19683bbf4caa24cd53` | double | FIELD_INDICADORES_QUALIDADE |
| Gestão Usina Fotovoltaica | `1ba1794470354856aaca3e784349cd5f9f4d074e` | double |  |
| Inscrição Estadual | `c3e623cfa197040b778400a8977ae2c8a8386024` | varchar |  |
| Município/Estado | `2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5` | address | FIELD_CIDADE |
| Observações (Detalhes) | `4fba2f9323c64acdcac770e38f2c0cdb840796bc` | varchar |  |
| Porcentagem de Exito | `225005fe8384d97183e5480781ea8ea82982301e` | enum |  |
| Quantidade de UC's | `c6d1c300a1d070c1a54494a246f6330beabe36aa` | varchar |  |
| Sole Consultoria | `c0a23912d889e00f51ed5bd08a55856a7e5dc930` | double | FIELD_QUALIDADE_ENERGIA |
| SOLE Web | `f9923cdce1274da8c10cec1b9ab561e024504620` | double | FIELD_QTD_SOLE |
| Sub Centro Nível 2 | `3b5fc4072a4bff3e5e24dce974d20e15c6ebaed6` | varchar | FIELD_REGIONAL (Sub Centro Nível 2) |
| Sub Centro Nível 3 | `4f6e152a7d4f89dbd6664ef97980531394721599` | varchar | FIELD_SUBCENTRO_NIVEL_3 -> SubCentroCusto3Id |
| Valor de Implantação | `015407d5106c321a227f1ca881f920fe2e1042ec` | monetary | FIELD_VALOR_IMPLANTACAO |
| Valor Recorrência | `2a331c4b62c9d46aae9451af25eca2d08a3fdf0a` | monetary | FIELD_VALOR_MENSAL |

## Usados pela automação

Definidos em `core/pipedrive_fields.py`.

| Nome no Pipedrive | Hash | Constante / papel |
|---|---|---|
| CPF/CNPJ | `176d2a0d5167d1edc9b949c75f8b9a7597eabe91` | FIELD_DOCUMENTO |
| Código Cliente | `41a3157128d51e2fc803eeec4b242efafcb55b4e` | FIELD_NUMERO_CONTRATO_P2 |
| Código da Instalação | `14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b` | FIELD_NUMERO_CONTRATO_P1 |
| Dados da Contratante | `28d491e0263008b437e28fc55bbad8302c4646c8` | FIELD_NOME_CLIENTE |
| Data de Pagamento da Implantação | `2b8f62a107891e26390459cfa4048b3eedade11b` | FIELD_DATA_IMPLANTACAO |
| Data de Pagamento da Primeira Cobrança Mensal | `f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2` | FIELD_DATA_PRIMEIRA_COBRANCA |
| E-mail Assinante do Contrato | `a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6` | SIGNER: Contato Principal |
| E-mail Coordenador | `92359b129485b08fd024b8c28ef022e7635419a3` | SIGNER: Coordenador Principal |
| E-mail Diretor | `35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2` | SIGNER: Diretor Principal |
| E-mail Gestor Contratante | `3002b2df87f0577585ebaec394fd09a38ca8778f` | FIELD_CONTATO_CONTRATANTE |
| E-mail Gestor GEBRAS | `ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b` | FIELD_CONTATO_GESTOR / SIGNER: Gestor Gebras |
| Email Financeiro Contratante | `722da69afe31c1f8fa4f5457a223e2a952ae0978` | FIELD_CONTATO_FINANCEIRO |
| Endereço | `81566ac6e038bb0ba3adfa122c798b3e497b7538` | FIELD_ENDERECO |
| Filial | `be20f11317ac66845bf97695f43e57795e26d01d` | FIELD_FILIAL -> BranchId Plune |
| Gestão da Qualidade de Energia | `ffb2d5aec9acdee5a242ca19683bbf4caa24cd53` | FIELD_INDICADORES_QUALIDADE |
| Município/Estado | `2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5` | FIELD_CIDADE |
| Sole Consultoria | `c0a23912d889e00f51ed5bd08a55856a7e5dc930` | FIELD_QUALIDADE_ENERGIA |
| SOLE Web | `f9923cdce1274da8c10cec1b9ab561e024504620` | FIELD_QTD_SOLE |
| Sub Centro Nível 2 | `3b5fc4072a4bff3e5e24dce974d20e15c6ebaed6` | FIELD_REGIONAL (Sub Centro Nível 2) |
| Sub Centro Nível 3 | `4f6e152a7d4f89dbd6664ef97980531394721599` | FIELD_SUBCENTRO_NIVEL_3 -> SubCentroCusto3Id |
| Valor de Implantação | `015407d5106c321a227f1ca881f920fe2e1042ec` | FIELD_VALOR_IMPLANTACAO |
| Valor Recorrência | `2a331c4b62c9d46aae9451af25eca2d08a3fdf0a` | FIELD_VALOR_MENSAL |
