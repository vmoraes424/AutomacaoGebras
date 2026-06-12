import type {
  FormPayloadV1,
  HubInstalacaoPedido,
  HubServicoCatalogo,
  HubServicoItem,
  UcLinhaV1,
  UcServicoKey,
} from "../api/types";
import {
  HUB_SERVICOS_CATALOGO_FALLBACK,
  emptyHubServicoItem,
  servicosTemplateHub as servicosTemplateFromCatalog,
} from "./hubCatalog";
import { formatMoneyBr, parseMoneyBr } from "./money";

export const UC_SERVICO_KEYS = HUB_SERVICOS_CATALOGO_FALLBACK.map(
  (s) => s.chave,
) as UcServicoKey[];

export const UC_SERVICO_LABELS: Record<UcServicoKey, string> = Object.fromEntries(
  HUB_SERVICOS_CATALOGO_FALLBACK.map((s) => [s.chave, `${s.nome} (${s.sigla})`]),
) as Record<UcServicoKey, string>;

export function catalogoOrdenado(catalogo?: HubServicoCatalogo[]): HubServicoCatalogo[] {
  const base = catalogo?.length ? catalogo : HUB_SERVICOS_CATALOGO_FALLBACK;
  return [...base].sort((a, b) => a.ordem_form - b.ordem_form);
}

export function parseCodigoClienteInstalacao(raw: string): {
  codigoCliente: number | null;
  codigosInstalacao: number[];
} {
  const texto = (raw ?? "").trim();
  if (!texto) return { codigoCliente: null, codigosInstalacao: [] };

  const parseIntStrict = (part: string): number | null => {
    const n = Number(part.trim());
    return Number.isFinite(n) && part.trim() !== "" ? n : null;
  };

  if (texto.includes("/")) {
    const [clientePart, instPart] = texto.split("/", 2);
    const codigoCliente = parseIntStrict(clientePart);
    if (codigoCliente === null) return { codigoCliente: null, codigosInstalacao: [] };
    const codigosInstalacao = instPart
      .split(/[,;\s]+/)
      .map((p) => parseIntStrict(p))
      .filter((n): n is number => n !== null);
    return { codigoCliente, codigosInstalacao };
  }

  const codigoCliente = parseIntStrict(texto.split(",")[0]);
  return { codigoCliente, codigosInstalacao: [] };
}

export function formatCodigoClienteInstalacao(
  codigoCliente: number,
  codigosInstalacao: number[],
): string {
  if (!codigosInstalacao.length) return String(codigoCliente);
  return `${codigoCliente}/${codigosInstalacao.join(",")}`;
}

export function codigoClienteOnly(raw: string): string {
  const { codigoCliente } = parseCodigoClienteInstalacao(raw);
  return codigoCliente !== null ? String(codigoCliente) : raw.trim();
}

export function servicoAtivoPorValor(valor: string): boolean {
  const n = parseMoneyBr(valor);
  return n !== null && n > 0;
}

export function servicoItemAtivo(item: HubServicoItem): boolean {
  return servicoAtivoPorValor(item.valor);
}

export function normalizeServicoItem(item: HubServicoItem): HubServicoItem {
  const valor = String(item.valor ?? "");
  return { ...item, valor, ativo: servicoAtivoPorValor(valor) };
}

export function servicoPatchFromValor(valor: string): Pick<HubServicoItem, "valor" | "ativo"> {
  const v = String(valor ?? "");
  return { valor: v, ativo: servicoAtivoPorValor(v) };
}

export function valorUcInstalacao(inst: HubInstalacaoPedido): number {
  let total = 0;
  for (const item of inst.servicos) {
    if (!servicoItemAtivo(item)) continue;
    total += parseMoneyBr(item.valor) ?? 0;
  }
  return Math.round(total * 100) / 100;
}

export function instalacaoTemServico(inst: HubInstalacaoPedido): boolean {
  return valorUcInstalacao(inst) > 0;
}

export function formatValorBrHub(valor: number): string {
  const [inteiro, frac] = valor.toFixed(2).split(".");
  const inteiroFmt = Number(inteiro).toLocaleString("pt-BR", { maximumFractionDigits: 0 });
  return `${inteiroFmt},${frac}`;
}

export function identificacaoUcHub(inst: HubInstalacaoPedido): string {
  const ident = inst.identificacao.trim();
  if (ident) return ident;
  return String(inst.codigo_instalacao).padStart(5, "0");
}

