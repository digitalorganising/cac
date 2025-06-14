import { unstable_cache } from "next/cache";
import "server-only";
import { SortKey } from "../search-params";
import { Outcome } from "../types";
import {
  FilterOptions,
  PaginationOptions,
  QueryOptions,
  SortOptions,
  client,
  getFilters,
  getQuery,
  outcomesIndex,
} from "./common";

export type GetOutcomesOptions = PaginationOptions &
  SortOptions &
  QueryOptions &
  FilterOptions;

export const getOutcomes = unstable_cache(
  async ({
    from,
    size,
    sortKey,
    sortOrder,
    ...queryOptions
  }: GetOutcomesOptions): Promise<{ size: number; docs: Outcome[] }> => {
    const response = await client.search({
      index: outcomesIndex,
      body: {
        from,
        size,
        track_total_hits: true,
        query: {
          bool: {
            should: getQuery(queryOptions),
            filter: getFilters(queryOptions),
          },
        },
        sort: getSort(sortKey, sortOrder),
        _source: ["display"],
      },
    });

    const totalHits =
      typeof response.body.hits.total === "number"
        ? response.body.hits.total
        : (response.body.hits.total?.value ?? 0);

    return {
      size: totalHits,
      docs: response.body.hits.hits.map((hit: any) => hit._source.display),
    };
  },
  ["client", "getFilters", "getQuery", "getSort"],
);

const getSort = (sortKey?: SortKey, sortOrder?: "asc" | "desc") => {
  const documentKeys = {
    lastUpdated: "filter.lastUpdated",
    applicationDate: "filter.keyDates.applicationReceived",
    concludedDate: "filter.keyDates.outcomeConcluded",
    bargainingUnitSize: "filter.bargainingUnit.size",
  } as const;
  const tieBreak = { id: { order: "asc" as const } };

  const documentKey =
    sortKey && sortKey !== "relevance" ? documentKeys[sortKey] : undefined;
  if (sortKey && documentKey) {
    return [{ [documentKey]: { order: sortOrder ?? "desc" } }, tieBreak];
  }

  return [
    { _score: { order: "desc" as const } },
    { "filter.lastUpdated": { order: "desc" as const } },
    tieBreak,
  ];
};
