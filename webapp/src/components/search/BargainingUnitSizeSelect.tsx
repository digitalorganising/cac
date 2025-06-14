"use client";

import { BarChartIcon } from "@radix-ui/react-icons";
import React from "react";
import { useAppQueryState } from "@/lib/app-query-state";
import { AccordionContent, AccordionItem } from "../ui/accordion";
import { HistogramSlider } from "../ui/histogram-slider";
import { InputTriggerButton } from "../ui/input-trigger-button";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { AccordionFilter } from "./common";

export function BargainingUnitSizeSelect({
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
    <Popover modal={true}>
      <PopoverTrigger asChild>
        <InputTriggerButton icon={<BarChartIcon />}>
          Bargaining Unit Size
        </InputTriggerButton>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-100 p-6">
        <HistogramSlider
          name="bargainingUnit.size"
          form="outcomes-search-form"
          bins={bins}
          min={min ?? undefined}
          max={max ?? undefined}
          onSelectRange={handleSelectRange}
        />
      </PopoverContent>
    </Popover>
  );
}

export function BargainingUnitSizeSelectMobile({
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
    <AccordionItem value="bargainingUnit.size">
      <AccordionFilter
        label="Bargaining Unit Size"
        count={min || max ? (min ? 1 : 0) + (max ? 1 : 0) : undefined}
        onClear={() => {
          setMin(null);
          setMax(null);
        }}
      />
      <AccordionContent className="py-2">
        <HistogramSlider
          name="bargainingUnit.size"
          form="outcomes-search-form"
          bins={bins}
          min={min ?? undefined}
          max={max ?? undefined}
          onSelectRange={handleSelectRange}
        />
      </AccordionContent>
    </AccordionItem>
  );
}
