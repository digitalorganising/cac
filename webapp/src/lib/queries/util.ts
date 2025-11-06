import { AppSearchParams, SortKey, SortOrder } from "../search-params";
import { GetOutcomesOptions } from "./outcomes";

export const appSearchParamsToOutcomesOptions = (
  pageSize: number,
  params: AppSearchParams,
): GetOutcomesOptions => {
  const [sortKey, sortOrder]: [SortKey | undefined, SortOrder | undefined] =
    (params.sort?.split("-") as [SortKey, SortOrder]) ?? [undefined, undefined];
  return {
    from: (params.page - 1) * pageSize,
    size: pageSize,
    query: params.query ?? undefined,
    "parties.unions": params["parties.unions"],
    "parties.employer": params["parties.employer"],
    reference: params.reference ? [params.reference] : undefined,
    state: params.state,
    "events.type": params["events.type"],
    "events.date.from": params["events.date.from"]?.toISOString() ?? undefined,
    "events.date.to": params["events.date.to"]?.toISOString() ?? undefined,
    "bargainingUnit.size.from": params["bargainingUnit.size.from"] ?? undefined,
    "bargainingUnit.size.to": params["bargainingUnit.size.to"] ?? undefined,
    "durations.overall.from": params["durations.overall.from"] ?? undefined,
    "durations.overall.to": params["durations.overall.to"] ?? undefined,
    sortKey,
    sortOrder,
  };
};
