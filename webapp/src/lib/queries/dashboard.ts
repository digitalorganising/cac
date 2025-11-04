import { Types as OpenSearchTypes } from "@opensearch-project/opensearch";
import { cacheLife } from "next/cache";
import "server-only";
import { getStateCategory } from "../utils/state-category";
import { getClient } from "./client";
import { outcomesIndex } from "./common";
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

// Request creators
const createCategoryCountsRequest = () => ({
  size: 0,
  aggs: {
    state: {
      terms: {
        field: "facet.state",
        size: 10,
      },
    },
  },
});

const createApplicationsPerUnionRequest = () => ({
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
});

const createBargainingUnitSizesRequest = () => ({
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
});

const createTimeToAcceptanceRequest = () => ({
  size: 0,
});

const createTimeToConclusionRequest = () => ({
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
});

const createBargainingUnitSizeVsTurnoutRequest = () => ({
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
});

const isSearchResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): response is OpenSearchTypes.Core_Msearch.MultiSearchItem => {
  if ("error" in response) {
    console.error(response);
    throw new Error("Response is an error response, not a search response");
  }
  return true;
};

// Response parsers
const parseCategoryCountsResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): CategoryCounts => {
  const body = isSearchResponse(response) ? response : undefined;
  const agg = body?.aggregations
    ?.state as OpenSearchTypes.Common_Aggregations.StringTermsAggregate;
  const buckets =
    agg?.buckets as OpenSearchTypes.Common_Aggregations.StringTermsBucket[];
  return stateCounts(buckets);
};

const parseApplicationsPerUnionResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): ApplicationsPerUnionData => {
  const body = isSearchResponse(response) ? response : undefined;
  const unionsAgg = body?.aggregations
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
};

const parseBargainingUnitSizesResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): BargainingUnitSizeData => {
  const body = isSearchResponse(response) ? response : undefined;
  const agg = body?.aggregations
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
};

const parseTimeToAcceptanceResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): TimeToAcceptanceData => {
  const body = isSearchResponse(response) ? response : undefined;
  return [] as TimeToAcceptanceData;
};

const parseTimeToConclusionResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): TimeToConclusionData => {
  const body = isSearchResponse(response) ? response : undefined;
  const agg = body?.aggregations
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
};

const parseBargainingUnitSizeVsTurnoutResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): BargainingUnitSizeVsTurnoutData => {
  const body = isSearchResponse(response) ? response : undefined;
  const hits = body?.hits.hits || [];
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
};

// Single msearch function
export type DashboardData = {
  categoryCounts: CategoryCounts;
  applicationsPerUnion: ApplicationsPerUnionData;
  bargainingUnitSizes: BargainingUnitSizeData;
  timeToAcceptance: TimeToAcceptanceData;
  timeToConclusion: TimeToConclusionData;
  bargainingUnitSizeVsTurnout: BargainingUnitSizeVsTurnoutData;
};

export async function getAllDashboardData(): Promise<DashboardData> {
  "use cache";
  cacheLife("hours");

  const client = await getClient();

  // Build msearch body: alternating index and query pairs
  const msearchBody = [
    { index: outcomesIndex },
    createCategoryCountsRequest(),
    { index: outcomesIndex },
    createApplicationsPerUnionRequest(),
    { index: outcomesIndex },
    createBargainingUnitSizesRequest(),
    { index: outcomesIndex },
    createTimeToAcceptanceRequest(),
    { index: outcomesIndex },
    createTimeToConclusionRequest(),
    { index: outcomesIndex },
    createBargainingUnitSizeVsTurnoutRequest(),
  ];

  const msearchResponse = await client.msearch({
    body: msearchBody,
  });

  // Parse responses in order
  const responses = msearchResponse.body.responses;
  return {
    categoryCounts: parseCategoryCountsResponse(responses[0]),
    applicationsPerUnion: parseApplicationsPerUnionResponse(responses[1]),
    bargainingUnitSizes: parseBargainingUnitSizesResponse(responses[2]),
    timeToAcceptance: parseTimeToAcceptanceResponse(responses[3]),
    timeToConclusion: parseTimeToConclusionResponse(responses[4]),
    bargainingUnitSizeVsTurnout: parseBargainingUnitSizeVsTurnoutResponse(
      responses[5],
    ),
  };
}
