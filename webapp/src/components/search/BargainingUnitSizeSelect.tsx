"use client";

import React from "react";
import { HistogramSlider } from "../ui/histogram-slider";
import { useAppQueryState } from "@/lib/app-query-state";

export default function BargainingUnitSizeSelect({
  bins,
}: {
  bins: React.ComponentProps<typeof HistogramSlider>["bins"];
}) {
  const [min, setMin] = useAppQueryState("bargainingUnit.size.from");
  const [max, setMax] = useAppQueryState("bargainingUnit.size.to");

  const handleSelectRange = (newMin?: number, newMax?: number) => {
    setMin(newMin ?? null);
    setMax(newMax ?? null);
  };

  return (
    <HistogramSlider
      label="Bargaining Unit Size"
      name="bargainingUnit.size"
      form="outcomes-search-form"
      bins={bins}
      min={min ?? undefined}
      max={max ?? undefined}
      onSelectRange={handleSelectRange}
    />
  );
}
