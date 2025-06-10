"use client";

import { DateRange } from "../ui/date-range";
import { useAppQueryState } from "@/lib/app-query-state";

type Props = Omit<
  React.ComponentProps<typeof DateRange>,
  "onSelectStart" | "onSelectEnd" | "start" | "end"
>;

export default function EventDateSelect(props: Props) {
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
