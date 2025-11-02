import { Types as OpenSearchTypes } from "@opensearch-project/opensearch";
import { cacheLife } from "next/cache";
import "server-only";
import { getStateCategory } from "../utils/state-category";
import { filterPrefix, getClient, outcomesIndex } from "./common";
import { getFacetProps } from "./facets";

export type CategoryCounts = {
  successful: number;
  unsuccessful: number;
  pending: number;
  withdrawn: number;
};

export type ApplicationsPerUnionData = {
  union: string;
  successful: number;
  unsuccessful: number;
  pending: number;
  withdrawn: number;
}[];

export type BargainingUnitSizeData = {
  sizeRange: string;
  successful: number;
  unsuccessful: number;
  pending: number;
  withdrawn: number;
}[];

export type TimeToAcceptanceData = {
  timeRange: string;
  count: number;
}[];

export type TimeToConclusionData = {
  timeRange: number;
  successful: number;
  unsuccessful: number;
}[];

export type BargainingUnitSizeVsTurnoutData = {
  size: number;
  turnout: number;
  title: string;
  success: boolean;
}[];

const stateCounts = (
  buckets: OpenSearchTypes.Common_Aggregations.StringTermsBucket[],
): CategoryCounts => {
  const counts: CategoryCounts = {
    successful: 0,
    unsuccessful: 0,
    pending: 0,
    withdrawn: 0,
  };

  for (const bucket of buckets) {
    const facet = getFacetProps(bucket.key);
    const category = getStateCategory(facet.value.toString());
    if (category) {
      counts[category] += bucket.doc_count;
    }
  }
  return counts;
};

export async function getCategoryCounts(): Promise<CategoryCounts> {
  "use cache";
  cacheLife("hours");

  const client = await getClient();
  const body = {
    size: 0,
    aggs: {
      state: {
        terms: {
          field: "facet.state",
          size: 10,
        },
      },
    },
  };

  const response = await client.search({ index: outcomesIndex, body });
  const agg = response.body.aggregations
    ?.state as OpenSearchTypes.Common_Aggregations.StringTermsAggregate;
  const buckets =
    agg?.buckets as OpenSearchTypes.Common_Aggregations.StringTermsBucket[];

  return stateCounts(buckets);
}

export async function getApplicationsPerUnion(): Promise<ApplicationsPerUnionData> {
  "use cache";
  cacheLife("hours");

  const client = await getClient();
  const body = {
    size: 0,
    aggs: {
      unions: {
        terms: {
          field: "facet.parties.unions",
          size: 15,
        },
        aggs: {
          states: {
            terms: {
              field: "facet.state",
              size: 10,
            },
          },
        },
      },
    },
  };

  const response = await client.search({ index: outcomesIndex, body });
  const unionsAgg = response.body.aggregations
    ?.unions as OpenSearchTypes.Common_Aggregations.StringTermsAggregate;
  const unionBuckets =
    unionsAgg?.buckets as OpenSearchTypes.Common_Aggregations.StringTermsBucket[];

  return unionBuckets.map((unionBucket: any) => {
    const unionFacet = getFacetProps(unionBucket.key);
    const union = unionFacet.value.toString();
    const stateBuckets = unionBucket.states?.buckets || [];

    return {
      union,
      ...stateCounts(stateBuckets),
    };
  });
}

export async function getBargainingUnitSizes(): Promise<BargainingUnitSizeData> {
  "use cache";
  cacheLife("hours");

  const client = await getClient();
  const body = {
    size: 0,
    aggs: {
      bargainingUnitSize: {
        histogram: {
          field: "facet.bargainingUnit.size",
          interval: 5,
          hard_bounds: {
            min: 0,
            max: 500,
          },
          extended_bounds: {
            min: 0,
            max: 500,
          },
        },
        aggs: {
          states: {
            terms: {
              field: "facet.state",
              size: 10,
            },
          },
        },
      },
    },
  };

  const response = await client.search({ index: outcomesIndex, body });
  const agg = response.body.aggregations
    ?.bargainingUnitSize as OpenSearchTypes.Common_Aggregations.HistogramAggregate;
  const buckets =
    agg?.buckets as OpenSearchTypes.Common_Aggregations.HistogramBucket[];

  return buckets.map((bucket: any) => {
    const facet = getFacetProps(bucket.key);
    const sizeRange = facet.value.toString();
    const stateBuckets = bucket.states?.buckets || [];
    return {
      sizeRange,
      ...stateCounts(stateBuckets),
    };
  });
}

export async function getTimeToAcceptance(): Promise<TimeToAcceptanceData> {
  "use cache";
  cacheLife("hours");

  const client = await getClient();
  return {} as any;
}

export async function getTimeToConclusion(): Promise<TimeToConclusionData> {
  "use cache";
  cacheLife("hours");

  const client = await getClient();
  const body = {
    size: 0,
    query: {
      term: {
        "filter.duration.relation": "eq",
      },
    },
    aggs: {
      timeToConclusion: {
        histogram: {
          field: "filter.duration.value",
          interval: 7 * 24 * 60 * 60,
          extended_bounds: {
            min: 0,
            max: 104 * 7 * 24 * 60 * 60,
          },
          hard_bounds: {
            min: 0,
            max: 104 * 7 * 24 * 60 * 60,
          },
        },
        aggs: {
          states: {
            terms: {
              field: "facet.state",
              size: 10,
            },
          },
        },
      },
    },
  };

  const response = await client.search({ index: outcomesIndex, body });
  const agg = response.body.aggregations
    ?.timeToConclusion as OpenSearchTypes.Common_Aggregations.HistogramAggregate;
  const buckets =
    agg?.buckets as OpenSearchTypes.Common_Aggregations.HistogramBucket[];

  return buckets.map((bucket: any) => {
    const facet = getFacetProps(bucket.key);
    const seconds = Number(facet.value);
    const timeRange = Math.floor(seconds / (7 * 24 * 60 * 60));
    const stateBuckets = bucket.states?.buckets || [];
    return {
      timeRange,
      ...stateCounts(stateBuckets),
    };
  });
}

export async function getBargainingUnitSizeVsTurnout(): Promise<BargainingUnitSizeVsTurnoutData> {
  "use cache";
  cacheLife("hours");

  const client = await getClient();
  // Fetch outcomes that have both bargaining unit size and ballot data
  const body = {
    size: 1000,
    query: {
      bool: {
        filter: [
          {
            range: {
              "filter.bargainingUnit.size": {
                gte: 0,
                lte: 1000,
              },
            },
          },
          {
            term: {
              "filter.events.type": "ballot_held",
            },
          },
        ],
      },
    },
    _source: [
      "display.bargainingUnit.size",
      "display.ballot.turnoutPercent",
      "display.title",
      "display.state.value",
    ],
  };

  const response = await client.search({ index: outcomesIndex, body });
  const hits = response.body.hits?.hits || [];

  const data: BargainingUnitSizeVsTurnoutData = [];

  for (const hit of hits) {
    if (!hit._source?.display) continue;
    const outcome = hit._source.display;
    const size = outcome.bargainingUnit?.size;
    const turnout = outcome.ballot?.turnoutPercent;
    const title = outcome.title;
    const state = outcome.state.value;
    // Only include outcomes that have both size and turnout data
    if (
      size !== undefined &&
      size !== null &&
      turnout !== undefined &&
      turnout !== null &&
      title
    ) {
      data.push({
        size,
        turnout,
        title,
        success: state === "successful" || state === "method_agreed",
      });
    }
  }

  return data;
}
