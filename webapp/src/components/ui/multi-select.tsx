import { ChevronDownIcon } from "@radix-ui/react-icons";
import { UpdateIcon } from "@radix-ui/react-icons";
import { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { LabelledCheckbox } from "./checkbox";
import CountBadge from "./count-badge";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";
import { ScrollArea } from "./scroll-area";

type Props = {
  label: string;
  name: string;
  options: { label: string; value: string }[];
  selected: Set<string>;
  onSelect: (value: string, checked: boolean) => void;
  onClearAll?: () => void;
  form?: string;
  loading?: boolean;
};

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

export default function MultiSelect({
  label,
  name,
  options,
  selected,
  onSelect,
  onClearAll,
  form,
  loading,
}: Props) {
  return (
    <Popover modal={true}>
      {Array.from(selected).map((value) => (
        <input
          type="hidden"
          name={name}
          value={value}
          form={form}
          key={value}
        />
      ))}
      <PopoverTrigger asChild>
        <SelectTrigger
          aria-label={`${label} filter`}
          loading={loading}
          count={selected.size}
        >
          {label}
        </SelectTrigger>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-fit p-0">
        <ScrollArea
          className="[&>[data-radix-scroll-area-viewport]]:max-h-[300px] p-2"
          type="auto"
        >
          {options.map((option) => (
            <LabelledCheckbox
              key={option.value}
              id={option.value}
              label={option.label}
              checked={selected.has(option.value)}
              onCheckedChange={(newChecked) => {
                onSelect(
                  option.value,
                  newChecked === "indeterminate" ? false : newChecked,
                );
              }}
            />
          ))}
        </ScrollArea>
        {onClearAll ? (
          <div className="p-0.5 border-t border-slate-200 flex justify-center items-center">
            <button
              aria-label="Clear all"
              className="text-center text-sm px-3 py-1 rounded-sm hover:bg-slate-100"
              onClick={onClearAll}
            >
              Clear all
            </button>
          </div>
        ) : null}
      </PopoverContent>
    </Popover>
  );
}
