import "server-only";
import {
  Client,
  Types as OpenSearchTypes,
} from "@opensearch-project/opensearch";
import { awsCredentialsProvider } from "@vercel/functions/oidc";
import { AwsSigv4Signer } from "@opensearch-project/opensearch/aws";
import { Outcome } from "@/lib/types";
import { unstable_cache } from "next/cache";
import { Filters, SortKey } from "./filtering";

const client = new Client({
  ...AwsSigv4Signer({
    region: process.env.AWS_REGION!,
    service: "es",
    getCredentials: awsCredentialsProvider({
      roleArn: process.env.AWS_ROLE_ARN!,
    }),
  }),
  node: process.env.OPENSEARCH_ENDPOINT!,
});

export type GetOutcomesOptions = {
  from: number;
  size: number;
  sortKey?: SortKey;
  sortOrder?: "asc" | "desc";
  query?: string;
  "parties.unions"?: string[];
  "parties.employer"?: string[];
  reference?: string[];
  state?: string[];
  "events.type"?: string[];
  "events.date.from"?: string;
  "events.date.to"?: string;
  "bargainingUnit.size.from"?: string;
  "bargainingUnit.size.to"?: string;
};

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

const filterMatch = (field: string) => (query: string) => ({
  match: {
    [field]: {
      query,
      minimum_should_match: "3<-25%",
    },
  },
});

const filterText = (field: string, query?: string[]) => {
  if (!query) {
    return [];
  }

  if (query.length === 1) {
    return [filterMatch(field)(query[0])];
  }

  return [
    {
      bool: {
        should: query.map(filterMatch(field)),
      },
    },
  ];
};

const filterKeyword = (field: string, query?: string[]) => {
  if (!query) {
    return [];
  }

  return [
    {
      terms: {
        [field]: query,
      },
    },
  ];
};

type QueryOptions = {
  query?: string;
  "parties.unions"?: string[];
  "parties.employer"?: string[];
  state?: string[];
  "events.type"?: string[];
  reference?: string[];
};

const getQuery = ({
  query,
  "parties.unions": unions,
  "parties.employer": employer,
  state,
  "events.type": eventsType,
  reference,
}: QueryOptions) => ({
  bool: {
    should: query
      ? [
          {
            match: {
              full_text: query,
            },
          },
        ]
      : [{ match_all: {} }],
    filter: [
      filterText("filter.parties.unions", unions),
      filterText("filter.parties.employer", employer),
      filterKeyword("filter.state", state),
      filterKeyword("filter.events.type", eventsType),
      filterKeyword("filter.reference", reference),
    ].flat(),
  },
});

const outcomesIndex = "outcomes-2025-05-31-indexed";

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
        query: getQuery(queryOptions),
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
  ["client"],
);

const facetPrefix = "facet.";

const termsAgg = (name: string) => ({
  [name]: {
    terms: {
      field: name,
      size: 50,
    },
  },
});

const aggIsFacet = (
  agg: [string, OpenSearchTypes.Common_Aggregations.Aggregate],
): agg is [string, OpenSearchTypes.Common_Aggregations.StringTermsAggregate] =>
  agg[0].startsWith(facetPrefix) && "buckets" in agg[1];

const getFacetProps = (key: string): { value: string; label?: string } => {
  const p = JSON.parse(key);
  if (typeof p === "string") {
    return { value: p };
  }

  return { value: p.value, label: p.label };
};

export type Facets = Record<
  keyof Filters,
  { value: string; label?: string; count: number }[]
>;

export const getFacets = unstable_cache(
  async (queryOptions: QueryOptions): Promise<Facets> => {
    const response = await client.search({
      index: outcomesIndex,
      body: {
        size: 0,
        query: getQuery(queryOptions),
        aggs: {
          ...termsAgg("facet.parties.unions"),
          ...termsAgg("facet.state"),
          ...termsAgg("facet.events.type"),
        },
      },
    });

    const aggs = response.body.aggregations;
    const facets = Object.fromEntries(
      Object.entries(aggs ?? {})
        .filter(aggIsFacet)
        .map(([name, agg]) => [
          name.slice(facetPrefix.length),
          (
            agg.buckets as OpenSearchTypes.Common_Aggregations.StringTermsBucket[]
          ).map(({ key, doc_count }) => ({
            ...getFacetProps(key as string),
            count: doc_count,
          })),
        ]),
    ) as Facets;

    return facets;
  },
  ["client"],
);
