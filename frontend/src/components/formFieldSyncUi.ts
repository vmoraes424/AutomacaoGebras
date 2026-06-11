import type { AnimationEvent } from "react";

export type FieldSyncUiProps = {
  fieldSyncPulse?: Set<string>;
  onFieldPulseEnd?: (fieldPath: string) => void;
};

export function fieldError(
  errors: Record<string, string> | undefined,
  key: string,
): string | undefined {
  return errors?.[key];
}

export function composeFieldClass(
  fieldKey: string | undefined,
  opts: {
    validationError?: boolean;
    fieldSyncPulse?: Set<string>;
    extra?: string;
  },
): string | undefined {
  const parts: string[] = [];
  if (opts.extra) parts.push(opts.extra);
  if (opts.validationError) parts.push("field-error");
  if (fieldKey && opts.fieldSyncPulse?.has(fieldKey)) parts.push("field-sync-pulse");
  return parts.length > 0 ? parts.join(" ") : undefined;
}

export function handleFieldPulseAnimationEnd(
  event: AnimationEvent<HTMLInputElement | HTMLTextAreaElement>,
  fieldPath: string,
  onFieldPulseEnd?: (fieldPath: string) => void,
) {
  if (!event.animationName.includes("field-sync-pulse")) return;
  onFieldPulseEnd?.(fieldPath);
}
