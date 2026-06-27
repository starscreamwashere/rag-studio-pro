import { cn } from "@/lib/utils";

const VARIANTS = {
  neutral: "bg-surface-2 text-muted-foreground",
  success: "bg-[#e8f3ec] text-[#3f7d5a]",
  warning: "bg-[#fdf3e3] text-[#9a6b1e]",
  error: "bg-[#fce8e8] text-[#b04a4a]",
  info: "bg-[#eaf1fd] text-[#3f6fd1]",
} as const;

export type BadgeVariant = keyof typeof VARIANTS;

export function Badge({
  variant = "neutral",
  className,
  ...props
}: { variant?: BadgeVariant } & React.ComponentProps<"span">) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
        VARIANTS[variant],
        className,
      )}
      {...props}
    />
  );
}
