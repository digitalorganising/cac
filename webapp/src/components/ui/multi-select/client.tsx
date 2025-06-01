"use client";

import { useState } from "react";
import { Popover, PopoverContent, PopoverTrigger } from "../popover";
import { Checkbox } from "../checkbox";
import { Label } from "../label";
import { ScrollArea } from "../scroll-area";
import { SelectTrigger } from "./server";

type Props = {
  label: string;
  name: string;
  options: { label: string; value: string }[];
  selected: Set<string>;
  onSelect: (value: string, checked: boolean) => void;
  form?: string;
  loading?: boolean;
};

export default function MultiSelect({
  label,
  name,
  options,
  selected,
  onSelect,
  form,
  loading,
}: Props) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen} modal={true}>
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
          aria-expanded={open}
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
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
