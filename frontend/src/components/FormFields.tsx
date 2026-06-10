import type { FormPayloadV1 } from "../api/types";

type SectionProps = {
  payload: FormPayloadV1;
  onChange: (next: FormPayloadV1) => void;
  disabled?: boolean;
  fieldErrors?: Record<string, string>;
};

function fieldError(errors: Record<string, string> | undefined, key: string): string | undefined {
  return errors?.[key];
}

function Field({
  label,
  fieldKey,
  value,
  onChange,
  type = "text",
  disabled,
  fieldErrors,
}: {
  label: string;
  fieldKey?: string;
  value: string | number;
  onChange: (v: string) => void;
  type?: string;
  disabled?: boolean;
  fieldErrors?: Record<string, string>;
}) {
  const err = fieldKey ? fieldError(fieldErrors, fieldKey) : undefined;
  return (
    <label className={err ? "field-has-error" : undefined}>
      {label}
      <input
        type={type}
        value={value}
        disabled={disabled}
        aria-invalid={err ? true : undefined}
        aria-describedby={err ? `${fieldKey}-error` : undefined}
        className={err ? "field-error" : undefined}
        onChange={(e) => onChange(e.target.value)}
      />
      {err && (
        <span id={`${fieldKey}-error`} className="field-error-msg" role="alert">
          {err}
        </span>
      )}
    </label>
  );
}

export function ClienteSection({ payload, onChange, disabled, fieldErrors }: SectionProps) {
  const c = payload.cliente;
  const set = (key: keyof typeof c, value: string) =>
    onChange({ ...payload, cliente: { ...c, [key]: value } });

  return (
    <section className="form-section" aria-labelledby="sec-cliente">
      <h2 id="sec-cliente">Cliente</h2>
      <div className="field-grid">
        <Field fieldKey="cliente.contratante" fieldErrors={fieldErrors} label="Contratante" value={c.contratante} disabled={disabled} onChange={(v) => set("contratante", v)} />
        <Field fieldKey="cliente.documento" fieldErrors={fieldErrors} label="CPF/CNPJ" value={c.documento} disabled={disabled} onChange={(v) => set("documento", v)} />
        <Field fieldKey="cliente.cep" fieldErrors={fieldErrors} label="CEP" value={c.cep} disabled={disabled} onChange={(v) => set("cep", v)} />
        <Field fieldKey="cliente.municipio_estado" fieldErrors={fieldErrors} label="Município/Estado" value={c.municipio_estado} disabled={disabled} onChange={(v) => set("municipio_estado", v)} />
        <Field fieldKey="cliente.inscricao_estadual" fieldErrors={fieldErrors} label="Inscrição estadual" value={c.inscricao_estadual} disabled={disabled} onChange={(v) => set("inscricao_estadual", v)} />
        <Field fieldKey="cliente.inscricao_municipal" fieldErrors={fieldErrors} label="Inscrição municipal" value={c.inscricao_municipal} disabled={disabled} onChange={(v) => set("inscricao_municipal", v)} />
        <Field fieldKey="cliente.codigo_cliente_instalacao" fieldErrors={fieldErrors} label="Código cliente/instalação" value={c.codigo_cliente_instalacao} disabled={disabled} onChange={(v) => set("codigo_cliente_instalacao", v)} />
      </div>
      <div className="field-grid" style={{ marginTop: "0.75rem" }}>
        <label className={fieldError(fieldErrors, "cliente.endereco") ? "field-has-error" : undefined} style={{ gridColumn: "1 / -1" }}>
          Endereço
          <input
            value={c.endereco}
            disabled={disabled}
            aria-invalid={fieldError(fieldErrors, "cliente.endereco") ? true : undefined}
            className={fieldError(fieldErrors, "cliente.endereco") ? "field-error" : undefined}
            onChange={(e) => set("endereco", e.target.value)}
          />
          {fieldError(fieldErrors, "cliente.endereco") && (
            <span className="field-error-msg" role="alert">{fieldError(fieldErrors, "cliente.endereco")}</span>
          )}
        </label>
        <label className={fieldError(fieldErrors, "cliente.notas") ? "field-has-error" : undefined} style={{ gridColumn: "1 / -1" }}>
          Notas
          <textarea
            value={c.notas}
            disabled={disabled}
            className={fieldError(fieldErrors, "cliente.notas") ? "field-error" : undefined}
            onChange={(e) => set("notas", e.target.value)}
          />
          {fieldError(fieldErrors, "cliente.notas") && (
            <span className="field-error-msg" role="alert">{fieldError(fieldErrors, "cliente.notas")}</span>
          )}
        </label>
      </div>
    </section>
  );
}

