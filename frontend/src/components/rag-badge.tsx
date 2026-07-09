import { cn } from "@/lib/utils";

type Status = string | null | undefined;

function normalize(s: Status): "red" | "amber" | "green" | "unknown" {
  const v = (s ?? "").toString().trim().toLowerCase();
  if (v === "red") return "red";
  if (v === "amber" || v === "yellow") return "amber";
  if (v === "green") return "green";
  return "unknown";
}

const styles = {
  red: "bg-rag-red text-rag-red-foreground",
  amber: "bg-rag-amber text-rag-amber-foreground",
  green: "bg-rag-green text-rag-green-foreground",
  unknown: "bg-muted text-muted-foreground",
} as const;

export function RagBadge({ status, className }: { status: Status; className?: string }) {
  const kind = normalize(status);
  const label = kind === "unknown" ? status || "Unknown" : kind.charAt(0).toUpperCase() + kind.slice(1);
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide",
        styles[kind],
        className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-90" />
      {label}
    </span>
  );
}

export function RagDot({ status, className }: { status: Status; className?: string }) {
  const kind = normalize(status);
  const c = {
    red: "bg-rag-red",
    amber: "bg-rag-amber",
    green: "bg-rag-green",
    unknown: "bg-muted-foreground/40",
  }[kind];
  return <span className={cn("inline-block h-2.5 w-2.5 rounded-full", c, className)} />;
}