import dayjs from "dayjs";
import { AppSearchParams } from "@/lib/search-params";
import { AccordionTrigger } from "../ui/accordion";
import CountBadge from "../ui/count-badge";

export const filterLabels: Partial<Record<keyof AppSearchParams, string>> = {
  "parties.unions": "Unions",
  "parties.employer": "Employer",
  reference: "Reference",
  state: "Status",
  "events.type": "Events",
  "events.date.from": "Start date",
  "events.date.to": "End date",
  "bargainingUnit.size.from": "Minimum BU size",
  "bargainingUnit.size.to": "Maximum BU size",
};

export const humanizeDate = (date: Date) => dayjs(date).format("MMMM YYYY");

export function AccordionFilter({
  label,
  count,
  onClear,
}: {
  label: string;
  count?: number;
  onClear: () => void;
}) {
  return (
    <AccordionTrigger className="gap-3">
      <span className="hover:underline flex-grow self-start">{label}</span>
      {count ? (
        <>
          <a
            role="button"
            className="text-xs text-muted-foreground cursor-pointer hover:text-foreground"
            title="Clear all"
            onClick={(e) => {
              e.stopPropagation(); // Don't want to open the accordion
              onClear();
            }}
          >
            Clear
          </a>
          <CountBadge count={count} />
        </>
      ) : null}
    </AccordionTrigger>
  );
}
