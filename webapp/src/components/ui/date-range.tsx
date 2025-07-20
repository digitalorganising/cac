import { CalendarIcon, UpdateIcon } from "@radix-ui/react-icons";
import { cn } from "@/lib/utils";
import { InputTriggerButton } from "./input-trigger-button";
import { MonthPicker } from "./month-picker";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";

type Props = {
  start?: Date;
  end?: Date;
  onSelectStart?: (date?: Date) => void;
  onSelectEnd?: (date?: Date) => void;
  disabled?: boolean | "start" | "end";
  className?: string;
  form?: string;
  nameStart?: string;
  nameEnd?: string;
  loading?: boolean;
};

function CalendarBadge({ selected }: { selected: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex items-center justify-center text-white size-5 px-1 rounded-full pointer-events-none",
        selected ? "bg-slate-600" : "bg-transparent",
      )}
    >
      <CalendarIcon
        className={cn(
          "size-3",
          selected ? "text-white" : "text-muted-foreground",
        )}
      />
    </span>
  );
}

export function DateRange({
  start,
  end,
  onSelectStart,
  onSelectEnd,
  disabled,
  className,
  form,
  nameStart,
  nameEnd,
  loading,
}: Props) {
  return (
    <span
      aria-disabled={loading}
      className={cn(
        "flex cursor-pointer border-input w-fit items-center justify-between rounded-md border bg-white text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none aria-disabled:cursor-not-allowed aria-disabled:opacity-50",
        className,
      )}
    >
      {nameStart && (
        <input
          className="hidden"
          type="month"
          name={nameStart}
          form={form}
          value={start?.toISOString().slice(0, 7)}
        />
      )}
      <DateRangePicker date={start} onSelect={onSelectStart} max={end}>
        <InputTriggerButton
          className="border-none flex-row-reverse pl-2 pr-3 gap-1"
          title="Start date"
          disabled={disabled === "start" || disabled === true}
          loading={loading}
          icon={<CalendarBadge selected={start !== undefined} />}
        >
          Start
        </InputTriggerButton>
      </DateRangePicker>

      <div className="w-px flex-grow self-stretch my-1.5 bg-slate-300" />

      {nameEnd && (
        <input
          type="month"
          name={nameEnd}
          form={form}
          value={end?.toISOString().slice(0, 7)}
        />
      )}
      <DateRangePicker date={end} onSelect={onSelectEnd} min={start}>
        <InputTriggerButton
          className="border-none flex-row-reverse pl-2 pr-3 gap-1"
          title="End date"
          disabled={disabled === "end" || disabled === true}
          loading={loading}
          icon={<CalendarBadge selected={end !== undefined} />}
        >
          End
        </InputTriggerButton>
      </DateRangePicker>
    </span>
  );
}

function DateRangePicker({
  children,
  form,
  name,
  date,
  onSelect,
  max,
  min,
}: {
  children: React.ReactNode;
  date?: Date;
  onSelect?: (date?: Date) => void;
  max?: Date;
  min?: Date;
  form?: string;
  name?: string;
}) {
  return (
    <Popover modal={true}>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <MonthPicker
          selectedMonth={date}
          onMonthSelect={onSelect}
          minDate={min}
          maxDate={max}
        />
      </PopoverContent>
    </Popover>
  );
}
