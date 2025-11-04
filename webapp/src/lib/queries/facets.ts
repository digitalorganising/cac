import { Types as OpenSearchTypes } from "@opensearch-project/opensearch";
import { cacheLife } from "next/cache";
import "server-only";
import { hasDeepProperty } from "../utils";
import { getClient } from "./client";
import {
  FilterOptions,
  QueryOptions,
  getFilters,
  getQuery,
  outcomesIndex,
} from "./common";

export const multiSelectFacetNames = [
  "parties.unions",
  "state",
  "events.type",
] as const;
export type MultiSelectFacet = (typeof multiSelectFacetNames)[number];
export const histogramFacetNames = ["bargainingUnit.size"] as const;
export type HistogramFacet = (typeof histogramFacetNames)[number];

type Bucket = { value: string | number; label?: string; count: number };

export const normalizeBuckets = (
  aggregations: Record<string, OpenSearchTypes.Common_Aggregations.Aggregate>,
): Record<string, Bucket[]> =>
  Object.fromEntries(
    [...multiSelectFacetNames, ...histogramFacetNames].flatMap((name) => {
      const agg = aggregations?.[facetPrefix + name];
      if (!agg || !("filtered" in agg)) {
        return [];
      }
      const buckets = agg.filtered
        .buckets as OpenSearchTypes.Common_Aggregations.StringTermsBucket[];
      return [
        [
          name,
          buckets.map(({ key, doc_count }) => ({
            ...getFacetProps(key),
            count: doc_count,
          })),
        ],
      ];
    }),
  );

export type Facets = {
  multiSelect: Record<MultiSelectFacet, Bucket[]>;
  histogram: Record<HistogramFacet, Bucket[]>;
};

export type GetFacetsOptions = QueryOptions & FilterOptions;

const pick = <T extends object, const K extends keyof T>(
  obj: T,
  keys: readonly K[],
): Pick<T, K> =>
  Object.fromEntries(keys.map((key) => [key, obj[key]])) as Pick<T, K>;

export const getFacets = async (
  options: GetFacetsOptions,
  debug = false,
): Promise<Facets> => {
  "use cache: remote";
  cacheLife("hours");

  const client = await getClient();
  const filters = getFilters(options);
  const body = {
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
      ...histogramAgg("bargainingUnit.size", filters, {
        // These are magic numbers that make the histogram look nice
        min: 0,
        max: 250,
        interval: 5,
      }),
    },
  };
  if (debug) {
    console.log("Request body (facets):", body);
  }
  const response = await client.search({ index: outcomesIndex, body });

  if (debug) {
    console.log("Response body (facets):", response.body);
  }

  const aggs = response.body.aggregations;
  const bucketedFacets = normalizeBuckets(aggs ?? {});
  return {
    multiSelect: pick(bucketedFacets, multiSelectFacetNames),
    histogram: pick(bucketedFacets, histogramFacetNames),
  };
};

const facetPrefix = "facet.";

const nonMatchingFilters = (
  filters: OpenSearchTypes.Common_QueryDsl.QueryContainer[],
  name: string,
) => {
  const shouldKeepFilter = (
    filter: OpenSearchTypes.Common_QueryDsl.QueryContainer,
  ) => !hasDeepProperty({ _name: `filter-${name}` }, filter);

  return {
    bool: {
      filter: filters.filter(shouldKeepFilter),
    },
  };
};

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

const histogramAgg = (
  name: string,
  filters: OpenSearchTypes.Common_QueryDsl.QueryContainer[],
  params: { min: number; max: number; interval: number },
) => ({
  [facetPrefix + name]: {
    filter: nonMatchingFilters(filters, name),
    aggs: {
      filtered: {
        histogram: {
          field: facetPrefix + name,
          interval: params.interval,
          hard_bounds: {
            min: params.min,
            max: params.max,
          },
          extended_bounds: {
            min: params.min,
            max: params.max,
          },
        },
      },
    },
  },
});

export const getFacetProps = (
  key: OpenSearchTypes.Common.FieldValue,
): { value: string | number; label?: string } => {
  switch (typeof key) {
    case "string":
      const p = JSON.parse(key);
      if (typeof p === "string") {
        return { value: p };
      }
      return { value: p.value, label: p.label };
    case "number":
      return { value: key };
    case "boolean":
      return { value: key.toString() };
    case "undefined":
      return { value: "" };
    default:
      return key as { value: string; label?: string };
  }
};
