import type { FormPayloadV1, HubInstalacaoPedido, HubServicoCatalogo, HubServicoItem } from "../api/types";
import type { CSSProperties } from "react";
import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { formatMoneyBr, moneyToStorage, parseMoneyBr } from "../utils/money";
import { HUB_SERVICOS_CATALOGO_FALLBACK } from "../utils/hubCatalog";
import {
  applyHubInstalacoes,
  buildObservacoesDetalhesHub,
  catalogoOrdenado,
  codigoClienteOnly,
  getHubInstalacoes,
  mergeHubInstalacoes,
  parseCodigoClienteInstalacao,
  countUcsAtivas,
  pipeFieldsFromUcMatrix,
  somaValoresHub,
  sumColunaServico,
  valorUcInstalacao,
} from "../utils/ucServicos";
import { formatDisplayName } from "../utils/formatDisplayName";
import { joinCidadeEstado, splitCidadeEstado } from "../utils/cidadeEstado";
import {
  composeFieldClass,
  fieldError,
  handleFieldPulseAnimationEnd,
  type FieldSyncUiProps,
} from "./formFieldSyncUi";

export type PipeFieldSync = { path: string; value: string | number };

type SectionProps = {
  payload: FormPayloadV1;
  onChange: (next: FormPayloadV1) => void;
  disabled?: boolean;
  fieldErrors?: Record<string, string>;
  onFieldBlur?: (fieldPath: string, value: string | number) => void;
  onSyncPipeFields?: (fields: PipeFieldSync[]) => Promise<void>;
  onPersistDraft?: (payload: FormPayloadV1) => Promise<void>;
} & FieldSyncUiProps;

function BlurGuardTextarea({
  fieldPath,
  value,
  disabled,
  className,
  onChange,
  onFieldBlur,
  onFieldPulseEnd,
}: {
  fieldPath: string;
  value: string;
  disabled?: boolean;
  className?: string;
  onChange: (value: string) => void;
  onFieldBlur?: (fieldPath: string, value: string) => void;
  onFieldPulseEnd?: (fieldPath: string) => void;
}) {
  const valueAtFocus = useRef(value);
  return (
    <textarea
      value={value}
      disabled={disabled}
      className={className}
      onFocus={() => {
        valueAtFocus.current = value;
      }}
      onChange={(e) => onChange(e.target.value)}
      onBlur={(e) => {
        const next = e.target.value;
        if (next === valueAtFocus.current) return;
        onFieldBlur?.(fieldPath, next);
      }}
      onAnimationEnd={(e) => handleFieldPulseAnimationEnd(e, fieldPath, onFieldPulseEnd)}
    />
  );
}

function BlurGuardInput({
  fieldPath,
  value,
  disabled,
  className,
  ariaInvalid,
  onChange,
  onFieldBlur,
  onFieldPulseEnd,
  style,
}: {
  fieldPath: string;
  value: string;
  disabled?: boolean;
  className?: string;
  ariaInvalid?: boolean;
  onChange: (value: string) => void;
  onFieldBlur?: (fieldPath: string, value: string) => void;
  onFieldPulseEnd?: (fieldPath: string) => void;
  style?: CSSProperties;
}) {
  const valueAtFocus = useRef(value);
  return (
    <input
      value={value}
      disabled={disabled}
      aria-invalid={ariaInvalid}
      className={className}
      style={style}
      onFocus={() => {
        valueAtFocus.current = value;
      }}
      onChange={(e) => onChange(e.target.value)}
      onBlur={(e) => {
        const next = e.target.value;
        if (next === valueAtFocus.current) return;
        onFieldBlur?.(fieldPath, next);
      }}
      onAnimationEnd={(e) => handleFieldPulseAnimationEnd(e, fieldPath, onFieldPulseEnd)}
    />
  );
}

