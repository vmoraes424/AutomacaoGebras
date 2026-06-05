# Campos Pipedrive (Deals) — hashes e nomes

Gerado em **05/06/2026 10:35** via `GET /api/v2/dealFields`. Total: **76** campos.

Fonte: API Pipedrive v2. Campos usados pela automação estão marcados na coluna *Uso no código*.

## Índice

- [Todos os campos](#todos-os-campos)
- [Somente custom fields](#somente-custom-fields)
- [Usados pela automação](#usados-pela-automação)

## Todos os campos

| Nome do campo | Hash (`field_code`) | Tipo | Custom | Uso no código |
|---|---|---|---|---|
| CEP | `6d3373f7ee86c7d2449824136baf3ee1938a8ef1` | varchar | Sim | FIELD_CEP -> CEPPrincipal / ClienteCep |
| Consultor | `60ffe8e9c2aa51f717865559e86e6044bfb335e6` | enum | Sim | FIELD_SUBCENTRO_NIVEL_3 (Consultor / SubCentroCusto3Id) |
| Contratante | `28d491e0263008b437e28fc55bbad8302c4646c8` | text | Sim | FIELD_NOME_CLIENTE |
| CPF/CNPJ | `176d2a0d5167d1edc9b949c75f8b9a7597eabe91` | varchar | Sim | FIELD_DOCUMENTO |
| Código Cliente/Código da Instalação | `41a3157128d51e2fc803eeec4b242efafcb55b4e` | varchar | Sim | FIELD_CODIGO_CLIENTE_INSTALACAO |
| Data de Pagamento da Implantação | `2b8f62a107891e26390459cfa4048b3eedade11b` | date | Sim | FIELD_DATA_PAGAMENTO_IMPLANTACAO / FIELD_DATA_IMPLANTACAO |
| Data de Pagamento da Primeira Cobrança Mensal | `f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2` | date | Sim | FIELD_DATA_PRIMEIRA_COBRANCA |
| E-mail Assinante do Contrato | `a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6` | varchar | Sim | SIGNER: Contato Principal |
| E-mail Consultor GEBRAS | `3bacd163054a20c843e79bc525bebc1285773b17` | set | Sim | FIELD_EMAIL_CONSULTOR_GEBRAS / SIGNER: Consultor |
| E-mail Coordenador GEBRAS | `3a5c1d1dc1b5f023f57c65b9bf725c27d754d31b` | set | Sim | FIELD_EMAIL_COORDENADOR_GEBRAS / SIGNER: Coordenador |
| E-mail Diretor GEBRAS | `a2eba4ca348f3597d570d84c356aa66e81d762cd` | set | Sim | FIELD_EMAIL_DIRETOR_GEBRAS / SIGNER: Diretor |
| E-mail Gestor Contratante | `3002b2df87f0577585ebaec394fd09a38ca8778f` | varchar | Sim | FIELD_CONTATO_CONTRATANTE |
| Email Financeiro Contratante | `722da69afe31c1f8fa4f5457a223e2a952ae0978` | varchar | Sim | FIELD_CONTATO_FINANCEIRO |
| Endereço | `81566ac6e038bb0ba3adfa122c798b3e497b7538` | address | Sim | FIELD_ENDERECO |
| Filial | `be20f11317ac66845bf97695f43e57795e26d01d` | enum | Sim | FIELD_FILIAL -> BranchId Plune |
| Gestão ACL - Mercado Livre de Energia | `8f998d4877d478b3905c126d8b23f205d0686b77` | double | Sim | FIELD_GESTAO_ACL |
| Gestão da Qualidade de Energia | `ffb2d5aec9acdee5a242ca19683bbf4caa24cd53` | double | Sim | FIELD_INDICADORES_QUALIDADE (Gestão da Qualidade de Energia) |
| Gestão Usina Fotovoltaica | `1ba1794470354856aaca3e784349cd5f9f4d074e` | double | Sim | FIELD_GESTAO_USINA_FOTOVOLTAICA |
| Inscrição Estadual | `c3e623cfa197040b778400a8977ae2c8a8386024` | varchar | Sim | FIELD_INSCRICAO_ESTADUAL -> inscricao_estadual (contrato) |
| Inscrição Municipal | `f40caca58878f19aefba960b87127753b7b932ca` | varchar | Sim | FIELD_INSCRICAO_MUNICIPAL |
| Município/Estado | `2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5` | address | Sim | FIELD_CIDADE |
| Notas | `14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b` | varchar | Sim | FIELD_NOTAS |
| Observações (Detalhes) | `4fba2f9323c64acdcac770e38f2c0cdb840796bc` | varchar | Sim | FIELD_OBSERVACOES_DETALHES (opcional) |
| Porcentagem de Exito | `225005fe8384d97183e5480781ea8ea82982301e` | enum | Sim | FIELD_PERCENTUAL_EXITO -> percentual_exito (contrato) |
| Quantidade de UC's | `c6d1c300a1d070c1a54494a246f6330beabe36aa` | varchar | Sim | FIELD_QUANTIDADE_UCS |
| Regional | `14855b5973f28e97dafd4e2abccc539d7461dc24` | enum | Sim | FIELD_REGIONAL (Regional / SubCentroCusto2Id) |
| Sole Consultoria | `c0a23912d889e00f51ed5bd08a55856a7e5dc930` | double | Sim | FIELD_QUALIDADE_ENERGIA (Sole Consultoria) |
| SOLE Web | `f9923cdce1274da8c10cec1b9ab561e024504620` | double | Sim | FIELD_QTD_SOLE |
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
| CEP | `6d3373f7ee86c7d2449824136baf3ee1938a8ef1` | varchar | FIELD_CEP -> CEPPrincipal / ClienteCep |
| Consultor | `60ffe8e9c2aa51f717865559e86e6044bfb335e6` | enum | FIELD_SUBCENTRO_NIVEL_3 (Consultor / SubCentroCusto3Id) |
| Contratante | `28d491e0263008b437e28fc55bbad8302c4646c8` | text | FIELD_NOME_CLIENTE |
| CPF/CNPJ | `176d2a0d5167d1edc9b949c75f8b9a7597eabe91` | varchar | FIELD_DOCUMENTO |
| Código Cliente/Código da Instalação | `41a3157128d51e2fc803eeec4b242efafcb55b4e` | varchar | FIELD_CODIGO_CLIENTE_INSTALACAO |
| Data de Pagamento da Implantação | `2b8f62a107891e26390459cfa4048b3eedade11b` | date | FIELD_DATA_PAGAMENTO_IMPLANTACAO / FIELD_DATA_IMPLANTACAO |
| Data de Pagamento da Primeira Cobrança Mensal | `f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2` | date | FIELD_DATA_PRIMEIRA_COBRANCA |
| E-mail Assinante do Contrato | `a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6` | varchar | SIGNER: Contato Principal |
| E-mail Consultor GEBRAS | `3bacd163054a20c843e79bc525bebc1285773b17` | set | FIELD_EMAIL_CONSULTOR_GEBRAS / SIGNER: Consultor |
| E-mail Coordenador GEBRAS | `3a5c1d1dc1b5f023f57c65b9bf725c27d754d31b` | set | FIELD_EMAIL_COORDENADOR_GEBRAS / SIGNER: Coordenador |
| E-mail Diretor GEBRAS | `a2eba4ca348f3597d570d84c356aa66e81d762cd` | set | FIELD_EMAIL_DIRETOR_GEBRAS / SIGNER: Diretor |
| E-mail Gestor Contratante | `3002b2df87f0577585ebaec394fd09a38ca8778f` | varchar | FIELD_CONTATO_CONTRATANTE |
| Email Financeiro Contratante | `722da69afe31c1f8fa4f5457a223e2a952ae0978` | varchar | FIELD_CONTATO_FINANCEIRO |
| Endereço | `81566ac6e038bb0ba3adfa122c798b3e497b7538` | address | FIELD_ENDERECO |
| Filial | `be20f11317ac66845bf97695f43e57795e26d01d` | enum | FIELD_FILIAL -> BranchId Plune |
| Gestão ACL - Mercado Livre de Energia | `8f998d4877d478b3905c126d8b23f205d0686b77` | double | FIELD_GESTAO_ACL |
| Gestão da Qualidade de Energia | `ffb2d5aec9acdee5a242ca19683bbf4caa24cd53` | double | FIELD_INDICADORES_QUALIDADE (Gestão da Qualidade de Energia) |
| Gestão Usina Fotovoltaica | `1ba1794470354856aaca3e784349cd5f9f4d074e` | double | FIELD_GESTAO_USINA_FOTOVOLTAICA |
| Inscrição Estadual | `c3e623cfa197040b778400a8977ae2c8a8386024` | varchar | FIELD_INSCRICAO_ESTADUAL -> inscricao_estadual (contrato) |
| Inscrição Municipal | `f40caca58878f19aefba960b87127753b7b932ca` | varchar | FIELD_INSCRICAO_MUNICIPAL |
| Município/Estado | `2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5` | address | FIELD_CIDADE |
| Notas | `14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b` | varchar | FIELD_NOTAS |
| Observações (Detalhes) | `4fba2f9323c64acdcac770e38f2c0cdb840796bc` | varchar | FIELD_OBSERVACOES_DETALHES (opcional) |
| Porcentagem de Exito | `225005fe8384d97183e5480781ea8ea82982301e` | enum | FIELD_PERCENTUAL_EXITO -> percentual_exito (contrato) |
| Quantidade de UC's | `c6d1c300a1d070c1a54494a246f6330beabe36aa` | varchar | FIELD_QUANTIDADE_UCS |
| Regional | `14855b5973f28e97dafd4e2abccc539d7461dc24` | enum | FIELD_REGIONAL (Regional / SubCentroCusto2Id) |
| Sole Consultoria | `c0a23912d889e00f51ed5bd08a55856a7e5dc930` | double | FIELD_QUALIDADE_ENERGIA (Sole Consultoria) |
| SOLE Web | `f9923cdce1274da8c10cec1b9ab561e024504620` | double | FIELD_QTD_SOLE |
| Valor de Implantação | `015407d5106c321a227f1ca881f920fe2e1042ec` | monetary | FIELD_VALOR_IMPLANTACAO |
| Valor Recorrência | `2a331c4b62c9d46aae9451af25eca2d08a3fdf0a` | monetary | FIELD_VALOR_MENSAL |

## Usados pela automação

Definidos em `core/pipedrive_fields.py`.

| Nome no Pipedrive | Hash | Constante / papel |
|---|---|---|
| CEP | `6d3373f7ee86c7d2449824136baf3ee1938a8ef1` | FIELD_CEP -> CEPPrincipal / ClienteCep |
| Consultor | `60ffe8e9c2aa51f717865559e86e6044bfb335e6` | FIELD_SUBCENTRO_NIVEL_3 (Consultor / SubCentroCusto3Id) |
| Contratante | `28d491e0263008b437e28fc55bbad8302c4646c8` | FIELD_NOME_CLIENTE |
| CPF/CNPJ | `176d2a0d5167d1edc9b949c75f8b9a7597eabe91` | FIELD_DOCUMENTO |
| Código Cliente/Código da Instalação | `41a3157128d51e2fc803eeec4b242efafcb55b4e` | FIELD_CODIGO_CLIENTE_INSTALACAO |
| Data de Pagamento da Implantação | `2b8f62a107891e26390459cfa4048b3eedade11b` | FIELD_DATA_PAGAMENTO_IMPLANTACAO / FIELD_DATA_IMPLANTACAO |
| Data de Pagamento da Primeira Cobrança Mensal | `f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2` | FIELD_DATA_PRIMEIRA_COBRANCA |
| E-mail Assinante do Contrato | `a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6` | SIGNER: Contato Principal |
| E-mail Consultor GEBRAS | `3bacd163054a20c843e79bc525bebc1285773b17` | FIELD_EMAIL_CONSULTOR_GEBRAS / SIGNER: Consultor |
| E-mail Coordenador GEBRAS | `3a5c1d1dc1b5f023f57c65b9bf725c27d754d31b` | FIELD_EMAIL_COORDENADOR_GEBRAS / SIGNER: Coordenador |
| E-mail Diretor GEBRAS | `a2eba4ca348f3597d570d84c356aa66e81d762cd` | FIELD_EMAIL_DIRETOR_GEBRAS / SIGNER: Diretor |
| E-mail Gestor Contratante | `3002b2df87f0577585ebaec394fd09a38ca8778f` | FIELD_CONTATO_CONTRATANTE |
| Email Financeiro Contratante | `722da69afe31c1f8fa4f5457a223e2a952ae0978` | FIELD_CONTATO_FINANCEIRO |
| Endereço | `81566ac6e038bb0ba3adfa122c798b3e497b7538` | FIELD_ENDERECO |
| Filial | `be20f11317ac66845bf97695f43e57795e26d01d` | FIELD_FILIAL -> BranchId Plune |
| Gestão ACL - Mercado Livre de Energia | `8f998d4877d478b3905c126d8b23f205d0686b77` | FIELD_GESTAO_ACL |
| Gestão da Qualidade de Energia | `ffb2d5aec9acdee5a242ca19683bbf4caa24cd53` | FIELD_INDICADORES_QUALIDADE (Gestão da Qualidade de Energia) |
| Gestão Usina Fotovoltaica | `1ba1794470354856aaca3e784349cd5f9f4d074e` | FIELD_GESTAO_USINA_FOTOVOLTAICA |
| Inscrição Estadual | `c3e623cfa197040b778400a8977ae2c8a8386024` | FIELD_INSCRICAO_ESTADUAL -> inscricao_estadual (contrato) |
| Inscrição Municipal | `f40caca58878f19aefba960b87127753b7b932ca` | FIELD_INSCRICAO_MUNICIPAL |
| Município/Estado | `2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5` | FIELD_CIDADE |
| Notas | `14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b` | FIELD_NOTAS |
| Observações (Detalhes) | `4fba2f9323c64acdcac770e38f2c0cdb840796bc` | FIELD_OBSERVACOES_DETALHES (opcional) |
| Porcentagem de Exito | `225005fe8384d97183e5480781ea8ea82982301e` | FIELD_PERCENTUAL_EXITO -> percentual_exito (contrato) |
| Quantidade de UC's | `c6d1c300a1d070c1a54494a246f6330beabe36aa` | FIELD_QUANTIDADE_UCS |
| Regional | `14855b5973f28e97dafd4e2abccc539d7461dc24` | FIELD_REGIONAL (Regional / SubCentroCusto2Id) |
| Sole Consultoria | `c0a23912d889e00f51ed5bd08a55856a7e5dc930` | FIELD_QUALIDADE_ENERGIA (Sole Consultoria) |
| SOLE Web | `f9923cdce1274da8c10cec1b9ab561e024504620` | FIELD_QTD_SOLE |
| Valor de Implantação | `015407d5106c321a227f1ca881f920fe2e1042ec` | FIELD_VALOR_IMPLANTACAO |
| Valor Recorrência | `2a331c4b62c9d46aae9451af25eca2d08a3fdf0a` | FIELD_VALOR_MENSAL |
