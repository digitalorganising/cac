import dayjs from "dayjs";
import { OutcomeKeyDates } from "@/lib/types";

export function formatDuration({
  outcomeConcluded,
  applicationReceived,
}: OutcomeKeyDates): string {
  const start = dayjs(applicationReceived);
  const end = dayjs(outcomeConcluded ?? undefined);

  const nDays = end.diff(start, "days");
  if (nDays <= 31) {
    return `${nDays} days`;
  }

  const nWeeks = Math.floor(nDays / 7);
  if (nWeeks <= 8) {
    const remainder = nDays % 7;
    return `${nWeeks} weeks, ${remainder} days`;
  }

  const nMonths = end.diff(start, "months");
  const nYears = Math.floor(nMonths / 12);
  const remainder = end.diff(start.add(nMonths, "months"), "days");
  if (nYears < 1) {
    return `${nMonths} months, ${remainder} days`;
  } else {
    return `${nYears} years, ${nMonths % 12} months, ${remainder} days`;
  }
}