function MoneyField({
  label,
  fieldKey,
  value,
  onChange,
  onFieldBlur,
  onFieldPulseEnd,
  disabled,
  fieldErrors,
  fieldSyncPulse,
}: {
  label: string;
  fieldKey: string;
  value: string;
  onChange: (v: string) => void;
  onFieldBlur?: (fieldPath: string, value: string) => void;
  onFieldPulseEnd?: (fieldPath: string) => void;
  disabled?: boolean;
  fieldErrors?: Record<string, string>;
  fieldSyncPulse?: Set<string>;
}) {
  const err = fieldError(fieldErrors, fieldKey);
  const valueAtFocus = useRef("");
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");

  const shown = editing ? draft : formatMoneyBr(value);

  return (
    <label className={err ? "field-has-error" : undefined}>
      {label}
      <input
        type="text"
        inputMode="decimal"
        value={shown}
        disabled={disabled}
        aria-invalid={err ? true : undefined}
        aria-describedby={err ? `${fieldKey}-error` : undefined}
        className={composeFieldClass(fieldKey, {
          validationError: Boolean(err),
          fieldSyncPulse,
        })}
        onFocus={() => {
          valueAtFocus.current = moneyToStorage(value);
          setDraft(formatMoneyBr(value) || moneyToStorage(value));
          setEditing(true);
        }}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={() => {
          setEditing(false);
          const parsed = parseMoneyBr(draft);
          const stored = parsed !== null ? moneyToStorage(parsed) : moneyToStorage(value);
          onChange(stored);
          if (stored === valueAtFocus.current) return;
          onFieldBlur?.(fieldKey, stored);
        }}
        onAnimationEnd={(e) => handleFieldPulseAnimationEnd(e, fieldKey, onFieldPulseEnd)}
      />
      {err && (
        <span id={`${fieldKey}-error`} className="field-error-msg" role="alert">
          {err}
        </span>
      )}
    </label>
  );
}

function MunicipioEstadoFields({
  value,
  disabled,
  fieldErrors,
  onChange,
  onFieldBlur,
  fieldSyncPulse,
  onFieldPulseEnd,
}: {
  value: string;
  disabled?: boolean;
  fieldErrors?: Record<string, string>;
  onChange: (combined: string) => void;
  onFieldBlur?: (fieldPath: string, value: string) => void;
  fieldSyncPulse?: Set<string>;
  onFieldPulseEnd?: (fieldPath: string) => void;
}) {
  const fieldKey = "cliente.municipio_estado";
  const err = fieldError(fieldErrors, fieldKey);
  const split = splitCidadeEstado(value);
  const [municipio, setMunicipio] = useState(split.municipio);
  const [estado, setEstado] = useState(split.estado);
  const focusRef = useRef({ municipio: split.municipio, estado: split.estado });

  useEffect(() => {
    const next = splitCidadeEstado(value);
    setMunicipio(next.municipio);
    setEstado(next.estado);
  }, [value]);

  const commitBlur = () => {
    const combined = joinCidadeEstado(municipio, estado);
    const prev = joinCidadeEstado(focusRef.current.municipio, focusRef.current.estado);
    onChange(combined);
    if (combined !== prev) {
      onFieldBlur?.(fieldKey, combined);
    }
  };

  const inputClass = composeFieldClass(fieldKey, {
    validationError: Boolean(err),
    fieldSyncPulse,
  });

  return (
    <>
      <label className={`field-localizacao-estado${err ? " field-has-error" : ""}`}>
        Estado
        <input
          type="text"
          value={estado}
          disabled={disabled}
          maxLength={2}
          placeholder="UF"
          aria-invalid={err ? true : undefined}
          className={inputClass}
          onFocus={() => {
            focusRef.current = { municipio, estado };
          }}
          onChange={(e) => {
            const next = e.target.value.toUpperCase().replace(/[^A-Z]/g, "").slice(0, 2);
            setEstado(next);
            onChange(joinCidadeEstado(municipio, next));
          }}
          onBlur={commitBlur}
          onAnimationEnd={(e) => handleFieldPulseAnimationEnd(e, fieldKey, onFieldPulseEnd)}
        />
      </label>
      <label className={`field-localizacao-municipio${err ? " field-has-error" : ""}`}>
        Município
        <input
          type="text"
          value={municipio}
          disabled={disabled}
          aria-invalid={err ? true : undefined}
          className={inputClass}
          onFocus={() => {
            focusRef.current = { municipio, estado };
          }}
          onChange={(e) => {
            const next = e.target.value;
            setMunicipio(next);
            onChange(joinCidadeEstado(next, estado));
          }}
          onBlur={commitBlur}
          onAnimationEnd={(e) => handleFieldPulseAnimationEnd(e, fieldKey, onFieldPulseEnd)}
        />
        {err && (
          <span className="field-error-msg" role="alert">
            {err}
          </span>
        )}
      </label>
    </>
  );
}

