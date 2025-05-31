import { AppQueryParams } from "@/lib/filtering";

export type Filters = Pick<
  AppQueryParams,
  "parties.unions" | "parties.employer" | "reference" | "state" | "events.type"
>;

export const filterLabels: Record<keyof Filters, string> = {
  "parties.unions": "Union",
  "parties.employer": "Employer",
  reference: "Reference",
  state: "State",
  "events.type": "Events",
};
