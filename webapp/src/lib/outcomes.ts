import "server-only";
import { Client } from "@opensearch-project/opensearch";
import { awsCredentialsProvider } from "@vercel/functions/oidc";
import { AwsSigv4Signer } from "@opensearch-project/opensearch/aws";
import { Outcome } from "@/lib/types";
import { unstable_cache } from "next/cache";

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

type GetOutcomesOptions = {
  from: number;
  size: number;
  query?: string;
  "parties.unions"?: string;
  "parties.employer"?: string;
  reference?: string;
};

const filterText = (field: string, query?: string) =>
  query
    ? [
        {
          match: {
            [field]: {
              query,
              minimum_should_match: "3<-25%",
            },
          },
        },
      ]
    : [];

export const getOutcomes = unstable_cache(
  async ({
    from,
    size,
    query,
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
                    term: { reference },
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
        sort: [
          { _score: { order: "desc" } },
          { last_updated: { order: "desc" } },
        ],
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