function Field({
  label,
  fieldKey,
  value,
  onChange,
  onFieldBlur,
  onFieldPulseEnd,
  type = "text",
  disabled,
  fieldErrors,
  fieldSyncPulse,
  className,
}: {
  label: string;
  fieldKey?: string;
  value: string | number;
  onChange: (v: string) => void;
  onFieldBlur?: (fieldPath: string, value: string | number) => void;
  onFieldPulseEnd?: (fieldPath: string) => void;
  type?: string;
  disabled?: boolean;
  fieldErrors?: Record<string, string>;
  fieldSyncPulse?: Set<string>;
  className?: string;
}) {
  const err = fieldKey ? fieldError(fieldErrors, fieldKey) : undefined;
  const valueAtFocus = useRef<string>("");

  const normalizeInput = (raw: string) =>
    type === "number" ? (raw === "" ? "0" : String(Number(raw))) : raw;

  const labelClass = [className, err ? "field-has-error" : undefined].filter(Boolean).join(" ") || undefined;

  return (
    <label className={labelClass}>
      {label}
      <input
        type={type}
        value={value}
        disabled={disabled}
        aria-invalid={err ? true : undefined}
        aria-describedby={err ? `${fieldKey}-error` : undefined}
        className={composeFieldClass(fieldKey, {
          validationError: Boolean(err),
          fieldSyncPulse,
        })}
        onChange={(e) => onChange(e.target.value)}
        onFocus={(e) => {
          valueAtFocus.current = normalizeInput(e.target.value);
        }}
        onBlur={(e) => {
          if (!fieldKey || !onFieldBlur) return;
          const raw = e.target.value;
          const normalized = normalizeInput(raw);
          if (normalized === valueAtFocus.current) return;
          onFieldBlur(
            fieldKey,
            type === "number" ? (raw === "" ? 0 : Number(raw)) : raw,
          );
        }}
        onAnimationEnd={(e) => fieldKey && handleFieldPulseAnimationEnd(e, fieldKey, onFieldPulseEnd)}
      />
      {err && (
        <span id={`${fieldKey}-error`} className="field-error-msg" role="alert">
          {err}
        </span>
      )}
    </label>
  );
}

