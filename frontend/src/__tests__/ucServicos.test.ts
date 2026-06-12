import { describe, expect, it } from "vitest";
import { emptyFormPayloadV1 } from "../schemas/formV1";
import {
  applyHubInstalacoes,
  applyUcMatrix,
  buildObservacoesDetalhesHub,
  emptyUcServicosMatriz,
  formatCodigoClienteInstalacao,
  parseCodigoClienteInstalacao,
  mergeHubInstalacoes,
  pipeFieldsFromUcMatrix,
  servicosTemplateHub,
  servicoAtivoPorValor,
  servicoItemAtivo,
  servicoPatchFromValor,
  somaValoresHub,
} from "../utils/ucServicos";
import { HUB_SERVICOS_CATALOGO_FALLBACK } from "../utils/hubCatalog";

describe("ucServicos", () => {
  it("parse e format codigo cliente/instalacao", () => {
    expect(parseCodigoClienteInstalacao("352")).toEqual({
      codigoCliente: 352,
      codigosInstalacao: [],
    });
    expect(formatCodigoClienteInstalacao(352, [665, 1942])).toBe("352/665,1942");
  });

  it("matriz HUB nao sobrescreve contadores do Pipe", () => {
    const base = emptyFormPayloadV1();
    base.servicos.sole_web = 99;
    base.servicos.quantidade_ucs = 5;
    const linhas = [
      {
        codigo_instalacao: 665,
        identificacao: "00665",
        razao_social: "",
        cidade: "",
        uf: "",
        servicos: {
          ...emptyUcServicosMatriz(),
          sole_web: { ativo: true, valor: "1000" },
        },
      },
    ];
    const next = applyUcMatrix(base, linhas, 352);
    expect(next.servicos.sole_web).toBe(99);
    expect(next.servicos.quantidade_ucs).toBe(5);
    expect(next.hub.observacoes_detalhes).toContain("SOLE WEB");
    expect(next.hub.valor_total).toBe("1000");
    expect(next.valores.valor_recorrencia).toBe("1000");
    expect(next.hub.instalacoes[0].valor_uc).toBe("1000");
    expect(next.cliente.codigo_cliente_instalacao).toBe("352/665");
    expect(somaValoresHub(next.hub.instalacoes)).toBe(1000);
    expect(buildObservacoesDetalhesHub(next.hub.instalacoes)).toBe(
      "UC = 00665 - SOLE WEB = 1.000,00",
    );
  });

  it("servico ativo depende só do valor > 0", () => {
    expect(servicoAtivoPorValor("45")).toBe(true);
    expect(servicoAtivoPorValor("0")).toBe(false);
    expect(servicoAtivoPorValor("")).toBe(false);
    const patch = servicoPatchFromValor("1000");
    expect(patch).toEqual({ valor: "1000", ativo: true });
    expect(servicoPatchFromValor("")).toEqual({ valor: "", ativo: false });

    const servicos = servicosTemplateHub(HUB_SERVICOS_CATALOGO_FALLBACK);
    const sw = servicos.find((s) => s.chave === "sole_web")!;
    expect(servicoItemAtivo({ ...sw, ativo: false, valor: "1000" })).toBe(true);
    expect(servicoItemAtivo({ ...sw, ativo: true, valor: "" })).toBe(false);
  });

  it("applyHubInstalacoes estrutura pedido_instalacao_extra", () => {
    const servicos = servicosTemplateHub(HUB_SERVICOS_CATALOGO_FALLBACK);
    const sw = servicos.find((s) => s.chave === "sole_web")!;
    sw.valor = "1950";
    const next = applyHubInstalacoes(emptyFormPayloadV1(), [
      {
        codigo_instalacao: 12108,
        codigo_cliente: 352,
        identificacao: "625700568",
        razao_social: "",
        cidade: "",
        uf: "",
        valor_uc: "",
        servicos,
      },
    ], 352);
    expect(next.hub.instalacoes[0].servicos.find((s) => s.chave === "sole_web")?.codigo_servico).toBe(2);
    expect(next.hub.valor_total).toBe("1950");
    expect(next.valores.valor_recorrencia).toBe("1950");
  });

  it("mergeHubInstalacoes atualiza ativo do HUB sem perder serviços salvos", () => {
    const servicos = servicosTemplateHub(HUB_SERVICOS_CATALOGO_FALLBACK);
    const base = applyHubInstalacoes(emptyFormPayloadV1(), [
      {
        codigo_instalacao: 2652,
        codigo_cliente: 352,
        identificacao: "",
        razao_social: "",
        cidade: "Pelotas",
        uf: "RS",
        ativo: true,
        valor_uc: "",
        servicos,
      },
    ], 352);

    const next = mergeHubInstalacoes(
      base,
      [
        {
          codigo: 2652,
          identificacao: "",
          razao_social: "",
          cidade: "Pelotas",
          uf: "RS",
          ativo: false,
        },
      ],
      352,
      HUB_SERVICOS_CATALOGO_FALLBACK,
    );

    expect(next.hub.instalacoes[0].ativo).toBe(false);
    expect(next.hub.instalacoes[0].servicos.length).toBe(servicos.length);
  });

  it("pipeFieldsFromUcMatrix envia codigo cliente/instalacao e valor recorrencia", () => {
    const payload = applyHubInstalacoes(emptyFormPayloadV1(), [], 352);
    expect(pipeFieldsFromUcMatrix(payload)).toEqual([
      { path: "cliente.codigo_cliente_instalacao", value: "352" },
    ]);

    const comValor = applyHubInstalacoes(emptyFormPayloadV1(), [
      {
        codigo_instalacao: 665,
        codigo_cliente: 352,
        identificacao: "00665",
        razao_social: "",
        cidade: "",
        uf: "",
        valor_uc: "",
        servicos: (() => {
          const servicos = servicosTemplateHub(HUB_SERVICOS_CATALOGO_FALLBACK);
          const sw = servicos.find((s) => s.chave === "sole_web")!;
          sw.valor = "6480";
          return servicos;
        })(),
      },
    ], 352);
    expect(pipeFieldsFromUcMatrix(comValor)).toEqual([
      { path: "cliente.codigo_cliente_instalacao", value: "352/665" },
      { path: "valores.valor_recorrencia", value: "6480" },
    ]);
  });
});
