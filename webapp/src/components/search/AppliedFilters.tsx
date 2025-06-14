import { Cross2Icon } from "@radix-ui/react-icons";
import Link from "next/link";
import React from "react";
import { Entries } from "type-fest";
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

const renderValue = (value?: string | Date | number): string | undefined => {
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

export default function AppliedFilters({
  filterEntries,
}: {
  filterEntries: FilterEntries;
}) {
  const params = appSearchParamsCache.all();
  return (Object.entries(filterEntries) as Entries<FilterEntries>).flatMap(
    ([key, entries]) =>
      entries.map(({ value, label }) => (
        <Link
          key={`filter-${key}-${value}`}
          href={
            appSearchParamsSerializer(deleteParamValue(params, key, value)) ||
            "/"
          }
          className="flex gap-x-2 items-center bg-slate-100 rounded-md px-3 py-2 border border-slate-200 group"
        >
          <span className="text-sm text-nowrap">
            <strong className="font-semibold">{filterLabels[key]}</strong>:{" "}
            <span className="no-underline group-hover:underline">
              {label ?? renderValue(value)}
            </span>
          </span>
          <Cross2Icon className="size-3 text-slate-500 group-hover:text-slate-700" />
        </Link>
      )),
  );
}
