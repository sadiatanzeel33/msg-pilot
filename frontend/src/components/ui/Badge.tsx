import { cn } from "@/lib/utils";

const colors: Record<string, string> = {
  green: "bg-green-100 text-green-700",
  red: "bg-red-100 text-red-700",
  yellow: "bg-yellow-100 text-yellow-700",
  blue: "bg-blue-100 text-blue-700",
  gray: "bg-gray-100 text-gray-600",
};

export function Badge({ color = "gray", children }: { color?: string; children: React.ReactNode }) {
  return <span className={cn("px-2 py-0.5 rounded-full text-xs font-medium", colors[color] || colors.gray)}>{children}</span>;
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { color: string; label: string }> = {
    draft: { color: "gray", label: "Draft" },
    scheduled: { color: "blue", label: "Scheduled" },
    running: { color: "yellow", label: "Running" },
    paused: { color: "yellow", label: "Paused" },
    completed: { color: "green", label: "Completed" },
    stopped: { color: "red", label: "Stopped" },
    sent: { color: "green", label: "Sent" },
    failed: { color: "red", label: "Failed" },
    pending: { color: "gray", label: "Pending" },
    skipped: { color: "gray", label: "Skipped" },
  };
  const m = map[status] || { color: "gray", label: status };
  return <Badge color={m.color}>{m.label}</Badge>;
}
