"use client";

import { ClockIcon } from "@radix-ui/react-icons";
import { useEffect, useState } from "react";
import { useAppQueryState } from "@/lib/app-query-state";
import { formatSecondsDuration } from "@/lib/duration";
import { clamp } from "@/lib/utils";
import { AccordionContent, AccordionItem } from "../ui/accordion";
import { InputTriggerButton } from "../ui/input-trigger-button";
import { Label } from "../ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { Slider } from "../ui/slider";
import { AccordionFilter } from "./common";

const MIN_DURATION_WEEKS = 0;
const MAX_DURATION_WEEKS = 79;
const WEEK = 7 * 24 * 60 * 60;
const MIN_DURATION = MIN_DURATION_WEEKS * WEEK;
const MAX_DURATION = MAX_DURATION_WEEKS * WEEK;

function DurationValue({
  value,
  label,
  name,
  bound = -1,
}: {
  value: number;
  label: string;
  name: string;
  bound?: number;
}) {
  return (
    <div>
      <Label htmlFor={name} className="text-xs font-semibold">
        {label}
      </Label>
      <span className="text-sm">
        {formatSecondsDuration(value)}
        {value === bound ? "+" : ""}
      </span>
      <input
        type="hidden"
        name={name}
        value={value}
        form="outcomes-search-form"
      />
    </div>
  );
}

function DurationSelectSlider({
  min,
  max,
  handleSelectRange,
}: {
  min?: number;
  max?: number;
  handleSelectRange: (newMin?: number, newMax?: number) => void;
}) {
  const [uiValue, setUiValue] = useState<[number, number]>([
    min ?? MIN_DURATION,
    max ?? MAX_DURATION,
  ]);

  useEffect(() => {
    setUiValue([min ?? MIN_DURATION, max ?? MAX_DURATION]);
  }, [min, max]);

  const [uiMin, uiMax] = uiValue;
  const commit = (min?: number, max?: number) => {
    const clampedMin = min
      ? clamp(min, MIN_DURATION, max ?? MAX_DURATION)
      : undefined;
    const clampedMax = max
      ? clamp(max, clampedMin ?? MIN_DURATION, MAX_DURATION)
      : undefined;

    setUiValue([clampedMin ?? uiMin, clampedMax ?? uiMax]);
    handleSelectRange(
      clampedMin === MIN_DURATION ? undefined : clampedMin,
      clampedMax === MAX_DURATION ? undefined : clampedMax,
    );
  };
  return (
    <div className="mt-2">
      <Slider
        min={MIN_DURATION}
        max={MAX_DURATION}
        minStepsBetweenThumbs={WEEK}
        value={uiValue}
        onValueChange={([min, max]) => setUiValue([min, max])}
        onValueCommit={([min, max]) => commit(min, max)}
        thumbClassName="size-4"
      />
      <div className="flex justify-between mt-6">
        <DurationValue
          value={uiMin}
          label="From"
          name="durations.overall.from"
        />
        <DurationValue
          value={uiMax}
          label="To"
          name="durations.overall.to"
          bound={MAX_DURATION}
        />
      </div>
    </div>
  );
}

export function DurationSelect() {
  const [min, setMin] = useAppQueryState("durations.overall.from");
  const [max, setMax] = useAppQueryState("durations.overall.to");

  const handleSelectRange = (newMin?: number, newMax?: number) => {
    setMin(newMin ?? null);
    setMax(newMax ?? null);
  };

  return (
    <Popover modal={true}>
      <PopoverTrigger asChild>
        <InputTriggerButton icon={<ClockIcon />} selected={!!min || !!max}>
          Duration
        </InputTriggerButton>
      </PopoverTrigger>
      <PopoverContent align="start">
        <DurationSelectSlider
          min={min ?? undefined}
          max={max ?? undefined}
          handleSelectRange={handleSelectRange}
        />
      </PopoverContent>
    </Popover>
  );
}

export function DurationSelectMobile() {
  const [min, setMin] = useAppQueryState("durations.overall.from");
  const [max, setMax] = useAppQueryState("durations.overall.to");

  const handleSelectRange = (newMin?: number, newMax?: number) => {
    setMin(newMin ?? null);
    setMax(newMax ?? null);
  };

  return (
    <AccordionItem value="duration">
      <AccordionFilter
        label="Duration"
        count={min || max ? 1 : undefined}
        onClear={() => {
          setMin(null);
          setMax(null);
        }}
      />
      <AccordionContent className="p-2">
        <DurationSelectSlider
          min={min ?? undefined}
          max={max ?? undefined}
          handleSelectRange={handleSelectRange}
        />
      </AccordionContent>
    </AccordionItem>
  );
}
