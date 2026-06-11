import type { HubServicoCatalogo, HubServicoItem } from "../api/types";

/** Fallback alinhado a core/hub_catalogo.py (pedido_nome_servico). */
export const HUB_SERVICOS_CATALOGO_FALLBACK: HubServicoCatalogo[] = [
  {
    codigo_servico: 2,
    chave: "sole_web",
    nome: "SOLE Web (com telemetria)",
    sigla: "SW",
    nome_pipe: "SOLE WEB",
    ordem_form: 1,
  },
  {
    codigo_servico: 1,
    chave: "sole_consultoria",
    nome: "SOLE Consultoria",
    sigla: "SC",
    nome_pipe: "Sole Consultoria",
    ordem_form: 2,
  },
  {
    codigo_servico: 4,
    chave: "gestao_acl",
    nome: "Gestão Mercado Livre",
    sigla: "GML",
    nome_pipe: "ACL",
    ordem_form: 3,
  },
  {
    codigo_servico: 3,
    chave: "gestao_usina_fotovoltaica",
    nome: "Gestão de Usina Fotovoltaica",
    sigla: "GUF",
    nome_pipe: "Gestão de Usina Fotovoltaica",
    ordem_form: 4,
  },
  {
    codigo_servico: 6,
    chave: "gestao_qualidade_energia",
    nome: "Gestão de Qualidade de Energia",
    sigla: "GQE",
    nome_pipe: "Gestão de Qualidade de Energia",
    ordem_form: 5,
  },
];

export function emptyHubServicoItem(cat: HubServicoCatalogo): HubServicoItem {
  return {
    codigo_servico: cat.codigo_servico,
    chave: cat.chave,
    nome: cat.nome,
    sigla: cat.sigla,
    nome_pipe: cat.nome_pipe,
    ativo: false,
    valor: "",
  };
}

export function servicosTemplateHub(catalogo: HubServicoCatalogo[]): HubServicoItem[] {
  return catalogo.map(emptyHubServicoItem);
}
