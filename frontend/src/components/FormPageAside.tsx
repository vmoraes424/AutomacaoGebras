import { useEffect, useId, useState } from "react";
import type { FormReadiness, FormReadinessItem, FormReadinessSection } from "../api/types";
import { formatDisplayName } from "../utils/formatDisplayName";
import { GebrasLoader } from "./GebrasLoader";

type FormPageAsideProps = {
  ownerName: string;
  contratante: string;
  readiness: FormReadiness | null;
  readinessLoading: boolean;
  attachmentsLoading?: boolean;
};

type PendingItem = FormReadinessItem & { sectionLabel: string };

function countSectionPending(section: FormReadinessSection): number {
  return section.items.filter((item) => item.status === "pending" || item.status === "error").length;
}

function collectPendingItems(readiness: FormReadiness, sectionId?: string): PendingItem[] {
  const out: PendingItem[] = [];
  const sections = sectionId
    ? readiness.sections.filter((section) => section.id === sectionId)
    : readiness.sections;
  for (const section of sections) {
    for (const item of section.items) {
      if (item.status === "pending" || item.status === "error") {
        out.push({ ...item, sectionLabel: section.label });
      }
    }
  }
  return out;
}

type PendingModalFilter =
  | { mode: "all" }
  | { mode: "section"; sectionId: string; sectionLabel: string };

