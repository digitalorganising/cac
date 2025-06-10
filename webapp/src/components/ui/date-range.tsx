import { cn } from "@/lib/utils";
import { CalendarIcon } from "@radix-ui/react-icons";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";
import { MonthPicker } from "./month-picker";

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
};

const buttonClasses =
  "border-input cursor-pointer pl-2 pr-3 py-2 hover:bg-slate-50 flex w-fit items-center justify-between gap-1 rounded-md bg-white " +
  "focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 aria-expanded:bg-slate-50 " +
  "focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 outline-none";

function CalendarBadge({ selected }: { selected: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex items-center justify-center text-white size-5 px-1 rounded-full pointer-events-none",
        selected ? "bg-slate-600 text-white" : "text-muted-foreground",
      )}
    >
      <CalendarIcon />
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
}: Props) {
  return (
    <span
      className={cn(
        "flex cursor-pointer border-input flex w-fit items-center justify-between rounded-md border bg-white text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none",
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
        <button
          title="Start date"
          className={buttonClasses}
          disabled={disabled === "start" || disabled === true}
        >
          <CalendarBadge selected={start !== undefined} />
          Start
        </button>
      </DateRangePicker>

      <div className="w-px h-7/10 bg-slate-300" />

      {nameEnd && (
        <input
          type="month"
          name={nameEnd}
          form={form}
          value={end?.toISOString().slice(0, 7)}
        />
      )}
      <DateRangePicker date={end} onSelect={onSelectEnd} min={start}>
        <button
          title="End date"
          className={buttonClasses}
          disabled={disabled === "end" || disabled === true}
        >
          <CalendarBadge selected={end !== undefined} />
          End
        </button>
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
