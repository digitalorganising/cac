"use client";

import React from "react";
import { useAppQueryState } from "@/lib/app-query-state";
import { MultiSelectFacet } from "@/lib/queries/facets";
import { cn } from "@/lib/utils";
import {
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";
import { LabelledCheckbox } from "../ui/checkbox";
import CountBadge from "../ui/count-badge";
import MultiSelect from "../ui/multi-select";

type Props = Omit<
  React.ComponentProps<typeof MultiSelect>,
  "selected" | "onSelect" | "name"
> & { name: MultiSelectFacet; className?: string };

export function FacetSelectDesktop(props: Props) {
  const [selected, setSelected] = useAppQueryState(props.name);

  const handleSelect = (value: string, checked: boolean) => {
    if (checked) {
      setSelected((s) => [...s, value]);
    } else {
      setSelected((s) => s.filter((v) => v !== value));
    }
  };

  return (
    <MultiSelect
      {...props}
      selected={new Set(selected ?? [])}
      onSelect={handleSelect}
      onClearAll={() => setSelected(null)}
    />
  );
}

export function FacetSelectMobile({
  label,
  options,
  className,
  name,
}: {
  label: string;
  name: MultiSelectFacet;
  options: { value: string; label: string }[];
  className?: string;
}) {
  const [selected, setSelected] = useAppQueryState(name);

  const handleSelect = (value: string, checked: boolean) => {
    if (checked) {
      setSelected((s) => [...s, value]);
    } else {
      setSelected((s) => s.filter((v) => v !== value));
    }
  };

  return (
    <AccordionItem value={name}>
      <AccordionTrigger className="gap-3">
        <span className="hover:underline flex-grow self-start">{label}</span>
        {selected?.length ? (
          <>
            <a
              role="button"
              className="text-xs text-muted-foreground cursor-pointer hover:text-foreground"
              title="Clear all"
              onClick={(e) => {
                e.stopPropagation(); // Don't want to open the accordion
                setSelected(null);
              }}
            >
              Clear
            </a>
            <CountBadge count={selected.length} />
          </>
        ) : null}
      </AccordionTrigger>
      <AccordionContent>
        <div className={cn("flex flex-col gap-2", className)}>
          {options.map((option) => (
            <LabelledCheckbox
              key={option.value}
              id={option.value}
              label={option.label}
              checked={selected?.includes(option.value as any)}
              onCheckedChange={(newChecked) =>
                handleSelect(
                  option.value,
                  newChecked === "indeterminate" ? false : newChecked,
                )
              }
            />
          ))}
        </div>
      </AccordionContent>
    </AccordionItem>
  );
}
