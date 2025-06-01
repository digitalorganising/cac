import "server-only";

import {
  Client,
  Types as OpenSearchTypes,
} from "@opensearch-project/opensearch";
import { AwsSigv4Signer } from "@opensearch-project/opensearch/aws";
import { awsCredentialsProvider } from "@vercel/functions/oidc";
import { SortKey } from "../filtering";

export const client = new Client({
  ...AwsSigv4Signer({
    region: process.env.AWS_REGION!,
    service: "es",
    getCredentials: awsCredentialsProvider({
      roleArn: process.env.AWS_ROLE_ARN!,
    }),
  }),
  node: process.env.OPENSEARCH_ENDPOINT!,
});

export const outcomesIndex = "outcomes-2025-05-31-indexed";

export type PaginationOptions = {
  from: number;
  size: number;
};

export type SortOptions = {
  sortKey?: SortKey;
  sortOrder?: "asc" | "desc";
};

export type QueryOptions = {
  query?: string;
};

export type FilterOptions = {
  "parties.unions"?: string[];
  "parties.employer"?: string[];
  reference?: string[];
  state?: string[];
  "events.type"?: string[];
};

const filterPrefix = "filter.";

const filterMatch = (name: string) => (query: string) => ({
  match: {
    [filterPrefix + name]: {
      query,
      minimum_should_match: "3<-25%",
    },
  },
});

const filterText = (name: string, query?: string[]) => {
  if (!query) {
    return [];
  }

  if (query.length === 1) {
    return [filterMatch(name)(query[0])];
  }

  return [
    {
      bool: {
        should: query.map(filterMatch(name)),
        _name: `filter-${name}`,
      },
    },
  ];
};

const filterKeyword = (name: string, query?: string[]) => {
  if (!query) {
    return [];
  }

  return [
    {
      terms: {
        [filterPrefix + name]: query,
        _name: `filter-${name}`,
      },
    },
  ];
};

export const getFilters = ({
  "parties.unions": unions,
  "parties.employer": employer,
  reference,
  state,
  "events.type": eventsType,
}: FilterOptions): OpenSearchTypes.Common_QueryDsl.QueryContainer[] =>
  [
    filterText("parties.unions", unions),
    filterText("parties.employer", employer),
    filterKeyword("state", state),
    filterKeyword("events.type", eventsType),
    filterKeyword("reference", reference),
  ].flat();

export const getQuery = ({ query }: QueryOptions) =>
  query
    ? [
        {
          match: {
            full_text: query,
          },
        },
      ]
    : [{ match_all: {} }];
