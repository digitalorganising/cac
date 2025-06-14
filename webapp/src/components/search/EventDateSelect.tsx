"use client";

import { CalendarIcon, Cross2Icon } from "@radix-ui/react-icons";
import { useState } from "react";
import { useAppQueryState } from "@/lib/app-query-state";
import {
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";
import CountBadge from "../ui/count-badge";
import { DateRange } from "../ui/date-range";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { InputTriggerButton } from "../ui/input-trigger-button";
import { Label } from "../ui/label";
import { MonthPicker } from "../ui/month-picker";
import { AccordionFilter, humanizeDate } from "./common";

type Props = Omit<
  React.ComponentProps<typeof DateRange>,
  "onSelectStart" | "onSelectEnd" | "start" | "end"
>;

export function EventDateSelect(props: Props) {
  const [start, setStart] = useAppQueryState("events.date.from");
  const [end, setEnd] = useAppQueryState("events.date.to");

  return (
    <DateRange
      {...props}
      start={start ?? undefined}
      end={end ?? undefined}
      onSelectStart={(date) => setStart(date ?? null)}
      onSelectEnd={(date) => setEnd(date ?? null)}
    />
  );
}

function MobileDateSelect({
  label,
  name,
  value,
  placeholder,
  min,
  max,
  onSelect,
}: {
  label: string;
  name: string;
  value?: Date;
  placeholder: string;
  min?: Date;
  max?: Date;
  onSelect?: (date?: Date) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="flex flex-col w-full space-y-1">
      <Label htmlFor={name} className="text-xs">
        {label}
      </Label>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <InputTriggerButton
            id={name}
            icon={<CalendarIcon />}
            className="w-full flex-row-reverse justify-end relative"
          >
            {value ? (
              humanizeDate(value)
            ) : (
              <span className="text-muted-foreground">{placeholder}</span>
            )}
            {value && onSelect ? (
              <button
                title="Clear"
                className="absolute right-1 top-1/2 -translate-y-1/2 bg-inherit size-7"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelect(undefined);
                }}
              >
                <Cross2Icon />
              </button>
            ) : null}
          </InputTriggerButton>
        </DialogTrigger>
        <DialogContent className="w-fit p-2" showCloseButton={false}>
          <DialogTitle className="sr-only">{label}</DialogTitle>
          <DialogDescription className="sr-only">
            Date selector
          </DialogDescription>
          <MonthPicker
            selectedMonth={value}
            onMonthSelect={(date) => {
              onSelect?.(date);
              setOpen(false);
            }}
            minDate={min}
            maxDate={max}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}

export function EventDateSelectMobile(props: Props) {
  const [start, setStart] = useAppQueryState("events.date.from");
  const [end, setEnd] = useAppQueryState("events.date.to");

  return (
    <AccordionItem value="events.date">
      <AccordionFilter
        label="Date"
        count={start || end ? (start ? 1 : 0) + (end ? 1 : 0) : undefined}
        onClear={() => {
          setStart(null);
          setEnd(null);
        }}
      />
      <AccordionContent className="space-y-2">
        <MobileDateSelect
          label="Start"
          name="events.date.from"
          value={start ?? undefined}
          placeholder="Select a start date"
          max={end ?? undefined}
          onSelect={(date) => setStart(date ?? null)}
        />
        <MobileDateSelect
          label="End"
          name="events.date.to"
          value={end ?? undefined}
          placeholder="Select an end date"
          min={start ?? undefined}
          onSelect={(date) => setEnd(date ?? null)}
        />
      </AccordionContent>
    </AccordionItem>
  );
}
