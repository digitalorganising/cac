import {
  Client,
  Types as OpenSearchTypes,
} from "@opensearch-project/opensearch";
import "server-only";
import { SortKey, SortOrder } from "../search-params";
import { getSecret } from "../secrets";

let _client: Client | undefined = undefined;
export const getClient = async () => {
  if (_client) {
    return _client;
  }

  const secret = await getSecret(process.env.OPENSEARCH_CREDENTIALS_SECRET!);
  if (!secret) {
    throw new Error("Failed to get opensearch credentials");
  }
  const { username, password } = JSON.parse(secret);
  _client = new Client({
    node: process.env.OPENSEARCH_ENDPOINT!,
    auth: {
      username,
      password,
    },
  });
  return _client;
};

export const outcomesIndex = process.env.OUTCOMES_INDEX!;

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
  "duration.from"?: number;
  "duration.to"?: number;
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
  "duration.from": durationFrom,
  "duration.to": durationTo,
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
    filterRange("duration.value", durationFrom, durationTo),
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
