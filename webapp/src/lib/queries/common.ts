import { Types as OpenSearchTypes } from "@opensearch-project/opensearch";
import "server-only";
import { SortKey, SortOrder } from "../search-params";

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
  "durations.overall.from"?: number;
  "durations.overall.to"?: number;
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

const filterDuration = (from?: number, to?: number) => {
  if (!from && !to) {
    return [];
  }

  return [
    {
      bool: {
        should: [
          {
            bool: {
              filter: [
                {
                  term: {
                    [filterPrefix + "duration.relation"]: "eq",
                  },
                },
                ...filterRange("duration.value", from, to),
              ],
            },
          },
          {
            bool: {
              filter: [
                {
                  term: {
                    [filterPrefix + "duration.relation"]: "gte",
                  },
                },
                {
                  script: {
                    script: {
                      source: `
                        ZoneId london = ZoneId.of("Europe/London");
                        ZonedDateTime applicationReceived = doc['filter.keyDates.applicationReceived'].value.withZoneSameInstant(london);
                        long duration = params.now - applicationReceived.toEpochSecond();
                        if (params.from != null && params.to != null) {
                          return duration >= params.from && duration <= params.to;
                        } else if (params.from != null) {
                          return duration >= params.from;
                        } else {
                          return duration <= params.to;
                        }
                    `,
                      params: {
                        from: from ?? null,
                        to: to ?? null,
                        now: Math.floor(Date.now() / 1000),
                      },
                    },
                  },
                },
              ],
            },
          },
        ],
        _name: `filter-duration`,
      },
    } as OpenSearchTypes.Common_QueryDsl.QueryContainer,
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
  "durations.overall.from": durationsOverallFrom,
  "durations.overall.to": durationsOverallTo,
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
    filterDuration(durationsOverallFrom, durationsOverallTo),
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
