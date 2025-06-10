"use client";

import React from "react";
import { HistogramSlider } from "../ui/histogram-slider";
import { useOptimisticFilterRouter } from "@/lib/useOptimisticFilterRouter";

const numberFromParam = (param: string | string[] | undefined) => {
  if (!param) {
    return undefined;
  }
  const n = Number(param);
  if (isNaN(n)) {
    return undefined;
  }
  return n;
};

export default function BargainingUnitSizeSelect({
  bins,
}: {
  bins: React.ComponentProps<typeof HistogramSlider>["bins"];
}) {
  const filterRouter = useOptimisticFilterRouter({
    resetOnNavigate: new Set(["page"]),
  });

  const min = numberFromParam(filterRouter.params["bargainingUnit.size.from"]);
  const max = numberFromParam(filterRouter.params["bargainingUnit.size.to"]);

  const handleSelectRange = (min?: number, max?: number) => {
    if (min !== undefined) {
      filterRouter.replace("bargainingUnit.size.from", min.toString());
    } else {
      filterRouter.delete("bargainingUnit.size.from");
    }
    if (max !== undefined) {
      filterRouter.replace("bargainingUnit.size.to", max.toString());
    } else {
      filterRouter.delete("bargainingUnit.size.to");
    }
  };

  return (
    <HistogramSlider
      label="Bargaining Unit Size"
      name="bargainingUnit.size"
      form="outcomes-search-form"
      bins={bins}
      min={min}
      max={max}
      onSelectRange={handleSelectRange}
    />
  );
}
