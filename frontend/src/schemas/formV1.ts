import type { FormPayloadV1 } from "../api/types";
import { syncValorRecorrenciaFromHub } from "../utils/ucServicos";

/** Payload vazio alinhado a tests/fixtures/formulario_v1/form_payload_v1_g1.json */
export function emptyFormPayloadV1(): FormPayloadV1 {
  return {
    schema_version: "v1",
    cliente: {
      contratante: "",
      documento: "",
      endereco: "",
      cep: "",
      municipio_estado: "",
      inscricao_estadual: "",
      inscricao_municipal: "",
      notas: "",
      codigo_cliente_instalacao: "",
    },
    servicos: {
      sole_web: 0,
      sole_consultoria: 0,
      gestao_acl: 0,
      gestao_usina_fotovoltaica: 0,
      gestao_qualidade_energia: 0,
      quantidade_ucs: 0,
      uc_linhas: [],
    },
    valores: {
      valor_recorrencia: "",
      valor_implantacao: "0",
    },
    datas: {
      data_pagamento_implantacao: "",
      data_primeira_cobranca: "",
    },
    comercial: {
      filial: "",
      regional: "",
      consultor: "",
      percentual_exito: "",
    },
    signatarios: {
      email_assinante_contrato: "",
      email_consultor_gebras: "",
      email_coordenador_gebras: "",
      email_diretor_gebras: "",
      email_financeiro_contratante: "",
      email_gestor_contratante: "",
    },
    hub: {
      observacoes_detalhes: "",
      valor_total: "",
      instalacoes: [],
    },
  };
}

/** Mescla payload salvo com template (garante todas as chaves v1). */
export function mergeFormPayloadV1(saved: Partial<FormPayloadV1> | undefined): FormPayloadV1 {
  const base = emptyFormPayloadV1();
  if (!saved) return base;
  const merged: FormPayloadV1 = {
    ...base,
    ...saved,
    cliente: { ...base.cliente, ...saved.cliente },
    servicos: {
      ...base.servicos,
      ...saved.servicos,
      uc_linhas: saved.servicos?.uc_linhas ?? base.servicos.uc_linhas,
    },
    valores: { ...base.valores, ...saved.valores },
    datas: { ...base.datas, ...saved.datas },
    comercial: { ...base.comercial, ...saved.comercial },
    signatarios: { ...base.signatarios, ...saved.signatarios },
    hub: {
      ...base.hub,
      ...saved.hub,
      instalacoes: saved.hub?.instalacoes ?? base.hub.instalacoes,
    },
  };
  return syncValorRecorrenciaFromHub(merged);
}
