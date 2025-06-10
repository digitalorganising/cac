import { AppSearchParams } from "@/lib/search-params";

export const filterLabels: Partial<Record<keyof AppSearchParams, string>> = {
  "parties.unions": "Unions",
  "parties.employer": "Employer",
  reference: "Reference",
  state: "Status",
  "events.type": "Events",
};
