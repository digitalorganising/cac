import React from "react";
import { Cross2Icon } from "@radix-ui/react-icons";
import Link from "next/link";
import { FilterHref, Filters } from "@/lib/filtering";
import { filterLabels } from "./common";
import { Entries } from "type-fest";

export type FilterEntries = Record<
  keyof Filters,
  { value: string; label?: string }[]
>;

export default function AppliedFilters({
  filterEntries,
  filterHref,
}: {
  filterEntries: FilterEntries;
  filterHref: FilterHref;
}) {
  return (Object.entries(filterEntries) as Entries<FilterEntries>).flatMap(
    ([key, entries]) =>
      entries.map(({ value, label }) => (
        <Link
          key={`filter-${key}-${value}`}
          href={filterHref.delete(key, value).urlObject}
          className="flex gap-x-2 items-center bg-slate-100 rounded-md px-3 py-2 border border-slate-200 group"
        >
          <span className="text-sm text-nowrap">
            <strong className="font-semibold">{filterLabels[key]}</strong>:{" "}
            <span className="no-underline group-hover:underline">
              {label ?? value}
            </span>
          </span>
          <Cross2Icon className="size-3 text-slate-500 group-hover:text-slate-700" />
        </Link>
      )),
  );
}
