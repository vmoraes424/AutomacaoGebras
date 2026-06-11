/** Rótulos legíveis para toasts e feedback de sync. */
export const FORM_FIELD_LABELS: Record<string, string> = {
  "cliente.contratante": "Contratante",
  "cliente.documento": "CPF/CNPJ",
  "cliente.endereco": "Endereço",
  "cliente.cep": "CEP",
  "cliente.municipio_estado": "Município / Estado",
  "cliente.inscricao_estadual": "Inscrição estadual",
  "cliente.inscricao_municipal": "Inscrição municipal",
  "cliente.notas": "Notas",
  "cliente.codigo_cliente_instalacao": "Código cliente HUB",
  "servicos.sole_web": "SOLE Web",
  "servicos.sole_consultoria": "Sole Consultoria",
  "servicos.gestao_acl": "Gestão ACL",
  "servicos.gestao_usina_fotovoltaica": "Gestão Usina FV",
  "servicos.gestao_qualidade_energia": "Gestão Qualidade Energia",
  "servicos.quantidade_ucs": "Quantidade de UC's",
  "valores.valor_recorrencia": "Valor recorrência",
  "valores.valor_implantacao": "Valor implantação",
  "datas.data_pagamento_implantacao": "Data pag. implantação",
  "datas.data_primeira_cobranca": "Data 1ª cobrança mensal",
  "comercial.filial": "Filial",
  "comercial.regional": "Regional",
  "comercial.consultor": "Consultor",
  "comercial.percentual_exito": "Porcentagem de êxito",
  "signatarios.email_assinante_contrato": "E-mail assinante contrato",
  "signatarios.email_consultor_gebras": "E-mail consultor Gebras",
  "signatarios.email_coordenador_gebras": "E-mail coordenador Gebras",
  "signatarios.email_diretor_gebras": "E-mail diretor Gebras",
  "signatarios.email_financeiro_contratante": "E-mail financeiro contratante",
  "signatarios.email_gestor_contratante": "E-mail gestor contratante",
  "hub.observacoes_detalhes": "HUB — Observações",
};

export function labelForFieldPath(fieldPath: string): string {
  return FORM_FIELD_LABELS[fieldPath] ?? fieldPath;
}