export function ClienteSection({
  payload,
  onChange,
  disabled,
  fieldErrors,
  onFieldBlur,
  onSyncPipeFields,
  onPersistDraft,
  fieldSyncPulse,
  onFieldPulseEnd,
}: SectionProps) {
  const c = payload.cliente;
  const set = (key: keyof typeof c, value: string) =>
    onChange({ ...payload, cliente: { ...c, [key]: value } });

  const syncProps = { fieldSyncPulse, onFieldPulseEnd };

  return (
    <section className="form-section" aria-labelledby="sec-cliente">
      <h2 id="sec-cliente">Cliente</h2>
      <div className="form-field-group">
        <h3 className="form-field-group-title">Identificação</h3>
        <div className="field-grid field-grid-cliente-identificacao">
          <Field fieldKey="cliente.contratante" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Contratante" value={c.contratante} disabled={disabled} onChange={(v) => set("contratante", v)} {...syncProps} />
          <Field fieldKey="cliente.documento" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="CPF/CNPJ" value={c.documento} disabled={disabled} onChange={(v) => set("documento", v)} {...syncProps} />
          <CodigoClienteField
            value={c.codigo_cliente_instalacao}
            disabled={disabled}
            fieldErrors={fieldErrors}
            payload={payload}
            onChange={onChange}
            onSyncPipeFields={onSyncPipeFields}
            onPersistDraft={onPersistDraft}
            fieldSyncPulse={fieldSyncPulse}
            onFieldPulseEnd={onFieldPulseEnd}
          />
        </div>
      </div>
      <div className="form-field-group">
        <h3 className="form-field-group-title">Localização</h3>
        <div className="field-grid field-grid-cliente-localizacao">
          <MunicipioEstadoFields
            value={c.municipio_estado}
            disabled={disabled}
            fieldErrors={fieldErrors}
            onChange={(v) => set("municipio_estado", v)}
            onFieldBlur={onFieldBlur}
            fieldSyncPulse={fieldSyncPulse}
            onFieldPulseEnd={onFieldPulseEnd}
          />
          <Field
            fieldKey="cliente.cep"
            className="field-localizacao-cep"
            fieldErrors={fieldErrors}
            onFieldBlur={onFieldBlur}
            label="CEP"
            value={c.cep}
            disabled={disabled}
            onChange={(v) => set("cep", v)}
            {...syncProps}
          />
          <label className={fieldError(fieldErrors, "cliente.endereco") ? "field-has-error field-span-all" : "field-span-all"}>
            Endereço
            <BlurGuardInput
              fieldPath="cliente.endereco"
              value={c.endereco}
              disabled={disabled}
              ariaInvalid={fieldError(fieldErrors, "cliente.endereco") ? true : undefined}
              className={composeFieldClass("cliente.endereco", {
                validationError: Boolean(fieldError(fieldErrors, "cliente.endereco")),
                fieldSyncPulse,
              })}
              onChange={(v) => set("endereco", v)}
              onFieldBlur={onFieldBlur}
              onFieldPulseEnd={onFieldPulseEnd}
            />
            {fieldError(fieldErrors, "cliente.endereco") && (
              <span className="field-error-msg" role="alert">{fieldError(fieldErrors, "cliente.endereco")}</span>
            )}
          </label>
        </div>
      </div>
      <div className="form-field-group">
        <h3 className="form-field-group-title">Fiscal e observações</h3>
        <div className="field-grid field-grid-cliente-fiscal">
          <Field fieldKey="cliente.inscricao_estadual" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Inscrição estadual" value={c.inscricao_estadual} disabled={disabled} onChange={(v) => set("inscricao_estadual", v)} {...syncProps} />
          <Field fieldKey="cliente.inscricao_municipal" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Inscrição municipal" value={c.inscricao_municipal} disabled={disabled} onChange={(v) => set("inscricao_municipal", v)} {...syncProps} />
          <label className={fieldError(fieldErrors, "cliente.notas") ? "field-has-error field-span-all" : "field-span-all"}>
            Notas
            <BlurGuardTextarea
              fieldPath="cliente.notas"
              value={c.notas}
              disabled={disabled}
              className={composeFieldClass("cliente.notas", {
                validationError: Boolean(fieldError(fieldErrors, "cliente.notas")),
                fieldSyncPulse,
              })}
              onChange={(v) => set("notas", v)}
              onFieldBlur={onFieldBlur}
              onFieldPulseEnd={onFieldPulseEnd}
            />
            {fieldError(fieldErrors, "cliente.notas") && (
              <span className="field-error-msg" role="alert">{fieldError(fieldErrors, "cliente.notas")}</span>
            )}
          </label>
        </div>
      </div>
    </section>
  );
}

