export type GebrasLoaderVariant = "default" | "inline" | "cards" | "consultants" | "form";

type GebrasLoaderProps = {
  label?: string;
  variant?: GebrasLoaderVariant;
  className?: string;
};

function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  return (
    <div
      className={`gebras-loader-spinner gebras-loader-spinner--${size}`}
      aria-hidden
    >
      <span className="gebras-loader-ring" />
    </div>
  );
}

function PageLoaderShell({ label, className }: { label: string; className?: string }) {
  return (
    <div
      className={["gebras-loader-screen", className].filter(Boolean).join(" ")}
      role="status"
      aria-live="polite"
      aria-label={label}
    >
      <div className="gebras-loader-screen-inner">
        <div className="gebras-loader-head gebras-loader-head--stacked">
          <Spinner size="lg" />
          <p className="gebras-loader-label gebras-loader-label--prominent">{label}</p>
        </div>
      </div>
    </div>
  );
}

export function GebrasLoader({
  label = "Carregando…",
  variant = "default",
  className,
}: GebrasLoaderProps) {
  const rootClass = ["gebras-loader", `gebras-loader--${variant}`, className]
    .filter(Boolean)
    .join(" ");

  if (variant === "inline") {
    return (
      <div className={rootClass} role="status" aria-live="polite" aria-label={label}>
        <Spinner size="sm" />
        {label && <p className="gebras-loader-label">{label}</p>}
      </div>
    );
  }

  return <PageLoaderShell label={label} className={className} />;
}
