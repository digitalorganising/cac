import "server-only";
import { Client } from "@opensearch-project/opensearch";
import { awsCredentialsProvider } from "@vercel/functions/oidc";
import { AwsSigv4Signer } from "@opensearch-project/opensearch/aws";
import { Outcome } from "@/lib/types";
import { unstable_cache } from "next/cache";
import { SortKey } from "./filtering";

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
};

const getSort = (sortKey?: SortKey, sortOrder?: "asc" | "desc") => {
  const documentKeys = {
    lastUpdated: "last_updated",
    applicationDate: "filter.keyDates.applicationReceived",
    concludedDate: "filter.keyDates.outcomeConcluded",
    bargainingUnitSize: "filter.bargainingUnit.size",
  } as const;
  const tieBreak = { reference: { order: "asc" as const } };

  const documentKey =
    sortKey && sortKey !== "relevance" ? documentKeys[sortKey] : undefined;
  if (sortKey && documentKey) {
    return [{ [documentKey]: { order: sortOrder ?? "desc" } }, tieBreak];
  }

  return [
    { _score: { order: "desc" as const } },
    { last_updated: { order: "desc" as const } },
    tieBreak,
  ];
};

const filterText = (field: string, query?: string[]) =>
  query
    ? query.map((q) => ({
        match: {
          [field]: {
            query: q,
            minimum_should_match: "3<-25%",
          },
        },
      }))
    : [];

export const getOutcomes = unstable_cache(
  async ({
    from,
    size,
    query,
    sortKey,
    sortOrder,
    "parties.unions": unions,
    "parties.employer": employer,
    reference,
  }: GetOutcomesOptions): Promise<{ size: number; docs: Outcome[] }> => {
    const response = await client.search({
      index: "outcomes-indexed",
      body: {
        from,
        size,
        track_total_hits: true,
        query: {
          bool: {
            must: reference
              ? [
                  {
                    terms: { reference },
                  },
                ]
              : [],
            should: query
              ? [
                  {
                    match: {
                      all_decisions: query,
                    },
                  },
                ]
              : [{ match_all: {} }],
            filter: [
              ...filterText("filter.parties.unions", unions),
              ...filterText("filter.parties.employer", employer),
            ],
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
  ["client"],
);
