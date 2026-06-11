import { useCallback, useEffect, useState } from "react";
import { flushSync } from "react-dom";
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
import { SyncToastStack, useSyncToasts } from "../components/SyncToast";
import { isPipeField } from "../constants/pipeFields";
import { labelForFieldPath } from "../constants/fieldLabels";
import { mergeFormPayloadV1 } from "../schemas/formV1";

export function DealFormPage() {
  const { ownerId, dealId } = useParams<{ ownerId: string; dealId: string }>();
  const location = useLocation();
  const navState = location.state as { ownerName?: string; dealTitle?: string } | null;
  const ownerName = navState?.ownerName ?? "";
  const dealTitle = navState?.dealTitle ?? "";
  const ownerUserId = Number(ownerId);
  const dealIdNum = Number(dealId);

  const [payload, setPayload] = useState<FormPayloadV1>(() => mergeFormPayloadV1(undefined));
  const [status, setStatus] = useState<string>("");
  const [validationErrors, setValidationErrors] = useState<Record<string, string> | null>(null);
  const [fieldSyncPulse, setFieldSyncPulse] = useState<Set<string>>(() => new Set());
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toasts, addToast, dismiss } = useSyncToasts();

  const readOnly = status === "submitted" || status === "validated" || status === "processing" || status === "processed";

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");

    api
      .getForm(dealIdNum, {
        ownerUserId,
        ownerName: ownerName || undefined,
        dealTitle: dealTitle || undefined,
      })
      .then((record) => {
        if (!active) return;
        setPayload(mergeFormPayloadV1(record.payload));
        setStatus(record.status);
        setValidationErrors(record.validation_errors ?? null);
      })
      .catch((e: unknown) => {
        if (!active) return;
        if (e instanceof Error && !e.message.includes("não encontrado")) {
          setError(e.message);
        }
        setStatus("draft");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [dealIdNum, ownerUserId]);

  const body = () => ({
    payload,
    schema_version: "v1" as const,
    owner_user_id: ownerUserId,
    owner_name: ownerName,
    deal_title: dealTitle,
  });

  const triggerFieldPulse = useCallback((fieldPath: string) => {
    // flushSync: pinta a animação no mesmo tick após o await (sem esperar frame extra).
    flushSync(() => {
      setFieldSyncPulse((prev) => {
        const next = new Set(prev);
        next.delete(fieldPath);
        return next;
      });
    });
    flushSync(() => {
      setFieldSyncPulse((prev) => {
        const next = new Set(prev);
        next.add(fieldPath);
        return next;
      });
    });
  }, []);

  const clearFieldPulse = useCallback((fieldPath: string) => {
    setFieldSyncPulse((prev) => {
      if (!prev.has(fieldPath)) return prev;
      const next = new Set(prev);
      next.delete(fieldPath);
      return next;
    });
  }, []);

  const handleFieldBlur = useCallback(
    async (fieldPath: string, value: string | number) => {
      if (readOnly || !isPipeField(fieldPath)) return;
      try {
        await api.syncFieldToPipedrive(dealIdNum, fieldPath, value, {
          owner_user_id: ownerUserId,
          owner_name: ownerName,
          deal_title: dealTitle,
        });
        triggerFieldPulse(fieldPath);
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Erro ao sincronizar campo";
        addToast(labelForFieldPath(fieldPath), msg);
      }
    },
    [dealIdNum, readOnly, addToast, triggerFieldPulse, ownerUserId, ownerName, dealTitle],
  );

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

  const handleSyncPipedrive = async () => {
    setSaving(true);
    setMessage("");
    setError("");
    setFieldSyncPulse(new Set());
    try {
      const result = await api.syncToPipedrive(dealIdNum, body());
      setMessage(result.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao sincronizar com o Pipedrive");
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

  const sectionProps = {
    payload,
    onChange: setPayload,
    disabled: readOnly,
    fieldErrors: validationErrors ?? undefined,
    onFieldBlur: handleFieldBlur,
    fieldSyncPulse,
    onFieldPulseEnd: clearFieldPulse,
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
        {dealTitle ? ` (${dealTitle})` : ""}
      </h1>
      <p className="muted">
        <Link to={`/deals/${ownerId}`} state={{ ownerName }}>
          ← Voltar aos cards
        </Link>
        {status && <> · Status: <strong>{status}</strong></>}
        {!readOnly && <> · Campos do Pipe sincronizam ao sair do input</>}
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

      <ClienteSection {...sectionProps} />
      <ServicosSection {...sectionProps} />
      <ValoresDatasSection {...sectionProps} />
      <ComercialSection {...sectionProps} />
      <SignatariosSection {...sectionProps} />
      <HubSection {...sectionProps} />

      <div className="actions">
        <button type="button" onClick={handleSaveDraft} disabled={saving || readOnly}>
          Salvar rascunho
        </button>
        <button
          type="button"
          className="sync-pipe"
          onClick={handleSyncPipedrive}
          disabled={saving || readOnly}
          title="Envia todos os campos mapeados ao Pipedrive"
        >
          Atualizar Pipedrive
        </button>
        <button type="button" className="secondary" onClick={handleSubmit} disabled={saving || readOnly}>
          Enviar formulário
        </button>
      </div>

      <SyncToastStack toasts={toasts} onDismiss={dismiss} />
    </div>
  );
}
