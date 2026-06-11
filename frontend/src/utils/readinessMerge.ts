import type {
  FormAttachmentsMeta,
  FormReadiness,
  FormReadinessSection,
} from "../api/types";

const ANEXOS_SECTION: FormReadinessSection = {
  id: "anexos",
  label: "Anexos",
  completed: 0,
  total: 1,
  ready: false,
  loading: true,
  items: [
    {
      id: "anexos.proposta_comercial_anexada",
      label: "Proposta comercial (Pipedrive)",
      status: "pending",
      message: null,
    },
  ],
};

function recomputeSummary(sections: FormReadinessSection[]) {
  let completed = 0;
  let total = 0;
  for (const section of sections) {
    if (section.loading) continue;
    for (const item of section.items) {
      total += 1;
      if (item.status === "ok") completed += 1;
    }
  }
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
  return { completed, total, percent };
}

/** Une prontidão (payload) com metadados de anexos do Pipedrive. */
export function mergeReadinessWithAttachments(
  base: FormReadiness,
  attachments: FormAttachmentsMeta | null,
  attachmentsLoading: boolean,
  payloadPropostaFlag: boolean,
): FormReadiness {
  const withoutAnexos = base.sections.filter((s) => s.id !== "anexos");

  if (attachmentsLoading) {
    const sections = [...withoutAnexos, ANEXOS_SECTION];
    const summary = recomputeSummary(sections);
    return {
      ...base,
      sections,
      summary: { ...base.summary, ...summary },
      ready_to_submit: false,
      attachments_deferred: true,
    };
  }

  if (!attachments) {
    return { ...base, sections: withoutAnexos, attachments_deferred: true };
  }

  const propostaOk =
    attachments.proposta_comercial_anexada || payloadPropostaFlag;
  const anexosSection: FormReadinessSection = {
    id: "anexos",
    label: "Anexos",
    completed: propostaOk ? 1 : 0,
    total: 1,
    ready: propostaOk,
    items: [
      {
        id: "anexos.proposta_comercial_anexada",
        label: "Proposta comercial (Pipedrive)",
        status: propostaOk ? "ok" : attachments.error ? "error" : "pending",
        message: attachments.error ?? null,
      },
    ],
  };

  const sections = [...withoutAnexos, anexosSection];
  const summary = recomputeSummary(sections);
  const validation_errors = { ...base.validation_errors };
  if (propostaOk) {
    delete validation_errors["anexos.proposta_comercial_anexada"];
  }

  const ready_to_submit =
    Object.keys(validation_errors).length === 0 && propostaOk;

  return {
    ...base,
    sections,
    summary: {
      ...base.summary,
      ...summary,
      validation_error_count: Object.keys(validation_errors).length,
    },
    ready_to_submit,
    contrato: attachments.contrato,
    attachments: {
      proposta_comercial_anexada: attachments.proposta_comercial_anexada,
      error: attachments.error,
    },
    attachments_deferred: false,
    validation_errors,
  };
}
