import { ChevronDownIcon, UpdateIcon } from "@radix-ui/react-icons";
import { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

function CountBadge({ count }: { count: number }) {
  return (
    <span className="inline-flex items-center justify-center bg-slate-600 text-white h-4 min-w-4 px-1 rounded-full text-xs tabular-nums">
      {count}
    </span>
  );
}

export function SelectTrigger({
  children,
  className,
  loading,
  count,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
  count?: number;
}) {
  return (
    <button
      role="combobox"
      className={cn(
        "cursor-pointer border-input [&_svg:not([class*='text-'])]:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 flex w-fit items-center justify-between gap-2 rounded-md border bg-white hover:bg-slate-50 aria-expanded:bg-slate-50 px-3 py-2 text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
        className,
      )}
      disabled={loading}
      {...props}
    >
      {children}
      {count !== undefined && count > 0 ? <CountBadge count={count} /> : null}
      {loading ? (
        <UpdateIcon className="animate-spin" />
      ) : (
        <ChevronDownIcon className="size-4 opacity-50" />
      )}
    </button>
  );
}
