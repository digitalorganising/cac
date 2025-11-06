import { Types as OpenSearchTypes } from "@opensearch-project/opensearch";
import { cacheLife } from "next/cache";
import "server-only";
import { StateCategory } from "@/components/timeline/types";
import { getStateCategory } from "../utils";
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
  timeRange: number;
  accepted: number;
  rejected: number;
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

export type ApplicationsReceivedPerMonthData = {
  month: string; // ISO date string (YYYY-MM-DD)
  count: number;
}[];

export type AverageDurations = {
  successful?: number;
  unsuccessful?: number;
  withdrawn?: number;
  pending?: number;
};

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
  query: {
    term: {
      "filter.durations.acceptance.relation": "eq",
    },
  },
  aggs: {
    timeToAcceptance: {
      histogram: {
        field: "filter.durations.acceptance.value",
        interval: 7 * 24 * 60 * 60, // 1 week in seconds
        extended_bounds: {
          min: 0,
          max: 52 * 7 * 24 * 60 * 60, // 52 weeks (1 year)
        },
        hard_bounds: {
          min: 0,
          max: 52 * 7 * 24 * 60 * 60,
        },
      },
      aggs: {
        byDecision: {
          terms: {
            field: "filter.state",
            size: 10,
          },
        },
      },
    },
  },
});

