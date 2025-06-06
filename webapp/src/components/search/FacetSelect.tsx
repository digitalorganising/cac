"use client";

import React from "react";
import MultiSelect from "../ui/multi-select";
import { useOptimisticFilterRouter } from "@/lib/useOptimisticFilterRouter";
import { Filters } from "@/lib/types";
import { arr } from "@/lib/utils";

type Props = Omit<
  React.ComponentProps<typeof MultiSelect>,
  "selected" | "onSelect" | "name"
> & { name: keyof Filters };

export default function FacetSelect(props: Props) {
  const filterRouter = useOptimisticFilterRouter({
    resetOnNavigate: new Set(["page"]),
  });
  const selected = new Set(arr(filterRouter.params[props.name] ?? []));

  const handleSelect = (value: string, checked: boolean) => {
    if (checked) {
      filterRouter.add(props.name, value);
    } else {
      filterRouter.delete(props.name, value);
    }
  };

  return (
    <MultiSelect
      {...props}
      selected={selected}
      onSelect={handleSelect}
      onClearAll={() => filterRouter.delete(props.name)}
    />
  );
}