export function buildObservacoesDetalhesHub(instalacoes: HubInstalacaoPedido[]): string {
  const blocos: string[] = [];
  for (const inst of instalacoes) {
    if (!instalacaoTemServico(inst)) continue;
    const nomes: string[] = [];
    for (const item of inst.servicos) {
      if (!servicoItemAtivo(item)) continue;
      nomes.push(item.nome_pipe || item.nome);
    }
    if (!nomes.length) continue;
    blocos.push(
      `UC = ${identificacaoUcHub(inst)} - ${nomes.join(" + ")} = ${formatValorBrHub(valorUcInstalacao(inst))}`,
    );
  }
  return blocos.join("; ");
}

export function somaValoresHub(instalacoes: HubInstalacaoPedido[]): number {
  let total = 0;
  for (const inst of instalacoes) {
    total += valorUcInstalacao(inst);
  }
  return Math.round(total * 100) / 100;
}

export function countUcsAtivas(instalacoes: HubInstalacaoPedido[]): number {
  return instalacoes.filter(instalacaoTemServico).length;
}

function mergeServicosInstalacao(
  existentes: HubServicoItem[] | undefined,
  catalogo: HubServicoCatalogo[],
): HubServicoItem[] {
  const porChave = new Map((existentes ?? []).map((s) => [s.chave, s]));
  return catalogo.map((cat) => {
    const prev = porChave.get(cat.chave);
    return normalizeServicoItem({
      ...emptyHubServicoItem(cat),
      valor: String(prev?.valor ?? ""),
      ativo: false,
    });
  });
}

function legacyUcLinhaParaInstalacao(
  linha: UcLinhaV1,
  codigoCliente: number,
  catalogo: HubServicoCatalogo[],
): HubInstalacaoPedido {
  const servicos = catalogo.map((cat) => {
    const celula = linha.servicos[cat.chave as UcServicoKey];
    return normalizeServicoItem({
      ...emptyHubServicoItem(cat),
      valor: String(celula?.valor ?? ""),
      ativo: false,
    });
  });
  const inst: HubInstalacaoPedido = {
    codigo_instalacao: linha.codigo_instalacao,
    codigo_cliente: codigoCliente,
    identificacao: linha.identificacao,
    razao_social: linha.razao_social,
    cidade: linha.cidade,
    uf: linha.uf,
    ativo: true,
    valor_uc: "",
    servicos,
  };
  const v = valorUcInstalacao(inst);
  inst.valor_uc = v > 0 ? String(v) : "";
  return inst;
}

export function getHubInstalacoes(
  payload: FormPayloadV1,
  catalogo?: HubServicoCatalogo[],
): HubInstalacaoPedido[] {
  const cat = catalogoOrdenado(catalogo);
  if (payload.hub.instalacoes?.length) {
    return payload.hub.instalacoes.map((inst) => ({
      ...inst,
      ativo: inst.ativo ?? true,
      servicos: mergeServicosInstalacao(inst.servicos, cat),
      valor_uc: String(valorUcInstalacao({ ...inst, servicos: mergeServicosInstalacao(inst.servicos, cat) }) || ""),
    }));
  }
  const { codigoCliente } = parseCodigoClienteInstalacao(payload.cliente.codigo_cliente_instalacao);
  const cc = codigoCliente ?? 0;
  const linhas = payload.servicos.uc_linhas ?? [];
  return linhas.map((l) => legacyUcLinhaParaInstalacao(l, cc, cat));
}

export function deriveCodigoClienteInstalacao(
  codigoCliente: number,
  instalacoes: HubInstalacaoPedido[],
): string {
  const codigos = instalacoes
    .filter(instalacaoTemServico)
    .map((i) => i.codigo_instalacao)
    .sort((a, b) => a - b);
  return formatCodigoClienteInstalacao(codigoCliente, codigos);
}

export function applyHubInstalacoes(
  payload: FormPayloadV1,
  instalacoes: HubInstalacaoPedido[],
  codigoCliente: number,
  catalogo?: HubServicoCatalogo[],
): FormPayloadV1 {
  const cat = catalogoOrdenado(catalogo);
  const normalized = instalacoes.map((inst) => {
    const servicos = mergeServicosInstalacao(inst.servicos, cat);
    const v = valorUcInstalacao({ ...inst, servicos });
    return {
      ...inst,
      codigo_cliente: codigoCliente,
      servicos,
      valor_uc: v > 0 ? String(v) : "",
    };
  });
  const total = somaValoresHub(normalized);
  const valorRecorrencia = total > 0 ? String(total) : "";
  return {
    ...payload,
    cliente: {
      ...payload.cliente,
      codigo_cliente_instalacao: deriveCodigoClienteInstalacao(codigoCliente, normalized),
    },
    valores: {
      ...payload.valores,
      ...(valorRecorrencia ? { valor_recorrencia: valorRecorrencia } : {}),
    },
    hub: {
      ...payload.hub,
      instalacoes: normalized,
      observacoes_detalhes: buildObservacoesDetalhesHub(normalized),
      valor_total: valorRecorrencia,
    },
  };
}