const createTimeToConclusionRequest = () => ({
  size: 0,
  query: {
    term: {
      "filter.durations.overall.relation": "eq",
    },
  },
  aggs: {
    timeToConclusion: {
      histogram: {
        field: "filter.durations.overall.value",
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

const createApplicationsReceivedPerMonthRequest = () => {
  const threeYearsAgo = new Date();
  threeYearsAgo.setFullYear(threeYearsAgo.getFullYear() - 3);
  const threeYearsAgoISO = threeYearsAgo.toISOString().split("T")[0];

  return {
    size: 0,
    query: {
      range: {
        "filter.keyDates.applicationReceived": {
          gte: threeYearsAgoISO,
        },
      },
    },
    aggs: {
      applicationsPerMonth: {
        date_histogram: {
          field: "filter.keyDates.applicationReceived",
          calendar_interval: "month",
          format: "yyyy-MM-dd",
          min_doc_count: 0,
          extended_bounds: {
            min: threeYearsAgoISO,
            max: "now",
          },
        },
      },
    },
  };
};

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

const createAverageDurationsRequest = () => ({
  size: 0,
  aggs: {
    completed: {
      filter: {
        term: {
          "filter.durations.overall.relation": "eq",
        },
      },
      aggs: {
        byState: {
          terms: {
            field: "filter.state",
            size: 20,
          },
          aggs: {
            avgDuration: {
              avg: {
                field: "filter.durations.overall.value",
              },
            },
          },
        },
      },
    },
    pending: {
      filter: {
        term: {
          "filter.durations.overall.relation": "gte",
        },
      },
      aggs: {
        avgDuration: {
          scripted_metric: {
            init_script: "state.duration = 0L; state.count = 0;",
            map_script: `
              ZoneId london = ZoneId.of("Europe/London");
              ZonedDateTime applicationReceived = doc['filter.keyDates.applicationReceived'].value.withZoneSameInstant(london);
              long duration = params.now - applicationReceived.toEpochSecond();
              state.duration += duration;
              state.count += 1;
            `,
            combine_script: "return state;",
            reduce_script: `
              long total = 0L;
              long count = 0;
              for (shardResult in states) {
                total += shardResult.duration;
                count += shardResult.count;
              }
              return count > 0 ? total / count : null;
            `,
            params: {
              now: Math.floor(Date.now() / 1000),
            },
          },
        },
      },
    },
  },
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
  const agg = body?.aggregations
    ?.timeToAcceptance as OpenSearchTypes.Common_Aggregations.HistogramAggregate;
  const buckets =
    agg?.buckets as (OpenSearchTypes.Common_Aggregations.HistogramBucket & {
      byDecision?: OpenSearchTypes.Common_Aggregations.StringTermsAggregate;
    })[];

  if (!buckets) {
    return [];
  }

  return buckets.map((bucket) => {
    const key = bucket.key;
    const weekNumber = Math.floor(
      (typeof key === "number" ? key : Number(key)) / (7 * 24 * 60 * 60),
    );

    // Count rejected (application_rejected) vs accepted (all others)
    const decisionBuckets =
      (bucket.byDecision
        ?.buckets as OpenSearchTypes.Common_Aggregations.StringTermsBucket[]) ||
      [];
    let rejected = 0;
    let accepted = 0;

    for (const decisionBucket of decisionBuckets) {
      const state =
        typeof decisionBucket.key === "string"
          ? decisionBucket.key
          : String(decisionBucket.key);
      if (state === "application_rejected") {
        rejected += decisionBucket.doc_count ?? 0;
      } else {
        accepted += decisionBucket.doc_count ?? 0;
      }
    }

    return {
      timeRange: weekNumber,
      accepted,
      rejected,
    };
  });
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

const parseApplicationsReceivedPerMonthResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): ApplicationsReceivedPerMonthData => {
  const body = isSearchResponse(response) ? response : undefined;
  const agg = body?.aggregations
    ?.applicationsPerMonth as OpenSearchTypes.Common_Aggregations.DateHistogramAggregate;
  const buckets =
    agg?.buckets as OpenSearchTypes.Common_Aggregations.DateHistogramBucket[];

  if (!buckets) {
    return [];
  }

  return buckets.map((bucket) => {
    const key = bucket.key;
    // key is a timestamp in milliseconds, convert to ISO date string
    const date = new Date(typeof key === "number" ? key : Number(key));
    const monthStr = date.toISOString().split("T")[0]; // YYYY-MM-DD format

    return {
      month: monthStr,
      count: bucket.doc_count ?? 0,
    };
  });
};

const parseAverageDurationsResponse = (
  response: OpenSearchTypes.Core_Msearch.ResponseItem,
): AverageDurations => {
  const body = isSearchResponse(response) ? response : undefined;
  const aggs = body?.aggregations;

  const pendingAgg = aggs?.pending as
    | { avgDuration?: { doc_count?: number; value?: number } }
    | undefined;
  const pendingAverageDuration = pendingAgg?.avgDuration?.value;

  const completedAgg = aggs?.completed as {
    byState?: OpenSearchTypes.Common_Aggregations.StringTermsAggregate;
  };
  const stateBuckets = completedAgg?.byState
    ?.buckets as OpenSearchTypes.Common_Aggregations.StringTermsBucket[];

  const completedAverageDurations: Record<StateCategory, number> = {
    successful: 0,
    unsuccessful: 0,
    withdrawn: 0,
    pending: 0,
  };

  const completedAverageN: Record<StateCategory, number> = {
    successful: 0,
    unsuccessful: 0,
    withdrawn: 0,
    pending: 0,
  };

  for (const bucket of stateBuckets) {
    const state = bucket.key;
    const docCount = bucket.doc_count;
    const avgDuration = (bucket as { avgDuration?: { value?: number } })
      .avgDuration?.value;
    const category = getStateCategory(state?.toString() ?? "");
    if (category && avgDuration !== undefined) {
      completedAverageN[category] += docCount;
      completedAverageDurations[category] +=
        (docCount / completedAverageN[category]) *
        (avgDuration - completedAverageDurations[category]);
    }
  }

  return {
    ...completedAverageDurations,
    pending: pendingAverageDuration,
  };
};

// Single msearch function
export type DashboardData = {
  categoryCounts: CategoryCounts;
  applicationsPerUnion: ApplicationsPerUnionData;
  bargainingUnitSizes: BargainingUnitSizeData;
  timeToAcceptance: TimeToAcceptanceData;
  timeToConclusion: TimeToConclusionData;
  bargainingUnitSizeVsTurnout: BargainingUnitSizeVsTurnoutData;
  averageDurations: AverageDurations;
  applicationsReceivedPerMonth: ApplicationsReceivedPerMonthData;
};

export async function getAllDashboardData(): Promise<DashboardData> {
  "use cache: remote";
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
    { index: outcomesIndex },
    createAverageDurationsRequest(),
    { index: outcomesIndex },
    createApplicationsReceivedPerMonthRequest(),
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
    averageDurations: parseAverageDurationsResponse(responses[6]),
    applicationsReceivedPerMonth: parseApplicationsReceivedPerMonthResponse(
      responses[7],
    ),
  };
}
