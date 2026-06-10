import { useCallback, useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { FormPayloadV1 } from "../api/types";
import {
  ClienteSection,
  ComercialSection,
  HubSection,
  ServicosSection,
  SignatariosSection,
  ValoresDatasSection,
} from "../components/FormFields";
import { mergeFormPayloadV1 } from "../schemas/formV1";

export function DealFormPage() {
  const { ownerId, dealId } = useParams<{ ownerId: string; dealId: string }>();
  const location = useLocation();
  const state = location.state as { ownerName?: string; dealTitle?: string } | null;
  const ownerUserId = Number(ownerId);
  const dealIdNum = Number(dealId);

  const [payload, setPayload] = useState<FormPayloadV1>(() => mergeFormPayloadV1(undefined));
  const [status, setStatus] = useState<string>("");
  const [validationErrors, setValidationErrors] = useState<Record<string, string> | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const readOnly = status === "submitted" || status === "validated" || status === "processing" || status === "processed";

  const loadForm = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const record = await api.getForm(dealIdNum, {
        ownerUserId: ownerUserId,
        ownerName: state?.ownerName,
        dealTitle: state?.dealTitle,
      });
      setPayload(mergeFormPayloadV1(record.payload));
      setStatus(record.status);
      setValidationErrors(record.validation_errors ?? null);
    } catch (e) {
      if (e instanceof Error && !e.message.includes("não encontrado")) {
        setError(e.message);
      }
      setStatus("draft");
    } finally {
      setLoading(false);
    }
  }, [dealIdNum]);

  useEffect(() => {
    loadForm();
  }, [loadForm]);

  const body = () => ({
    payload,
    schema_version: "v1" as const,
    owner_user_id: ownerUserId,
    owner_name: state?.ownerName ?? "",
    deal_title: state?.dealTitle ?? "",
  });

  const handleSaveDraft = async () => {
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const record = await api.saveDraft(dealIdNum, body());
      setStatus(record.status);
      setValidationErrors(null);
      setMessage("Rascunho salvo com sucesso.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao salvar");
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async () => {
    setSaving(true);
    setMessage("");
    setError("");
    setValidationErrors(null);
    try {
      const record = await api.submitForm(dealIdNum, body());
      setStatus(record.status);
      if (record.status === "error" && record.validation_errors) {
        setValidationErrors(record.validation_errors);
        setError("Formulário com erros de validação.");
      } else if (record.status === "validated" || record.status === "submitted") {
        setMessage("Formulário validado e enviado com sucesso.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao enviar");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="layout">
        <p>Carregando formulário…</p>
      </div>
    );
  }

  return (
    <div className="layout">
      <h1>
        Formulário — deal #{dealId}
        {state?.dealTitle ? ` (${state.dealTitle})` : ""}
      </h1>
      <p className="muted">
        <Link to={`/deals/${ownerId}`} state={{ ownerName: state?.ownerName }}>
          ← Voltar aos cards
        </Link>
        {status && <> · Status: <strong>{status}</strong></>}
      </p>

      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert error">{error}</div>}
      {validationErrors && Object.keys(validationErrors).length > 0 && (
        <div className="alert error" role="alert">
          Corrija os campos:
          <ul className="validation-list">
            {Object.entries(validationErrors).map(([k, v]) => (
              <li key={k}>
                <strong>{k}</strong>: {v}
              </li>
            ))}
          </ul>
        </div>
      )}
      {readOnly && (
        <div className="alert info">Este formulário já foi enviado e não pode mais ser editado.</div>
      )}

      <ClienteSection payload={payload} onChange={setPayload} disabled={readOnly} fieldErrors={validationErrors ?? undefined} />
      <ServicosSection payload={payload} onChange={setPayload} disabled={readOnly} fieldErrors={validationErrors ?? undefined} />
      <ValoresDatasSection payload={payload} onChange={setPayload} disabled={readOnly} fieldErrors={validationErrors ?? undefined} />
      <ComercialSection payload={payload} onChange={setPayload} disabled={readOnly} fieldErrors={validationErrors ?? undefined} />
      <SignatariosSection payload={payload} onChange={setPayload} disabled={readOnly} fieldErrors={validationErrors ?? undefined} />
      <HubSection payload={payload} onChange={setPayload} disabled={readOnly} fieldErrors={validationErrors ?? undefined} />

      <div className="actions">
        <button type="button" onClick={handleSaveDraft} disabled={saving || readOnly}>
          Salvar rascunho
        </button>
        <button type="button" className="secondary" onClick={handleSubmit} disabled={saving || readOnly}>
          Enviar formulário
        </button>
      </div>
    </div>
  );
}