function CodigoClienteField({
  value,
  disabled,
  fieldErrors,
  payload,
  onChange,
  onSyncPipeFields,
  onPersistDraft,
  fieldSyncPulse,
  onFieldPulseEnd,
}: {
  value: string;
  disabled?: boolean;
  fieldErrors?: Record<string, string>;
  payload: FormPayloadV1;
  onChange: (next: FormPayloadV1) => void;
  onSyncPipeFields?: (fields: PipeFieldSync[]) => Promise<void>;
  onPersistDraft?: (payload: FormPayloadV1) => Promise<void>;
  fieldSyncPulse?: Set<string>;
  onFieldPulseEnd?: (fieldPath: string) => void;
}) {
  const fieldKey = "cliente.codigo_cliente_instalacao";
  const err = fieldError(fieldErrors, fieldKey);
  const [draft, setDraft] = useState(() => codigoClienteOnly(value));
  const [loading, setLoading] = useState(false);
  const [hubError, setHubError] = useState("");
  const valueAtFocus = useRef(draft);

  useEffect(() => {
    setDraft(codigoClienteOnly(value));
  }, [value]);

  const loadHub = async (codigoCliente: number) => {
    setLoading(true);
    setHubError("");
    try {
      const hub = await api.getHubInstalacoes(String(codigoCliente));
      const next = mergeHubInstalacoes(payload, hub.instalacoes, codigoCliente);
      onChange(next);
      await onPersistDraft?.(next);
      await onSyncPipeFields?.(pipeFieldsFromUcMatrix(next));
    } catch (e) {
      setHubError(e instanceof Error ? e.message : "Erro ao carregar instalações HUB");
    } finally {
      setLoading(false);
    }
  };

  return (
    <label className={err ? "field-has-error" : undefined}>
      Código cliente HUB
      <input
        type="text"
        inputMode="numeric"
        value={draft}
        disabled={disabled || loading}
        aria-invalid={err ? true : undefined}
        className={composeFieldClass(fieldKey, {
          validationError: Boolean(err),
          fieldSyncPulse,
        })}
        onFocus={() => {
          valueAtFocus.current = draft;
        }}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={async () => {
          const trimmed = draft.trim();
          if (trimmed === valueAtFocus.current.trim()) return;
          const codigo = Number(trimmed);
          if (!Number.isFinite(codigo) || codigo <= 0) {
            setHubError("Informe um código de cliente numérico.");
            return;
          }
          await loadHub(codigo);
        }}
        onAnimationEnd={(e) => handleFieldPulseAnimationEnd(e, fieldKey, onFieldPulseEnd)}
      />
      {loading && <span className="field-hint">Carregando instalações do HUB…</span>}
      {hubError && (
        <span className="field-error-msg" role="alert">
          {hubError}
        </span>
      )}
      {err && (
        <span className="field-error-msg" role="alert">
          {err}
        </span>
      )}
      {value && value.includes("/") && (
        <span className="field-hint">Pipe: {value}</span>
      )}
    </label>
  );
}

