"use client";

import React from "react";
import MultiSelect from "../ui/multi-select";
import { useAppQueryState } from "@/lib/app-query-state";
import { MultiSelectFacet } from "@/lib/queries/facets";

type Props = Omit<
  React.ComponentProps<typeof MultiSelect>,
  "selected" | "onSelect" | "name"
> & { name: MultiSelectFacet };

export default function FacetSelect(props: Props) {
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