export function ServicosSection({ payload, onChange, disabled, fieldErrors }: SectionProps) {
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

export function ValoresDatasSection({ payload, onChange, disabled, fieldErrors }: SectionProps) {
  const v = payload.valores;
  const d = payload.datas;
  return (
    <section className="form-section" aria-labelledby="sec-valores">
      <h2 id="sec-valores">Valores e datas</h2>
      <div className="field-grid">
        <Field
          fieldKey="valores.valor_recorrencia"
          fieldErrors={fieldErrors}
          label="Valor recorrência"
          value={v.valor_recorrencia}
          disabled={disabled}
          onChange={(val) => onChange({ ...payload, valores: { ...v, valor_recorrencia: val } })}
        />
        <Field
          fieldKey="valores.valor_implantacao"
          fieldErrors={fieldErrors}
          label="Valor implantação"
          value={v.valor_implantacao}
          disabled={disabled}
          onChange={(val) => onChange({ ...payload, valores: { ...v, valor_implantacao: val } })}
        />
        <Field
          fieldKey="datas.data_pagamento_implantacao"
          fieldErrors={fieldErrors}
          label="Data pag. implantação"
          type="date"
          value={d.data_pagamento_implantacao}
          disabled={disabled}
          onChange={(val) => onChange({ ...payload, datas: { ...d, data_pagamento_implantacao: val } })}
        />
        <Field
          fieldKey="datas.data_primeira_cobranca"
          fieldErrors={fieldErrors}
          label="Data 1ª cobrança mensal"
          type="date"
          value={d.data_primeira_cobranca}
          disabled={disabled}
          onChange={(val) => onChange({ ...payload, datas: { ...d, data_primeira_cobranca: val } })}
        />
      </div>
    </section>
  );
}

export function ComercialSection({ payload, onChange, disabled, fieldErrors }: SectionProps) {
  const c = payload.comercial;
  const set = (key: keyof typeof c, value: string) =>
    onChange({ ...payload, comercial: { ...c, [key]: value } });
  return (
    <section className="form-section" aria-labelledby="sec-comercial">
      <h2 id="sec-comercial">Comercial</h2>
      <div className="field-grid">
        <Field fieldKey="comercial.filial" fieldErrors={fieldErrors} label="Filial" value={c.filial} disabled={disabled} onChange={(v) => set("filial", v)} />
        <Field fieldKey="comercial.regional" fieldErrors={fieldErrors} label="Regional" value={c.regional} disabled={disabled} onChange={(v) => set("regional", v)} />
        <Field fieldKey="comercial.consultor" fieldErrors={fieldErrors} label="Consultor" value={c.consultor} disabled={disabled} onChange={(v) => set("consultor", v)} />
        <Field fieldKey="comercial.percentual_exito" fieldErrors={fieldErrors} label="Porcentagem de êxito" value={c.percentual_exito} disabled={disabled} onChange={(v) => set("percentual_exito", v)} />
      </div>
    </section>
  );
}

export function SignatariosSection({ payload, onChange, disabled, fieldErrors }: SectionProps) {
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

export function HubSection({ payload, onChange, disabled, fieldErrors }: SectionProps) {
  const err = fieldError(fieldErrors, "hub.observacoes_detalhes");
  return (
    <section className="form-section" aria-labelledby="sec-hub">
      <h2 id="sec-hub">HUB — Observações (detalhes)</h2>
      <label className={err ? "field-has-error" : undefined}>
        Blocos UC (formato HUB)
        <textarea
          value={payload.hub.observacoes_detalhes}
          disabled={disabled}
          aria-invalid={err ? true : undefined}
          className={err ? "field-error" : undefined}
          onChange={(e) =>
            onChange({
              ...payload,
              hub: { ...payload.hub, observacoes_detalhes: e.target.value },
            })
          }
        />
        {err && <span className="field-error-msg" role="alert">{err}</span>}
      </label>
    </section>
  );
}
