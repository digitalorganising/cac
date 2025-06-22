import {
  Client,
  Types as OpenSearchTypes,
} from "@opensearch-project/opensearch";
import { AwsSigv4Signer } from "@opensearch-project/opensearch/aws";
import { awsCredentialsProvider } from "@vercel/functions/oidc";
import "server-only";
import { SortKey, SortOrder } from "../search-params";

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

export const outcomesIndex = "outcomes-merged-indexed";

export type PaginationOptions = {
  from: number;
  size: number;
};

export type SortOptions = {
  sortKey?: SortKey;
  sortOrder?: SortOrder;
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
  "events.date.from"?: string;
  "events.date.to"?: string;
  "bargainingUnit.size.from"?: number;
  "bargainingUnit.size.to"?: number;
};

export const filterPrefix = "filter.";

const filterMatch = (name: string) => (query: string) => ({
  match: {
    [filterPrefix + name]: {
      query,
      minimum_should_match: "3<-25%",
      _name: `filter-${name}`,
    },
  },
});

const filterText = (name: string, query?: string[]) => {
  if (!query || query.length === 0) {
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
  if (!query || query.length === 0) {
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

const filterRange = <T extends string | number>(
  name: string,
  from?: T,
  to?: T,
) => {
  if (!from && !to) {
    return [];
  }

  return [
    {
      range: {
        [filterPrefix + name]: {
          gte: from,
          lte: to,
          _name: `filter-${name}`,
        },
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
  "events.date.from": eventsDateFrom,
  "events.date.to": eventsDateTo,
  "bargainingUnit.size.from": bargainingUnitSizeFrom,
  "bargainingUnit.size.to": bargainingUnitSizeTo,
}: FilterOptions): OpenSearchTypes.Common_QueryDsl.QueryContainer[] =>
  [
    filterText("parties.unions", unions),
    filterText("parties.employer", employer),
    filterKeyword("state", state),
    filterKeyword("events.type", eventsType),
    filterKeyword("reference", reference),
    filterRange("events.date", eventsDateFrom, eventsDateTo),
    filterRange(
      "bargainingUnit.size",
      bargainingUnitSizeFrom,
      bargainingUnitSizeTo,
    ),
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
