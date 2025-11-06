import { Cross2Icon } from "@radix-ui/react-icons";
import Link from "next/link";
import React from "react";
import { Entries } from "type-fest";
import { formatSecondsDuration } from "@/lib/duration";
import { Facets, MultiSelectFacet } from "@/lib/queries/facets";
import {
  AppSearchParams,
  appSearchParamsCache,
  appSearchParamsSerializer,
  deleteParamValue,
} from "@/lib/search-params";
import { filterLabels, humanizeDate } from "./common";

export type FilterEntries = Record<
  keyof AppSearchParams,
  { value: string | Date | number; label?: string }[]
>;

const renderValue = (
  value?: string | Date | number,
  key?: keyof AppSearchParams,
): string | undefined => {
  // TODO: make this less terrible; renderers for each key
  if (key === "durations.overall.from" || key === "durations.overall.to") {
    return formatSecondsDuration(value as number);
  }
  if (typeof value === "string") {
    return value;
  }
  if (value instanceof Date) {
    return humanizeDate(value);
  }
  if (typeof value === "number") {
    return value.toString();
  }
  return value;
};

export async function AppliedLabelledFilters({
  filterEntries,
  facetsPromise,
}: {
  filterEntries: FilterEntries;
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  const filterEntriesWithLabels = Object.fromEntries(
    (Object.entries(filterEntries) as Entries<FilterEntries>).map(
      ([key, entries]) => [
        key,
        entries.map((entry) => ({
          ...entry,
          label: Object.values(
            facets.multiSelect[key as MultiSelectFacet] ?? {},
          )?.find((f) => f.value === entry.value)?.label,
        })),
      ],
    ),
  ) as FilterEntries;
  return <AppliedFilters filterEntries={filterEntriesWithLabels} />;
}

export default function AppliedFilters({
  filterEntries,
}: {
  filterEntries: FilterEntries;
}) {
  const params = appSearchParamsCache.all();
  const nAppliedFilters = Object.values(filterEntries).flat().length;
  return (
    <div className="flex flex-wrap gap-2">
      {(Object.entries(filterEntries) as Entries<FilterEntries>).flatMap(
        ([key, entries]) =>
          entries.map(({ value, label }) => (
            <Link
              key={`filter-${key}-${value}`}
              href={
                appSearchParamsSerializer(
                  deleteParamValue(params, key, value),
                ) || "/"
              }
              className="flex gap-x-2 items-center bg-slate-100 rounded-md px-3 py-2 border border-slate-200 group"
            >
              <span className="text-sm text-nowrap">
                <strong className="font-semibold">{filterLabels[key]}</strong>:{" "}
                <span className="no-underline group-hover:underline">
                  {label ?? renderValue(value, key)}
                </span>
              </span>
              <Cross2Icon className="size-3 text-slate-500 group-hover:text-slate-700" />
            </Link>
          )),
      )}
      {nAppliedFilters > 1 ? (
        <Link
          href={appSearchParamsSerializer({ query: params.query }) || "/"}
          className="flex gap-x-2 items-center bg-transparent rounded-md px-3 py-2 border border-slate-200 group"
        >
          <span className="text-sm text-nowrap group-hover:underline font-semibold">
            Clear all filters
          </span>
          <Cross2Icon className="size-3 text-slate-500 group-hover:text-slate-700" />
        </Link>
      ) : null}
    </div>
  );
}