/** @deprecated use applyHubInstalacoes */
export function applyUcMatrix(
  payload: FormPayloadV1,
  linhas: UcLinhaV1[],
  codigoCliente: number,
  catalogo?: HubServicoCatalogo[],
): FormPayloadV1 {
  const cat = catalogoOrdenado(catalogo);
  const instalacoes = linhas.map((l) => legacyUcLinhaParaInstalacao(l, codigoCliente, cat));
  return applyHubInstalacoes(payload, instalacoes, codigoCliente, cat);
}

export function mergeHubInstalacoes(
  payload: FormPayloadV1,
  instalacoes: Array<{
    codigo: number;
    identificacao: string;
    razao_social: string;
    cidade: string;
    uf: string;
    ativo: boolean;
  }>,
  codigoCliente: number,
  catalogo?: HubServicoCatalogo[],
): FormPayloadV1 {
  const cat = catalogoOrdenado(catalogo);
  const prev = getHubInstalacoes(payload, cat);
  const prevMap = new Map(prev.map((i) => [i.codigo_instalacao, i]));

  const rows: HubInstalacaoPedido[] = instalacoes.map((inst) => {
    const existing = prevMap.get(inst.codigo);
    if (existing) {
      return {
        ...existing,
        identificacao: inst.identificacao,
        razao_social: inst.razao_social,
        cidade: inst.cidade,
        uf: inst.uf,
        ativo: inst.ativo,
        servicos: mergeServicosInstalacao(existing.servicos, cat),
      };
    }
    return {
      codigo_instalacao: inst.codigo,
      codigo_cliente: codigoCliente,
      identificacao: inst.identificacao,
      razao_social: inst.razao_social,
      cidade: inst.cidade,
      uf: inst.uf,
      ativo: inst.ativo,
      valor_uc: "",
      servicos: servicosTemplateFromCatalog(cat),
    };
  });

  return applyHubInstalacoes(payload, rows, codigoCliente, cat);
}

export function syncValorRecorrenciaFromHub(
  payload: FormPayloadV1,
  catalogo?: HubServicoCatalogo[],
): FormPayloadV1 {
  const total = somaValoresHub(getHubInstalacoes(payload, catalogo));
  if (total <= 0) return payload;
  const valorRecorrencia = String(total);
  if (
    payload.valores.valor_recorrencia === valorRecorrencia &&
    payload.hub.valor_total === valorRecorrencia
  ) {
    return payload;
  }
  return {
    ...payload,
    valores: { ...payload.valores, valor_recorrencia: valorRecorrencia },
    hub: { ...payload.hub, valor_total: valorRecorrencia },
  };
}

export function pipeFieldsFromUcMatrix(payload: FormPayloadV1): Array<{
  path: string;
  value: string | number;
}> {
  const fields: Array<{ path: string; value: string | number }> = [
    {
      path: "cliente.codigo_cliente_instalacao",
      value: payload.cliente.codigo_cliente_instalacao,
    },
  ];
  if (payload.valores.valor_recorrencia) {
    fields.push({
      path: "valores.valor_recorrencia",
      value: payload.valores.valor_recorrencia,
    });
  }
  return fields;
}

export function sumColunaServico(
  instalacoes: HubInstalacaoPedido[],
  chave: string,
): number {
  let total = 0;
  for (const inst of instalacoes) {
    const item = inst.servicos.find((s) => s.chave === chave);
    if (item && servicoItemAtivo(item)) total += parseMoneyBr(item.valor) ?? 0;
  }
  return Math.round(total * 100) / 100;
}

export function servicosTemplateHub(catalogo?: HubServicoCatalogo[]): HubServicoItem[] {
  return servicosTemplateFromCatalog(catalogoOrdenado(catalogo));
}

/** Legado — matriz por chave fixa (testes / migração). */
export function emptyUcServicosMatriz(): UcLinhaV1["servicos"] {
  const out = {} as UcLinhaV1["servicos"];
  for (const cat of HUB_SERVICOS_CATALOGO_FALLBACK) {
    out[cat.chave as UcServicoKey] = { ativo: false, valor: "" };
  }
  return out;
}
