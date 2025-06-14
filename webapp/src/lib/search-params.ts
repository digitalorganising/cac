import {
  ParserBuilder,
  createParser,
  createSearchParamsCache,
  createSerializer,
  type inferParserType,
  parseAsArrayOf,
  parseAsBoolean,
  parseAsInteger,
  parseAsIsoDate,
  parseAsString,
  parseAsStringLiteral,
} from "nuqs/server";
import { eventTypes, outcomeStates } from "./types";

const sortKeys = [
  "relevance",
  "lastUpdated",
  "applicationDate",
  "concludedDate",
  "bargainingUnitSize",
] as const;
const sortOrders = ["asc", "desc"] as const;
const sortPermutations = sortKeys.flatMap((key) =>
  sortOrders.map((order): `${typeof key}-${typeof order}` => `${key}-${order}`),
);

export type SortKey = (typeof sortKeys)[number];
export type SortOrder = (typeof sortOrders)[number];

const parseAsUniqueArrayOf = <T>(
  valueParser: ParserBuilder<T>,
  separator?: string,
) => {
  const unique = (value: T[]): T[] => Array.from(new Set(value));
  const arrayParser = parseAsArrayOf(valueParser, separator).withDefault([]);
  return createParser({
    parse: (value: string) => unique(arrayParser.parse(value) ?? []),
    serialize: (value: T[]) => arrayParser.serialize(unique(value)),
    eq: (a, b) => {
      if (a === b) {
        return true;
      }
      if (a.length !== b.length) {
        return false;
      }
      const setB = new Set(b);
      return a.every((v) => setB.has(v));
    },
  }).withDefault([]);
};

export const appSearchParamsParser = {
  query: parseAsString,
  page: parseAsInteger.withDefault(1),
  sort: parseAsStringLiteral(sortPermutations).withDefault("relevance-desc"),
  "parties.unions": parseAsUniqueArrayOf(parseAsString),
  "parties.employer": parseAsUniqueArrayOf(parseAsString),
  reference: parseAsString,
  state: parseAsUniqueArrayOf(parseAsStringLiteral(outcomeStates)),
  "bargainingUnit.size.from": parseAsInteger,
  "bargainingUnit.size.to": parseAsInteger,
  "events.type": parseAsUniqueArrayOf(parseAsStringLiteral(eventTypes)),
  "events.date.from": parseAsIsoDate,
  "events.date.to": parseAsIsoDate,
  debug: parseAsBoolean.withDefault(false),
};

export const appSearchParamsCache = createSearchParamsCache(
  appSearchParamsParser,
);

export const appSearchParamsSerializer = createSerializer(
  appSearchParamsParser,
);

export type AppSearchParams = inferParserType<typeof appSearchParamsParser>;

type SingleValue<K extends keyof AppSearchParams> =
  NonNullable<AppSearchParams[K]> extends (infer V)[]
    ? V
    : NonNullable<AppSearchParams[K]>;

export const addParamValue = <const K extends keyof AppSearchParams>(
  params: AppSearchParams,
  key: K,
  value: SingleValue<K>,
): AppSearchParams => {
  const currentValue = params[key];
  if (Array.isArray(currentValue)) {
    return { ...params, [key]: [...currentValue, value] };
  }
  return { ...params, [key]: [value] };
};

export const deleteParamValue = <const K extends keyof AppSearchParams>(
  params: AppSearchParams,
  key: K,
  value?: SingleValue<K>,
): AppSearchParams => {
  if (value === undefined) {
    return {
      ...params,
      [key]: null,
    };
  }
  if (params[key] === value) {
    return {
      ...params,
      [key]: null,
    };
  }
  if (Array.isArray(params[key])) {
    return {
      ...params,
      [key]: params[key].filter((v) => v !== value),
    };
  }
  return params;
};
