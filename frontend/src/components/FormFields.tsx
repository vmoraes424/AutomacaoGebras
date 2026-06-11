import type { FormPayloadV1 } from "../api/types";
import type { CSSProperties } from "react";
import { useRef, useState } from "react";
import { formatMoneyBr, moneyToStorage, parseMoneyBr } from "../utils/money";
import {
  composeFieldClass,
  fieldError,
  handleFieldPulseAnimationEnd,
  type FieldSyncUiProps,
} from "./formFieldSyncUi";

type SectionProps = {
  payload: FormPayloadV1;
  onChange: (next: FormPayloadV1) => void;
  disabled?: boolean;
  fieldErrors?: Record<string, string>;
  onFieldBlur?: (fieldPath: string, value: string | number) => void;
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
}) {
  const err = fieldKey ? fieldError(fieldErrors, fieldKey) : undefined;
  const valueAtFocus = useRef<string>("");

  const normalizeInput = (raw: string) =>
    type === "number" ? (raw === "" ? "0" : String(Number(raw))) : raw;

  return (
    <label className={err ? "field-has-error" : undefined}>
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
      <div className="field-grid">
        <Field fieldKey="cliente.contratante" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Contratante" value={c.contratante} disabled={disabled} onChange={(v) => set("contratante", v)} {...syncProps} />
        <Field fieldKey="cliente.documento" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="CPF/CNPJ" value={c.documento} disabled={disabled} onChange={(v) => set("documento", v)} {...syncProps} />
        <Field fieldKey="cliente.cep" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="CEP" value={c.cep} disabled={disabled} onChange={(v) => set("cep", v)} {...syncProps} />
        <Field fieldKey="cliente.municipio_estado" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Município/Estado" value={c.municipio_estado} disabled={disabled} onChange={(v) => set("municipio_estado", v)} {...syncProps} />
        <Field fieldKey="cliente.inscricao_estadual" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Inscrição estadual" value={c.inscricao_estadual} disabled={disabled} onChange={(v) => set("inscricao_estadual", v)} {...syncProps} />
        <Field fieldKey="cliente.inscricao_municipal" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Inscrição municipal" value={c.inscricao_municipal} disabled={disabled} onChange={(v) => set("inscricao_municipal", v)} {...syncProps} />
        <Field fieldKey="cliente.codigo_cliente_instalacao" fieldErrors={fieldErrors} onFieldBlur={onFieldBlur} label="Código cliente/instalação" value={c.codigo_cliente_instalacao} disabled={disabled} onChange={(v) => set("codigo_cliente_instalacao", v)} {...syncProps} />
      </div>
      <div className="field-grid" style={{ marginTop: "0.75rem" }}>
        <label className={fieldError(fieldErrors, "cliente.endereco") ? "field-has-error" : undefined} style={{ gridColumn: "1 / -1" }}>
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
        <label className={fieldError(fieldErrors, "cliente.notas") ? "field-has-error" : undefined} style={{ gridColumn: "1 / -1" }}>
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
    </section>
  );
}

export function ServicosSection({ payload, onChange, disabled, fieldErrors, onFieldBlur, fieldSyncPulse, onFieldPulseEnd }: SectionProps) {
  const s = payload.servicos;
  const setNum = (key: keyof typeof s, raw: string) =>
    onChange({
      ...payload,
      servicos: { ...s, [key]: raw === "" ? 0 : Number(raw) },
    });

  const fields: { key: keyof typeof s; label: string; fieldKey: string }[] = [
    { key: "sole_web", label: "SOLE Web", fieldKey: "servicos.sole_web" },
    { key: "sole_consultoria", label: "Sole Consultoria", fieldKey: "servicos.sole_consultoria" },
    { key: "gestao_acl", label: "Gestão ACL", fieldKey: "servicos.gestao_acl" },
    { key: "gestao_usina_fotovoltaica", label: "Gestão Usina FV", fieldKey: "servicos.gestao_usina_fotovoltaica" },
    { key: "gestao_qualidade_energia", label: "Gestão Qualidade Energia", fieldKey: "servicos.gestao_qualidade_energia" },
    { key: "quantidade_ucs", label: "Quantidade de UC's", fieldKey: "servicos.quantidade_ucs" },
  ];

  return (
    <section className="form-section" aria-labelledby="sec-servicos">
      <h2 id="sec-servicos">Serviços (UCs)</h2>
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
            type="number"
            value={s[key]}
            disabled={disabled}
            onChange={(v) => setNum(key, v)}
          />
        ))}
      </div>
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
