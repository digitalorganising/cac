import dayjs from "dayjs";
import { OutcomeKeyDates } from "@/lib/types";

function pluralize(singular: string, quantity: number): string {
  return quantity === 1 ? singular : `${singular}s`;
}

export function formatDuration({
  outcomeConcluded,
  applicationReceived,
}: OutcomeKeyDates): string {
  const start = dayjs(applicationReceived);
  const end = dayjs(outcomeConcluded ?? undefined);

  const nDays = end.diff(start, "days");
  if (nDays <= 31) {
    return `${nDays} ${pluralize("day", nDays)}`;
  }

  const nWeeks = Math.floor(nDays / 7);
  if (nWeeks <= 8) {
    const remainder = nDays % 7;
    return `${nWeeks} ${pluralize("week", nWeeks)}, ${remainder} ${pluralize("day", remainder)}`;
  }

  const nMonths = end.diff(start, "months");
  const nYears = Math.floor(nMonths / 12);
  const remainder = end.diff(start.add(nMonths, "months"), "days");
  if (nYears < 1) {
    return `${nMonths} ${pluralize("month", nMonths)}, ${remainder} ${pluralize("day", remainder)}`;
  } else {
    return `${nYears} ${pluralize("year", nYears)}, ${nMonths % 12} ${pluralize("month", nMonths % 12)}, ${remainder} ${pluralize("day", remainder)}`;
  }
}
