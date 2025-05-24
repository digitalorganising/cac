import { UrlObject } from "node:url";

type QueryParams = Record<string, string | string[] | undefined>;

export type FilterHref = {
  replace: (key: string, value: string | string[]) => UrlObject;
  add: (key: string, value: string | string[]) => UrlObject;
  delete: (key: string, value?: string | string[]) => UrlObject;
};

export function createFilterHref<
  P extends QueryParams,
  F extends Extract<keyof P, string>,
>({
  searchParams,
  resetOnNavigate,
}: {
  searchParams: P;
  resetOnNavigate: Set<F>;
}): FilterHref {
  const href = (params: P) => ({ pathname: "/", query: params });
  const baseParams = Object.fromEntries(
    Object.entries(searchParams).filter(
      ([key]) => !resetOnNavigate.has(key as F),
    ),
  ) as P;

  return {
    replace: (key: string, value: string | string[]) =>
      href({ [key]: value } as P),
    add: (key: string, value: string | string[]) =>
      href(addQueryParam(baseParams, key, value)),
    delete: (key: string, value?: string | string[]) =>
      href(deleteQueryParam(searchParams, key, value)),
  };
}

function addQueryParam<P extends QueryParams>(
  base: P,
  key: keyof P,
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

function deleteQueryParam<P extends QueryParams>(
  base: P,
  key: keyof P,
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
