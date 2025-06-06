import { Filters } from "@/lib/types";

export const filterLabels: Record<keyof Filters, string> = {
  "parties.unions": "Unions",
  "parties.employer": "Employer",
  reference: "Reference",
  state: "Status",
  "events.type": "Events",
};
