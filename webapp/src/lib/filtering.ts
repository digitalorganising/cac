import type { UrlObject } from "node:url";
import { GetOutcomesOptions } from "./outcomes";

type Param = string | string[] | undefined;

export type AppQueryParams = Record<
  | "query"
  | "page"
  | "sort"
  | "parties.unions"
  | "parties.employer"
  | "reference"
  | "state"
  | "bargainingUnit.size.from"
  | "bargainingUnit.size.to"
  | "events.type"
  | "events.date.from"
  | "events.date.to"
  | "debug",
  Param
>;

export type SortKey =
  | "relevance"
  | "lastUpdated"
  | "applicationDate"
  | "concludedDate"
  | "bargainingUnitSize";
export type SortOrder = "asc" | "desc";

type ParamKey = keyof AppQueryParams;

const singleValue = <T extends string = string>(value: Param): T | undefined =>
  (Array.isArray(value) ? value[value.length - 1] : value) as T | undefined;

const multiValue = <T extends string = string>(
  value: Param,
): T[] | undefined =>
  value !== undefined
    ? ((Array.isArray(value) ? value : [value]) as T[])
    : undefined;

export function appQueryParamsToOutcomesOptions(
  pageSize: number,
  params: AppQueryParams,
): GetOutcomesOptions {
  const [sortKey, sortOrder]: [SortKey | undefined, SortOrder | undefined] =
    (singleValue(params.sort)?.split("-") as [SortKey, SortOrder]) ?? [
      undefined,
      undefined,
    ];
  return {
    from: pageSize * (parseInt(singleValue(params.page) ?? "1") - 1),
    size: pageSize,
    query: singleValue(params.query),
    "parties.unions": multiValue(params["parties.unions"]),
    "parties.employer": multiValue(params["parties.employer"]),
    reference: multiValue(params.reference),
    state: multiValue(params.state),
    "bargainingUnit.size.from": singleValue(params["bargainingUnit.size.from"]),
    "bargainingUnit.size.to": singleValue(params["bargainingUnit.size.to"]),
    "events.type": multiValue(params["events.type"]),
    "events.date.from": singleValue(params["events.date.from"]),
    "events.date.to": singleValue(params["events.date.to"]),
    sortKey,
    sortOrder,
  };
}

type Href = {
  urlObject: UrlObject;
  urlString: string;
};

export type FilterHref = {
  replace: (key: ParamKey, value: string | string[]) => Href;
  add: (key: ParamKey, value: string | string[]) => Href;
  delete: (key: ParamKey, value?: string | string[]) => Href;
};

export function createFilterHref({
  searchParams,
  resetOnNavigate,
  pathname = "/",
}: {
  searchParams: AppQueryParams;
  resetOnNavigate: Set<ParamKey>;
  pathname?: string;
}): FilterHref {
  const href = (params: AppQueryParams) => ({
    urlObject: { pathname, query: params },
    urlString:
      pathname +
      "?" +
      new URLSearchParams(
        Object.entries(params).flatMap(([key, value]) =>
          Array.isArray(value)
            ? value.map((v) => [key, v])
            : value === undefined
              ? []
              : [[key, value]],
        ),
      ).toString(),
  });

  const baseParams = Object.fromEntries(
    Object.entries(searchParams).filter(
      ([key]) => !resetOnNavigate.has(key as ParamKey),
    ),
  ) as AppQueryParams;

  return {
    replace: (key: ParamKey, value: string | string[]) =>
      href({ [key]: value } as AppQueryParams),
    add: (key: ParamKey, value: string | string[]) =>
      href(addQueryParam(baseParams, key, value)),
    delete: (key: ParamKey, value?: string | string[]) =>
      href(deleteQueryParam(searchParams, key, value)),
  };
}

function addQueryParam(
  base: AppQueryParams,
  key: ParamKey,
  value: string | string[],
) {
  if (Array.isArray(base[key]) && Array.isArray(value)) {
    return { ...base, [key]: [...new Set([...base[key], ...value])] };
  }

  if (Array.isArray(base[key]) && typeof value === "string") {
    return { ...base, [key]: [...new Set([...base[key], value])] };
  }

  if (typeof base[key] === "string" && Array.isArray(value)) {
    return { ...base, [key]: [...new Set([base[key], ...value])] };
  }

  if (
    typeof base[key] === "string" &&
    typeof value === "string" &&
    base[key] !== value
  ) {
    return { ...base, [key]: [base[key], value] };
  }

  return { ...base, [key]: value };
}

function deleteQueryParam(
  base: AppQueryParams,
  key: ParamKey,
  value?: string | string[],
) {
  if (value === undefined) {
    return { ...base, [key]: undefined };
  }

  if (Array.isArray(base[key]) && Array.isArray(value)) {
    return { ...base, [key]: base[key].filter((v) => !value.includes(v)) };
  }

  if (Array.isArray(base[key]) && typeof value === "string") {
    return { ...base, [key]: base[key].filter((v) => v !== value) };
  }

  if (
    typeof base[key] === "string" &&
    Array.isArray(value) &&
    value.includes(base[key])
  ) {
    return { ...base, [key]: undefined };
  }

  if (
    typeof base[key] === "string" &&
    typeof value === "string" &&
    base[key] === value
  ) {
    return { ...base, [key]: undefined };
  }

  return base;
}
