"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import type { Bin } from "./histogram";
import { Input } from "./input";
import { Label } from "./label";
import { Slider } from "./slider";

const DynamicHistogram = dynamic(() => import("./histogram"), {
  ssr: false,
  loading: () => <div className="h-16 w-full" />,
});

type Props = {
  name: string;
  bins: Bin[];
  max?: number;
  min?: number;
  onSelectRange?: (min?: number, max?: number) => void;
  form?: string;
};

const ensureNumber = (value: string) => Number(value.replace(/\D/, ""));

const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(value, max));

function SliderInput({
  name,
  label,
  value,
  onChange,
  form,
}: {
  name: string;
  label: string;
  value: number | string;
  onChange: (value: number) => void;
  form?: string;
}) {
  return (
    <div>
      <Label htmlFor={name} className="text-xs">
        {label}
      </Label>
      <Input
        id={name}
        className="w-16 text-center text-sm h-8 px-1 py-0"
        type="text"
        value={value}
        onChange={(e) => onChange(ensureNumber(e.target.value))}
        form={form}
      />
    </div>
  );
}

export function HistogramSlider({
  name,
  bins,
  max,
  min,
  onSelectRange,
  form,
}: Props) {
  const lowerBound = bins[0]?.value ?? 0;
  const upperBound = bins[bins.length - 1]?.value ?? 0;

  const [uiValue, setUiValue] = useState<[number, number]>([
    min ?? lowerBound,
    max ?? upperBound,
  ]);

  useEffect(() => {
    setUiValue([min ?? lowerBound, max ?? upperBound]);
  }, [min, max]);

  const [uiMin, uiMax] = uiValue;
  const commit = (min?: number, max?: number) => {
    const clampedMin = min
      ? clamp(min, lowerBound, max ?? upperBound)
      : undefined;
    const clampedMax = max
      ? clamp(max, clampedMin ?? lowerBound, upperBound)
      : undefined;

    setUiValue([clampedMin ?? uiMin, clampedMax ?? uiMax]);
    onSelectRange?.(
      clampedMin === lowerBound ? undefined : clampedMin,
      clampedMax === upperBound ? undefined : clampedMax,
    );
  };

  const formatMaxValue = (value: number) =>
    value === upperBound ? `${value}+` : value;

  return (
    <div>
      <DynamicHistogram
        bins={bins}
        min={uiMin}
        max={uiMax}
        className="h-16 w-full"
      />
      <Slider
        min={lowerBound}
        max={upperBound}
        value={uiValue}
        onValueChange={([min, max]) => setUiValue([min, max])}
        onValueCommit={([min, max]) => commit(min, max)}
        thumbClassName="size-6"
      />
      <div className="flex justify-between mt-4">
        <SliderInput
          name={`${name}.from`}
          label="Minimum"
          value={uiMin}
          onChange={(min) => commit(min, uiMax)}
          form={form}
        />
        <SliderInput
          name={`${name}.to`}
          label="Maximum"
          value={formatMaxValue(uiMax)}
          onChange={(max) => commit(uiMin, max)}
          form={form}
        />
      </div>
    </div>
  );
}
