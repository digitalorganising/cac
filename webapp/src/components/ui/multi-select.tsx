"use client";

import React, { ButtonHTMLAttributes, useState } from "react";
import { ChevronDownIcon } from "@radix-ui/react-icons";
import { cn } from "@/lib/utils";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";
import { Checkbox } from "./checkbox";
import { Label } from "./label";

type Props = {
  label: string;
  name: string;
  options: { label: string; value: string }[];
  selected: Set<string>;
  onSelect: (value: string, checked: boolean) => void;
  form?: string;
  disabled?: boolean;
};

export function SelectTrigger({
  children,
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      role="combobox"
      className={cn(
        "cursor-pointer border-input [&_svg:not([class*='text-'])]:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 flex w-fit items-center justify-between gap-2 rounded-md border bg-white hover:bg-slate-50 aria-expanded:bg-slate-50 px-3 py-2 text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
        className,
      )}
      {...props}
    >
      {children}
      <ChevronDownIcon className="size-4 opacity-50" />
    </button>
  );
}

function CountBadge({ count }: { count: number }) {
  return (
    <span className="inline-flex items-center justify-center bg-slate-600 text-white h-4 min-w-4 px-1 rounded-full text-xs tabular-nums">
      {count}
    </span>
  );
}

export default function MultiSelect({
  label,
  name,
  options,
  selected,
  onSelect,
  form,
  disabled,
}: Props) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
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
        <SelectTrigger aria-expanded={open} disabled={!!disabled}>
          {label}
          {selected.size > 0 && <CountBadge count={selected.size} />}
        </SelectTrigger>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-fit p-2">
        {options.map((option) => (
          <Label
            key={option.value}
            htmlFor={option.value}
            className="flex items-center gap-2 p-2 rounded-md hover:bg-slate-100 cursor-pointer [&>*]:cursor-pointer"
          >
            <Checkbox
              id={option.value}
              checked={selected.has(option.value)}
              onCheckedChange={(newChecked) => {
                onSelect(
                  option.value,
                  newChecked === "indeterminate" ? false : newChecked,
                );
              }}
            />
            <span>{option.label}</span>
          </Label>
        ))}
      </PopoverContent>
    </Popover>
  );
}
