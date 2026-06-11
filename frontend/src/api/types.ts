export type CrmUser = {
  id: number;
  name: string;
  email: string;
};

export type OperationalLabel =
  | "pendente"
  | "rascunho"
  | "erro"
  | "enviado"
  | "processando"
  | "processado";

export type CrmDeal = {
  id: number;
  title: string;
  owner_id: number | null;
  stage_id: number | null;
  status: string;
  pipeline_id: number | null;
  portal_stage?: string;
  form_status?: string | null;
  operational_label?: OperationalLabel;
  ready_for_form?: boolean;
  ready_for_automation?: boolean;
};

export type UcServicoKey =
  | "sole_web"
  | "sole_consultoria"
  | "gestao_acl"
  | "gestao_usina_fotovoltaica"
  | "gestao_qualidade_energia";

export type UcServicoCelula = {
  ativo: boolean;
  valor: string;
};

export type UcLinhaV1 = {
  codigo_instalacao: number;
  identificacao: string;
  razao_social: string;
  cidade: string;
  uf: string;
  servicos: Record<UcServicoKey, UcServicoCelula>;
};

export type HubInstalacao = {
  codigo: number;
  codigo_cliente: number;
  identificacao: string;
  razao_social: string;
  cidade: string;
  uf: string;
  ativo: boolean;
  selecionada: boolean;
};

/** pedido_nome_servico — colunas da matriz UC × serviço */
export type HubServicoCatalogo = {
  codigo_servico: number;
  chave: string;
  nome: string;
  sigla: string;
  nome_pipe: string;
  ordem_form: number;
};

/** pedido_instalacao_servico + valor no form (soma → pedido_instalacao_extra.valor) */
export type HubServicoItem = {
  codigo_servico: number;
  chave: string;
  nome: string;
  sigla: string;
  nome_pipe: string;
  ativo: boolean;
  valor: string;
};

/** pedido_instalacao_extra + serviços filhos */
export type HubInstalacaoPedido = {
  codigo_instalacao: number;
  codigo_cliente: number;
  identificacao: string;
  razao_social: string;
  cidade: string;
  uf: string;
  valor_uc: string;
  servicos: HubServicoItem[];
};

export type HubServicosResponse = {
  servicos: HubServicoCatalogo[];
};

export type HubInstalacoesResponse = {
  codigo_cliente: number;
  codigos_instalacao_selecionados: number[];
  formato_pipedrive: string;
  instalacoes: HubInstalacao[];
  codigos_nao_encontrados: number[];
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
    uc_linhas?: UcLinhaV1[];
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
    valor_total: string;
    instalacoes: HubInstalacaoPedido[];
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
