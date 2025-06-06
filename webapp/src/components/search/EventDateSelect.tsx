"use client";

import { useOptimisticFilterRouter } from "@/lib/useOptimisticFilterRouter";
import { DateRange } from "../ui/date-range";
import dayjs from "dayjs";

type Props = Omit<
  React.ComponentProps<typeof DateRange>,
  "onSelectStart" | "onSelectEnd" | "start" | "end"
>;

const dateFromParam = (
  param: string | string[] | undefined,
): Date | undefined => {
  if (!param) {
    return undefined;
  }
  const dateStr = typeof param === "string" ? param : param[0];
  return dayjs(dateStr).startOf("month").toDate();
};

export default function EventDateSelect(props: Props) {
  const filterRouter = useOptimisticFilterRouter({
    resetOnNavigate: new Set(["page"]),
  });

  const start = dateFromParam(filterRouter.params["events.date.from"]);
  const end = dateFromParam(filterRouter.params["events.date.to"]);

  const handleSelectMonth =
    (key: "events.date.from" | "events.date.to") => (date?: Date) => {
      if (!date) {
        filterRouter.delete(key);
      } else {
        const dateStr = (
          key === "events.date.from"
            ? dayjs(date).startOf("month")
            : dayjs(date).endOf("month")
        ).format("YYYY-MM-DD");
        filterRouter.add(key, dateStr);
      }
    };

  return (
    <DateRange
      {...props}
      start={start}
      end={end}
      onSelectStart={handleSelectMonth("events.date.from")}
      onSelectEnd={handleSelectMonth("events.date.to")}
    />
  );
}
