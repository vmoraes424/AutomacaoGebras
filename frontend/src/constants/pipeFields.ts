/** Caminhos do formulário v1 mapeados para custom fields do Pipedrive (FORM_PATH_TO_PIPE). */
export const PIPE_FIELD_PATHS = new Set([
  "cliente.contratante",
  "cliente.documento",
  "cliente.endereco",
  "cliente.cep",
  "cliente.municipio_estado",
  "cliente.inscricao_estadual",
  "cliente.inscricao_municipal",
  "cliente.notas",
  "cliente.codigo_cliente_instalacao",
  "servicos.sole_web",
  "servicos.sole_consultoria",
  "servicos.gestao_acl",
  "servicos.gestao_usina_fotovoltaica",
  "servicos.gestao_qualidade_energia",
  "servicos.quantidade_ucs",
  "valores.valor_recorrencia",
  "valores.valor_implantacao",
  "datas.data_pagamento_implantacao",
  "datas.data_primeira_cobranca",
  "comercial.filial",
  "comercial.regional",
  "comercial.consultor",
  "comercial.percentual_exito",
  "signatarios.email_assinante_contrato",
  "signatarios.email_consultor_gebras",
  "signatarios.email_coordenador_gebras",
  "signatarios.email_diretor_gebras",
  "signatarios.email_financeiro_contratante",
  "signatarios.email_gestor_contratante",
  "hub.observacoes_detalhes",
]);

export function isPipeField(fieldPath: string): boolean {
  return PIPE_FIELD_PATHS.has(fieldPath);
}