function PendingItemsModal({
  items,
  percent,
  sectionLabel,
  onClose,
}: {
  items: PendingItem[];
  percent: number;
  sectionLabel?: string;
  onClose: () => void;
}) {
  const titleId = useId();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  const grouped = items.reduce<Map<string, PendingItem[]>>((acc, item) => {
    const list = acc.get(item.sectionLabel) ?? [];
    list.push(item);
    acc.set(item.sectionLabel, list);
    return acc;
  }, new Map());

  return (
    <div className="readiness-modal-backdrop" onClick={onClose}>
      <div
        className="readiness-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="readiness-modal-header">
          <div>
            <h3 id={titleId} className="readiness-modal-title">
              {sectionLabel ? `O que falta em ${sectionLabel}` : "O que falta preencher"}
            </h3>
            <p className="readiness-modal-sub">
              {items.length} {items.length === 1 ? "campo pendente" : "campos pendentes"} · {percent}%
              concluído
            </p>
          </div>
          <button type="button" className="readiness-modal-close" onClick={onClose} aria-label="Fechar">
            ×
          </button>
        </header>

        <div className="readiness-modal-body">
          {[...grouped.entries()].map(([sectionLabel, sectionItems]) => (
            <section key={sectionLabel} className="readiness-modal-section">
              <h4 className="readiness-modal-section-title">{sectionLabel}</h4>
              <ul className="form-meta-pending-list">
                {sectionItems.map((item) => (
                  <li
                    key={item.id}
                    className={
                      item.status === "error"
                        ? "form-meta-pending-item form-meta-pending-item--error"
                        : "form-meta-pending-item"
                    }
                  >
                    <span className="form-meta-pending-field">{item.label}</span>
                    {item.message && (
                      <span className="form-meta-pending-hint">{item.message}</span>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}

export function FormPageAside({
  ownerName,
  contratante,
  readiness,
  readinessLoading,
  attachmentsLoading = false,
}: FormPageAsideProps) {
  const [pendingModal, setPendingModal] = useState<PendingModalFilter | null>(null);
  const displayOwner = ownerName ? formatDisplayName(ownerName) : "—";
  const displayCliente = contratante ? formatDisplayName(contratante) : "—";
  const percent = readiness?.summary.percent ?? 0;
  const pendingItems = readiness ? collectPendingItems(readiness) : [];
  const modalItems =
    readiness && pendingModal?.mode === "section"
      ? collectPendingItems(readiness, pendingModal.sectionId)
      : pendingItems;
  const hasPending = pendingItems.length > 0;
  const readyClass =
    readiness?.ready_to_submit
      ? "form-meta-readiness--ready"
      : percent >= 80
        ? "form-meta-readiness--almost"
        : "";

  useEffect(() => {
    if (!hasPending) setPendingModal(null);
  }, [hasPending]);

  const ringLabel = hasPending
    ? `${percent}% pronto. ${pendingItems.length} ${pendingItems.length === 1 ? "campo pendente" : "campos pendentes"}. Clique para ver detalhes.`
    : `${percent}% pronto${readiness?.ready_to_submit ? ". Pronto para enviar" : ""}`;

  return (
    <div className="form-page-meta" aria-label="Contexto e prontidão">
      <section className="form-meta-card form-meta-context">
        <h2 className="form-meta-card-title">Contexto do deal</h2>
        <div className="form-meta-context-grid">
          <div className="form-meta-kv">
            <span className="form-meta-kv-label">Consultor</span>
            <span className="form-meta-kv-value">{displayOwner}</span>
          </div>
          <div className="form-meta-kv">
            <span className="form-meta-kv-label">Contratante</span>
            <span className="form-meta-kv-value">{displayCliente}</span>
          </div>
          {readiness?.contrato && (
            <div className="form-meta-kv">
              <span className="form-meta-kv-label">Contrato</span>
              <span
                className={`form-meta-contrato-badge form-meta-contrato-badge--${readiness.contrato.source}`}
                title={
                  readiness.contrato.filename
                    ? `${readiness.contrato.source === "custom" ? "Contrato customizado" : "Modelo padrão Gebras"} · ${readiness.contrato.filename}`
                    : undefined
                }
              >
                {readiness.contrato.source === "custom" ? "Customizado" : "Padrão Gebras"}
              </span>
            </div>
          )}
        </div>
      </section>

      <section className={`form-meta-card form-meta-readiness ${readyClass}`.trim()}>
        <div className="form-meta-readiness-top">
          <div>
            <h2 className="form-meta-card-title">Prontidão para envio</h2>
            {readiness && (
              <p className="form-meta-readiness-sub">
                {readiness.summary.completed} de {readiness.summary.total} itens
                {readiness.ready_to_submit
                  ? " · pronto para enviar"
                  : hasPending
                    ? ` · falta ${pendingItems.length} ${pendingItems.length === 1 ? "campo" : "campos"}`
                    : ""}
              </p>
            )}
          </div>
          {readiness && !readinessLoading && (
            hasPending ? (
              <button
                type="button"
                className="form-meta-readiness-ring form-meta-readiness-ring-btn"
                onClick={() => setPendingModal({ mode: "all" })}
                aria-label={ringLabel}
                title="Ver o que falta preencher"
              >
                <span className="form-meta-readiness-percent" aria-hidden>
                  {percent}%
                </span>
              </button>
            ) : (
              <div className="form-meta-readiness-ring" aria-hidden>
                <span className="form-meta-readiness-percent">{percent}%</span>
              </div>
            )
          )}
        </div>

        {readinessLoading && !readiness && (
          <GebrasLoader variant="inline" label="Verificando campos…" />
        )}

        {readiness && (
          <>
            <div
              className="form-meta-readiness-bar"
              role="progressbar"
              aria-valuenow={percent}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Progresso de preenchimento"
            >
              <span className="form-meta-readiness-bar-fill" style={{ width: `${percent}%` }} />
            </div>

            {hasPending && (
              <button
                type="button"
                className="form-meta-readiness-link"
                onClick={() => setPendingModal({ mode: "all" })}
              >
                Ver o que falta preencher ({pendingItems.length})
              </button>
            )}

            <ul className="form-meta-section-chips">
              {readiness.sections.map((section) => {
                const sectionPending = countSectionPending(section);
                const chipClass = [
                  "form-meta-chip",
                  section.loading
                    ? "form-meta-chip--loading"
                    : section.ready
                      ? "form-meta-chip--ok"
                      : section.completed > 0
                        ? "form-meta-chip--partial"
                        : "",
                  sectionPending > 0 && !section.loading ? "form-meta-chip--clickable" : "",
                ]
                  .filter(Boolean)
                  .join(" ");

                const chipContent = (
                  <>
                    <span className="form-meta-chip-label">{section.label}</span>
                    <span className="form-meta-chip-count">
                      {section.loading ? "…" : `${section.completed}/${section.total}`}
                    </span>
                  </>
                );

                return (
                  <li key={section.id}>
                    {sectionPending > 0 && !section.loading ? (
                      <button
                        type="button"
                        className={chipClass}
                        onClick={() =>
                          setPendingModal({
                            mode: "section",
                            sectionId: section.id,
                            sectionLabel: section.label,
                          })
                        }
                        title={`Ver ${sectionPending} ${sectionPending === 1 ? "campo pendente" : "campos pendentes"} em ${section.label}`}
                        aria-label={`${section.label}: ${section.completed} de ${section.total} preenchidos. ${sectionPending} pendentes. Clique para ver.`}
                      >
                        {chipContent}
                      </button>
                    ) : (
                      <span className={chipClass} aria-label={`${section.label}: ${section.completed} de ${section.total}`}>
                        {chipContent}
                      </span>
                    )}
                  </li>
                );
              })}
            </ul>
            {attachmentsLoading && (
              <p className="form-meta-attachments-hint muted" aria-live="polite">
                Verificando anexos no Pipedrive…
              </p>
            )}
          </>
        )}
      </section>

      {pendingModal && modalItems.length > 0 && (
        <PendingItemsModal
          items={modalItems}
          percent={percent}
          sectionLabel={pendingModal.mode === "section" ? pendingModal.sectionLabel : undefined}
          onClose={() => setPendingModal(null)}
        />
      )}
    </div>
  );
}
