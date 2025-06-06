import "server-only";

import { Types as OpenSearchTypes } from "@opensearch-project/opensearch";
import { unstable_cache } from "next/cache";
import {
  client,
  FilterOptions,
  getFilters,
  getQuery,
  outcomesIndex,
  QueryOptions,
} from "./common";

export type Facets = {
  bucketed: Record<
    keyof Omit<FilterOptions, "events.date.from" | "events.date.to">,
    { value: string; label?: string; count: number }[]
  >;
};

export type GetFacetsOptions = QueryOptions & FilterOptions;

export const getFacets = unstable_cache(
  async (options: GetFacetsOptions): Promise<Facets> => {
    const filters = getFilters(options);
    const response = await client.search({
      index: outcomesIndex,
      body: {
        size: 0,
        query: {
          bool: {
            should: getQuery(options),
          },
        },
        aggs: {
          ...facetAgg("parties.unions", filters),
          ...facetAgg("state", filters),
          ...facetAgg("events.type", filters),
        },
      },
    });

    const aggs = response.body.aggregations;
    const bucketedFacets = Object.fromEntries(
      Object.entries(aggs ?? {})
        .filter(aggIsFacet)
        .map(([name, agg]) => [
          name.slice(facetPrefix.length),
          (
            agg.filtered
              .buckets as OpenSearchTypes.Common_Aggregations.StringTermsBucket[]
          ).map(({ key, doc_count }) => ({
            ...getFacetProps(key as string),
            count: doc_count,
          })),
        ]),
    ) as Facets["bucketed"];

    return {
      bucketed: bucketedFacets,
    };
  },
  ["client"],
);

const facetPrefix = "facet.";

const nonMatchingFilters = (
  filters: OpenSearchTypes.Common_QueryDsl.QueryContainer[],
  name: string,
) => ({
  bool: {
    filter: filters.filter((f) =>
      Object.values(f).some((v) => v._name !== `filter-${name}`),
    ),
  },
});

const facetAgg = (
  name: string,
  filters: OpenSearchTypes.Common_QueryDsl.QueryContainer[],
) => ({
  [facetPrefix + name]: {
    filter: nonMatchingFilters(filters, name),
    aggs: {
      filtered: {
        terms: {
          field: facetPrefix + name,
          size: 50,
        },
      },
    },
  },
});

const aggIsFacet = (
  agg: [string, OpenSearchTypes.Common_Aggregations.Aggregate],
): agg is [string, OpenSearchTypes.Common_Aggregations.FilterAggregate] =>
  agg[0].startsWith(facetPrefix) && "filtered" in agg[1];

const getFacetProps = (key: string): { value: string; label?: string } => {
  const p = JSON.parse(key);
  if (typeof p === "string") {
    return { value: p };
  }

  return { value: p.value, label: p.label };
};
