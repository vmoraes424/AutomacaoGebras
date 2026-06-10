export type CrmUser = {
  id: number;
  name: string;
  email: string;
};

export type CrmDeal = {
  id: number;
  title: string;
  owner_id: number | null;
  stage_id: number | null;
  status: string;
  pipeline_id: number | null;
};

export type FormPayloadV1 = {
  schema_version: string;
  cliente: {
    contratante: string;
    documento: string;
    endereco: string;
    cep: string;
    municipio_estado: string;
    inscricao_estadual: string;
    inscricao_municipal: string;
    notas: string;
    codigo_cliente_instalacao: string;
  };
  servicos: {
    sole_web: number;
    sole_consultoria: number;
    gestao_acl: number;
    gestao_usina_fotovoltaica: number;
    gestao_qualidade_energia: number;
    quantidade_ucs: number;
  };
  valores: {
    valor_recorrencia: string;
    valor_implantacao: string;
  };
  datas: {
    data_pagamento_implantacao: string;
    data_primeira_cobranca: string;
  };
  comercial: {
    filial: string;
    regional: string;
    consultor: string;
    percentual_exito: string;
  };
  signatarios: {
    email_assinante_contrato: string;
    email_consultor_gebras: string;
    email_coordenador_gebras: string;
    email_diretor_gebras: string;
    email_financeiro_contratante: string;
    email_gestor_contratante: string;
  };
  hub: {
    observacoes_detalhes: string;
  };
  anexos?: {
    proposta_comercial_anexada: boolean;
  };
};

export type FormRecord = {
  deal_id: number;
  status: string;
  schema_version: string;
  payload: FormPayloadV1;
  owner_user_id: number | null;
  owner_name: string;
  deal_title: string;
  created_at?: string;
  updated_at?: string;
  submitted_at?: string | null;
  validation_errors?: Record<string, string> | null;
};

export type FormDraftBody = {
  payload: FormPayloadV1;
  schema_version: string;
  owner_user_id?: number | null;
  owner_name?: string;
  deal_title?: string;
};
