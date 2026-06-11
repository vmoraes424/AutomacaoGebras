import { useCallback, useEffect, useMemo, useState } from "react";
import { flushSync } from "react-dom";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { FormAttachmentsMeta, FormPayloadV1, FormReadiness } from "../api/types";
import {
  ClienteSection,
  ComercialSection,
  HubSection,
  ServicosSection,
  SignatariosSection,
  ValoresDatasSection,
  type PipeFieldSync,
} from "../components/FormFields";
import { FormPageAside } from "../components/FormPageAside";
import { GebrasLoader } from "../components/GebrasLoader";
import { SyncToastStack, useSyncToasts } from "../components/SyncToast";
import { isPipeField } from "../constants/pipeFields";
import { labelForFieldPath } from "../constants/fieldLabels";
import { mergeFormPayloadV1 } from "../schemas/formV1";
import { useOwnerName } from "../hooks/useOwnerName";
import { formatDisplayName } from "../utils/formatDisplayName";
import {
  DEAL_LABEL_TEXT,
  formStatusToOperationalLabel,
} from "../utils/dealCard";
import { mergeReadinessWithAttachments } from "../utils/readinessMerge";

export function DealFormPage() {
  const { ownerId, dealId } = useParams<{ ownerId: string; dealId: string }>();
  const location = useLocation();
  const navState = location.state as { ownerName?: string; dealTitle?: string } | null;
  const ownerNameFromNav = navState?.ownerName ?? "";
  const dealTitle = navState?.dealTitle ?? "";
  const ownerUserId = Number(ownerId);
  const ownerName = useOwnerName(ownerUserId, ownerNameFromNav);
  const dealIdNum = Number(dealId);

  const [payload, setPayload] = useState<FormPayloadV1>(() => mergeFormPayloadV1(undefined));
  const [status, setStatus] = useState<string>("");
  const [validationErrors, setValidationErrors] = useState<Record<string, string> | null>(null);
  const [fieldSyncPulse, setFieldSyncPulse] = useState<Set<string>>(() => new Set());
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [readiness, setReadiness] = useState<FormReadiness | null>(null);
  const [readinessLoading, setReadinessLoading] = useState(false);
  const [attachments, setAttachments] = useState<FormAttachmentsMeta | null>(null);
  const [attachmentsLoading, setAttachmentsLoading] = useState(true);
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

  useEffect(() => {
    if (loading) return;
    let active = true;
    setAttachmentsLoading(true);
    api
      .getFormAttachments(dealIdNum, { fresh: false })
      .then((meta) => {
        if (active) setAttachments(meta);
      })
      .catch(() => {
        if (active) setAttachments(null);
      })
      .finally(() => {
        if (active) setAttachmentsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [dealIdNum, loading]);

  const body = () => ({
    payload,
    schema_version: "v1" as const,
    owner_user_id: ownerUserId,
    owner_name: ownerName,
    deal_title: dealTitle,
  });

  useEffect(() => {
    if (loading) return;
    let active = true;
    setReadinessLoading(true);
    const timer = window.setTimeout(() => {
      api
        .getFormReadiness(dealIdNum, body())
        .then((result) => {
          if (active) setReadiness(result);
        })
        .catch(() => {
          if (active) setReadiness(null);
        })
        .finally(() => {
          if (active) setReadinessLoading(false);
        });
    }, 300);
    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [payload, dealIdNum, ownerUserId, ownerName, dealTitle, loading]);

  const displayReadiness = useMemo(
    () =>
      readiness
        ? mergeReadinessWithAttachments(
            readiness,
            attachments,
            attachmentsLoading,
            Boolean(payload.anexos?.proposta_comercial_anexada),
          )
        : null,
    [readiness, attachments, attachmentsLoading, payload.anexos?.proposta_comercial_anexada],
  );

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

  const syncMeta = useCallback(
    () => ({
      owner_user_id: ownerUserId,
      owner_name: ownerName,
      deal_title: dealTitle,
    }),
    [ownerUserId, ownerName, dealTitle],
  );

  const handleFieldBlur = useCallback(
    async (fieldPath: string, value: string | number) => {
      if (readOnly || !isPipeField(fieldPath)) return;
      try {
        await api.syncFieldToPipedrive(dealIdNum, fieldPath, value, syncMeta());
        triggerFieldPulse(fieldPath);
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Erro ao sincronizar campo";
        addToast(labelForFieldPath(fieldPath), msg);
      }
    },
    [dealIdNum, readOnly, addToast, triggerFieldPulse, syncMeta],
  );

  const persistDraftQuiet = useCallback(
    async (nextPayload: FormPayloadV1) => {
      if (readOnly) return;
      try {
        await api.saveDraft(dealIdNum, {
          payload: nextPayload,
          schema_version: "v1",
          owner_user_id: ownerUserId,
          owner_name: ownerName,
          deal_title: dealTitle,
        });
      } catch {
        /* rascunho HUB; falha silenciosa — usuário pode salvar manualmente */
      }
    },
    [dealIdNum, readOnly, ownerUserId, ownerName, dealTitle],
  );

  const handleSyncPipeFields = useCallback(
    async (fields: PipeFieldSync[]) => {
      if (readOnly) return;
      for (const { path, value } of fields) {
        if (!isPipeField(path)) continue;
        try {
          await api.syncFieldToPipedrive(dealIdNum, path, value, syncMeta());
          triggerFieldPulse(path);
        } catch (e) {
          const msg = e instanceof Error ? e.message : "Erro ao sincronizar campo";
          addToast(labelForFieldPath(path), msg);
          break;
        }
      }
    },
    [dealIdNum, readOnly, addToast, triggerFieldPulse, syncMeta],
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
    onSyncPipeFields: handleSyncPipeFields,
    onPersistDraft: persistDraftQuiet,
    fieldSyncPulse,
    onFieldPulseEnd: clearFieldPulse,
  };

  if (loading) {
    return <GebrasLoader variant="form" label="Carregando formulário…" />;
  }

  const statusLabel = status ? formStatusToOperationalLabel(status) : null;
  const displayTitle = dealTitle ? formatDisplayName(dealTitle) : `Deal #${dealId}`;

  return (
    <div className="layout layout-form">
      <header className="form-page-header">
        <Link className="form-back-link" to={`/deals/${ownerId}`} state={{ ownerName }}>
          ← Voltar aos cards
        </Link>
        <div className="form-page-header-top">
          <span className="form-deal-id">#{dealId}</span>
          {statusLabel && (
            <span className={`badge badge-${statusLabel}`}>{DEAL_LABEL_TEXT[statusLabel]}</span>
          )}
        </div>
        <h1>{displayTitle}</h1>
        <p className="form-page-subtitle">Formulário comercial</p>
        {!readOnly && (
          <p className="form-sync-hint">Campos do Pipe sincronizam ao sair do input</p>
        )}
      </header>

      <FormPageAside
        ownerName={ownerName}
        contratante={payload.cliente.contratante}
        readiness={displayReadiness}
        readinessLoading={readinessLoading && !readiness}
        attachmentsLoading={attachmentsLoading}
      />

      <div className="form-alerts">
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
      </div>

      <ClienteSection {...sectionProps} />
      <ServicosSection {...sectionProps} />
      <ValoresDatasSection {...sectionProps} />
      <ComercialSection {...sectionProps} />
      <SignatariosSection {...sectionProps} />
      <HubSection {...sectionProps} />

      <div className="form-actions-bar">
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