function UcServicoCelulaField({
  celula,
  label,
  disabled,
  onToggle,
  onValorCommit,
}: {
  celula: HubServicoItem;
  label: string;
  disabled?: boolean;
  onToggle: () => void;
  onValorCommit: (valor: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const valueAtFocus = useRef("");

  const shown = editing ? draft : formatMoneyBr(celula.valor);

  return (
    <div className="uc-servico-celula">
      <label className="uc-servico-check">
        <input type="checkbox" checked={celula.ativo} disabled={disabled} onChange={onToggle} />
        <span className="sr-only">{label}</span>
      </label>
      <input
        type="text"
        inputMode="decimal"
        className="uc-servico-valor"
        value={shown}
        disabled={disabled || !celula.ativo}
        aria-label={`Valor ${label}`}
        onFocus={() => {
          valueAtFocus.current = moneyToStorage(celula.valor);
          setDraft(formatMoneyBr(celula.valor) || moneyToStorage(celula.valor));
          setEditing(true);
        }}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={() => {
          setEditing(false);
          const parsed = parseMoneyBr(draft);
          const stored = parsed !== null ? moneyToStorage(parsed) : moneyToStorage(celula.valor);
          if (stored !== valueAtFocus.current) onValorCommit(stored);
        }}
      />
    </div>
  );
}

export function ServicosSection({
  payload,
  onChange,
  disabled,
  fieldErrors,
  onSyncPipeFields,
  onPersistDraft,
  fieldSyncPulse,
}: SectionProps) {
  const [catalogo, setCatalogo] = useState<HubServicoCatalogo[]>(HUB_SERVICOS_CATALOGO_FALLBACK);
  const colunas = catalogoOrdenado(catalogo);
  const instalacoes = getHubInstalacoes(payload, colunas);
  const { codigoCliente } = parseCodigoClienteInstalacao(payload.cliente.codigo_cliente_instalacao);
  const [loading, setLoading] = useState(false);
  const [hubError, setHubError] = useState("");
  const bootstrapped = useRef(false);
  const totalHub = somaValoresHub(instalacoes);
  const ucsAtivas = countUcsAtivas(instalacoes);

  useEffect(() => {
    api.getHubServicos().then((r) => setCatalogo(r.servicos)).catch(() => {});
  }, []);

  useEffect(() => {
    if (bootstrapped.current || !codigoCliente || instalacoes.length > 0) return;
    bootstrapped.current = true;
    setLoading(true);
    api
      .getHubInstalacoes(String(codigoCliente))
      .then((hub) => {
        onChange(mergeHubInstalacoes(payload, hub.instalacoes, codigoCliente, colunas));
      })
      .catch((e: unknown) => {
        setHubError(e instanceof Error ? e.message : "Erro ao carregar instalações");
      })
      .finally(() => setLoading(false));
  }, [codigoCliente, colunas, instalacoes.length, onChange, payload]);

  const commitMatrix = async (nextInstalacoes: HubInstalacaoPedido[]) => {
    if (!codigoCliente) return;
    const next = applyHubInstalacoes(payload, nextInstalacoes, codigoCliente, colunas);
    onChange(next);
    await onPersistDraft?.(next);
    await onSyncPipeFields?.(pipeFieldsFromUcMatrix(next));
  };

  const updateCelula = (
    rowIndex: number,
    svcIndex: number,
    patch: Partial<HubServicoItem>,
  ) =>
    instalacoes.map((inst, idx) =>
      idx === rowIndex
        ? {
            ...inst,
            servicos: inst.servicos.map((svc, j) =>
              j === svcIndex ? { ...svc, ...patch } : svc,
            ),
          }
        : inst,
    );

  return (
    <section className="form-section" aria-labelledby="sec-servicos">
      <h2 id="sec-servicos">UC × serviço × valor</h2>
      <p className="field-hint">
        Marque o serviço e informe o valor (R$) por UC. No HUB, o valor por UC é a soma dos
        serviços (pedido_instalacao_extra); os códigos de serviço vão em
        pedido_instalacao_servico. Só o código cliente/instalação sincroniza no Pipedrive em tempo
        real.
      </p>
      {hubError && <div className="alert error">{hubError}</div>}
      {loading && <p className="muted">Carregando instalações…</p>}
      {!codigoCliente && !loading && (
        <p className="muted">Informe o código cliente na seção Cliente para listar as UCs.</p>
      )}
      {codigoCliente && instalacoes.length > 0 && (
        <>
          <div className="uc-servicos-wrap">
            <table className="uc-servicos-table">
              <thead>
                <tr>
                  <th scope="col" className="uc-sticky uc-sticky-1 uc-col-uc">Cód. instalação</th>
                  <th scope="col" className="uc-sticky uc-sticky-2 uc-col-id">UC</th>
                  <th scope="col" className="uc-sticky uc-sticky-3 uc-col-local">Local</th>
                  {colunas.map((col) => (
                    <th key={col.chave} scope="col" className="uc-servicos-th-check">
                      <span className="uc-servico-header">
                        <span className="uc-servico-nome">{col.nome}</span>
                        <span className="uc-servico-sigla">{col.sigla}</span>
                      </span>
                    </th>
                  ))}
                  <th scope="col" className="uc-servicos-th-total" title="Soma dos serviços por UC">
                    Σ UC
                  </th>
                </tr>
              </thead>
              <tbody>
                {instalacoes.map((inst, rowIndex) => {
                  const somaUc = valorUcInstalacao(inst);
                  const identDisplay = inst.identificacao
                    ? formatDisplayName(inst.identificacao)
                    : "—";
                  return (
                    <tr key={inst.codigo_instalacao}>
                      <td className="uc-sticky uc-sticky-1 uc-col-uc">
                        <strong>{inst.codigo_instalacao}</strong>
                      </td>
                      <td className="uc-sticky uc-sticky-2 uc-col-id">{identDisplay}</td>
                      <td className="uc-sticky uc-sticky-3 uc-col-local">
                        {[inst.cidade, inst.uf].filter(Boolean).join(" / ") || "—"}
                      </td>
                      {inst.servicos.map((svc, svcIndex) => (
                        <td key={svc.chave} className="uc-servicos-td-check">
                          <UcServicoCelulaField
                            celula={svc}
                            label={`${svc.nome} — UC ${inst.codigo_instalacao}`}
                            disabled={disabled}
                            onToggle={() => {
                              const ativo = !svc.ativo;
                              void commitMatrix(
                                updateCelula(rowIndex, svcIndex, {
                                  ativo,
                                  valor: ativo ? svc.valor : "",
                                }),
                              );
                            }}
                            onValorCommit={(valor) => {
                              void commitMatrix(
                                updateCelula(rowIndex, svcIndex, {
                                  ativo: true,
                                  valor,
                                }),
                              );
                            }}
                          />
                        </td>
                      ))}
                      <td className="uc-servicos-total">
                        {somaUc > 0 ? formatMoneyBr(somaUc) : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr className="uc-servicos-foot-row">
                  <th scope="row" colSpan={3} className="uc-sticky uc-sticky-1 uc-foot-label">
                    Σ por serviço
                  </th>
                  {colunas.map((col) => (
                    <td key={col.chave} className="uc-servicos-total">
                      {formatMoneyBr(sumColunaServico(instalacoes, col.chave)) || "—"}
                    </td>
                  ))}
                  <td className="uc-servicos-th-total" />
                </tr>
                <tr className="uc-servicos-foot-row uc-servicos-foot-summary">
                  <th scope="row" colSpan={3} className="uc-sticky uc-sticky-1 uc-foot-label">
                    Resumo pedido
                  </th>
                  {colunas.map((col) => (
                    <td key={col.chave} className="uc-servicos-foot-empty" aria-hidden="true" />
                  ))}
                  <td className="uc-servicos-th-total uc-servicos-summary">
                    <span>{ucsAtivas} UC&apos;s ativas</span>
                    <span className="uc-summary-sep" aria-hidden="true">·</span>
                    <span>{formatMoneyBr(totalHub) || "R$ 0,00"}</span>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
          {(buildObservacoesDetalhesHub(instalacoes) || payload.hub.observacoes_detalhes) && (
            <label className="uc-hub-preview" style={{ marginTop: "0.75rem" }}>
              Observações (Detalhes) — preview HUB
              <textarea
                readOnly
                value={buildObservacoesDetalhesHub(instalacoes)}
                className={composeFieldClass("hub.observacoes_detalhes", { fieldSyncPulse })}
                rows={3}
              />
              {fieldError(fieldErrors, "hub.observacoes_detalhes") && (
                <span className="field-error-msg" role="alert">
                  {fieldError(fieldErrors, "hub.observacoes_detalhes")}
                </span>
              )}
            </label>
          )}
        </>
      )}
    </section>
  );
}

export function ValoresDatasSection({ payload, onChange, disabled, fieldErrors, onFieldBlur, fieldSyncPulse, onFieldPulseEnd }: SectionProps) {
  const v = payload.valores;
  const d = payload.datas;
  const syncProps = { fieldSyncPulse, onFieldPulseEnd };
  return (
    <section className="form-section" aria-labelledby="sec-valores">
      <h2 id="sec-valores">Valores e datas</h2>
      <div className="field-grid">
        <MoneyField fieldKey="valores.valor_recorrencia" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Valor recorrência" value={v.valor_recorrencia} disabled={disabled} onChange={(val) => onChange({ ...payload, valores: { ...v, valor_recorrencia: val } })} {...syncProps} />
        <MoneyField fieldKey="valores.valor_implantacao" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Valor implantação" value={v.valor_implantacao} disabled={disabled} onChange={(val) => onChange({ ...payload, valores: { ...v, valor_implantacao: val } })} {...syncProps} />
        <Field fieldKey="datas.data_pagamento_implantacao" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Data pag. implantação" type="date" value={d.data_pagamento_implantacao} disabled={disabled} onChange={(val) => onChange({ ...payload, datas: { ...d, data_pagamento_implantacao: val } })} {...syncProps} />
        <Field fieldKey="datas.data_primeira_cobranca" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Data 1ª cobrança mensal" type="date" value={d.data_primeira_cobranca} disabled={disabled} onChange={(val) => onChange({ ...payload, datas: { ...d, data_primeira_cobranca: val } })} {...syncProps} />
      </div>
    </section>
  );
}

export function ComercialSection({ payload, onChange, disabled, fieldErrors, onFieldBlur, fieldSyncPulse, onFieldPulseEnd }: SectionProps) {
  const c = payload.comercial;
  const set = (key: keyof typeof c, value: string) =>
    onChange({ ...payload, comercial: { ...c, [key]: value } });
  const syncProps = { fieldSyncPulse, onFieldPulseEnd };
  return (
    <section className="form-section" aria-labelledby="sec-comercial">
      <h2 id="sec-comercial">Comercial</h2>
      <div className="field-grid">
        <Field fieldKey="comercial.filial" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Filial" value={c.filial} disabled={disabled} onChange={(v) => set("filial", v)} {...syncProps} />
        <Field fieldKey="comercial.regional" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Regional" value={c.regional} disabled={disabled} onChange={(v) => set("regional", v)} {...syncProps} />
        <Field fieldKey="comercial.consultor" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Consultor" value={c.consultor} disabled={disabled} onChange={(v) => set("consultor", v)} {...syncProps} />
        <Field fieldKey="comercial.percentual_exito" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Porcentagem de êxito" value={c.percentual_exito} disabled={disabled} onChange={(v) => set("percentual_exito", v)} {...syncProps} />
      </div>
    </section>
  );
}

export function SignatariosSection({ payload, onChange, disabled, fieldErrors, onFieldBlur, fieldSyncPulse, onFieldPulseEnd }: SectionProps) {
  const s = payload.signatarios;
  const set = (key: keyof typeof s, value: string) =>
    onChange({ ...payload, signatarios: { ...s, [key]: value } });
  const fields: { key: keyof typeof s; label: string; fieldKey: string }[] = [
    { key: "email_assinante_contrato", label: "E-mail assinante contrato", fieldKey: "signatarios.email_assinante_contrato" },
    { key: "email_consultor_gebras", label: "E-mail consultor Gebras", fieldKey: "signatarios.email_consultor_gebras" },
    { key: "email_coordenador_gebras", label: "E-mail coordenador Gebras", fieldKey: "signatarios.email_coordenador_gebras" },
    { key: "email_diretor_gebras", label: "E-mail diretor Gebras", fieldKey: "signatarios.email_diretor_gebras" },
    { key: "email_financeiro_contratante", label: "E-mail financeiro contratante", fieldKey: "signatarios.email_financeiro_contratante" },
    { key: "email_gestor_contratante", label: "E-mail gestor contratante", fieldKey: "signatarios.email_gestor_contratante" },
  ];
  return (
    <section className="form-section" aria-labelledby="sec-signatarios">
      <h2 id="sec-signatarios">Signatários</h2>
      <div className="field-grid">
        {fields.map(({ key, label, fieldKey }) => (
          <Field
            key={key}
            fieldKey={fieldKey}
            fieldErrors={fieldErrors}
            fieldSyncPulse={fieldSyncPulse}
            onFieldBlur={onFieldBlur}
            onFieldPulseEnd={onFieldPulseEnd}
            label={label}
            type="email"
            value={s[key]}
            disabled={disabled}
            onChange={(v) => set(key, v)}
          />
        ))}
      </div>
    </section>
  );
}

export function HubSection({ payload, onChange, disabled, fieldErrors, onFieldBlur, fieldSyncPulse, onFieldPulseEnd }: SectionProps) {
  const err = fieldError(fieldErrors, "hub.observacoes_detalhes");
  return (
    <section className="form-section" aria-labelledby="sec-hub">
      <h2 id="sec-hub">HUB — Observações (detalhes)</h2>
      <label className={err ? "field-has-error" : undefined}>
        Blocos UC (formato HUB)
        <BlurGuardTextarea
          fieldPath="hub.observacoes_detalhes"
          value={payload.hub.observacoes_detalhes}
          disabled={disabled}
          className={composeFieldClass("hub.observacoes_detalhes", {
            validationError: Boolean(err),
            fieldSyncPulse,
          })}
          onChange={(v) =>
            onChange({
              ...payload,
              hub: { ...payload.hub, observacoes_detalhes: v },
            })
          }
          onFieldBlur={onFieldBlur}
          onFieldPulseEnd={onFieldPulseEnd}
        />
        {err && <span className="field-error-msg" role="alert">{err}</span>}
      </label>
    </section>
  );
}
