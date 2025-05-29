import type { Entries, Except } from "type-fest";
import React from "react";
import { cn } from "@/lib/utils";
import { Cross2Icon } from "@radix-ui/react-icons";
import Link from "next/link";
import { AppQueryParams, FilterHref } from "@/lib/filtering";

type Filters = Pick<
  AppQueryParams,
  "parties.unions" | "parties.employer" | "reference"
>;

const singularFilterLabels: Record<keyof Filters, string> = {
  "parties.unions": "Union",
  "parties.employer": "Employer",
  reference: "Reference",
};

const Filter = <F extends keyof Filters>({
  filterKey,
  value,
  filterHref,
}: {
  filterKey: F;
  value: NonNullable<Filters[F]>;
  filterHref: FilterHref;
}) =>
  (Array.isArray(value) ? value : [value]).map((v) => (
    <Link
      key={`filter-${filterKey}-${v}`}
      href={filterHref.delete(filterKey, value).urlObject}
      className="flex gap-x-2 items-center bg-slate-100 rounded-md px-3 py-2 border border-slate-200 group"
    >
      <span className="text-sm text-nowrap">
        <strong className="font-semibold">
          {singularFilterLabels[filterKey]}
        </strong>
        : <span className="no-underline group-hover:underline">{v}</span>
      </span>
      <Cross2Icon className="size-3 text-slate-500 group-hover:text-slate-700" />
    </Link>
  ));

export default function AppliedFilters({
  params,
  className,
  filterHref,
  ...otherProps
}: {
  params: AppQueryParams;
  filterHref: FilterHref;
} & React.HTMLAttributes<HTMLDivElement>) {
  const appliedFilters = Object.entries(params).filter(
    (kv): kv is [keyof Filters, string[]] =>
      kv[0] in singularFilterLabels && kv[1] !== undefined,
  );

  if (appliedFilters.length === 0) {
    return null;
  }

  return (
    <div className={cn("flex flex-wrap gap-2", className)} {...otherProps}>
      {appliedFilters.map(([key, value]) => (
        <Filter
          key={key}
          filterKey={key}
          value={value}
          filterHref={filterHref}
        />
      ))}
    </div>
  );
}
