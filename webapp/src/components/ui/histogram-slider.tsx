"use client";

import { Popover, PopoverContent, PopoverTrigger } from "./popover";
import { ButtonHTMLAttributes, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { cn } from "@/lib/utils";
import { BarChartIcon } from "@radix-ui/react-icons";
import { Slider } from "./slider";
import type { Bin } from "./histogram";
import { Input } from "./input";
import { Label } from "./label";

const DynamicHistogram = dynamic(() => import("./histogram"), {
  ssr: false,
});

function HistogramSliderTrigger({
  children,
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        "cursor-pointer border-input [&_svg:not([class*='text-'])]:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 flex w-fit items-center justify-between gap-2 rounded-md border bg-white hover:bg-slate-50 aria-expanded:bg-slate-50 px-3 py-2 text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
        className,
      )}
      {...props}
    >
      {children}
      <BarChartIcon />
    </button>
  );
}

type Props = {
  label: React.ReactNode;
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
  label,
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
    <Popover modal={true}>
      <PopoverTrigger asChild>
        <HistogramSliderTrigger>{label}</HistogramSliderTrigger>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-100">
        <DynamicHistogram
          bins={bins}
          min={uiMin}
          max={uiMax}
          className="h-24 w-full"
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
      </PopoverContent>
    </Popover>
  );
}
