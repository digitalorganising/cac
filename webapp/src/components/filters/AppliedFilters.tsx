import type { Entries, Except } from "type-fest";
import { GetOutcomesOptions } from "@/lib/outcomes";
import React from "react";
import { cn, deleteQueryParam } from "@/lib/utils";
import { Cross2Icon } from "@radix-ui/react-icons";
import Link from "next/link";

type Filters = Except<GetOutcomesOptions, "from" | "size" | "query">;

const singularFilterLabels: Record<keyof Filters, string> = {
  "parties.unions": "Union",
  "parties.employer": "Employer",
  reference: "Reference",
};

const pluralFilterLabels: Record<keyof Filters, string> = {
  "parties.unions": "Unions",
  "parties.employer": "Employers",
  reference: "References",
};

const Filter = <F extends keyof Filters>({
  filterKey,
  value,
  searchParams,
}: {
  filterKey: F;
  value: NonNullable<Filters[F]>;
  searchParams: { [key: string]: string | string[] | undefined };
}) => (
  <Link
    href={{
      pathname: "/",
      query: deleteQueryParam(searchParams, filterKey, value),
    }}
    className="flex gap-x-2 items-center bg-slate-100 rounded-md px-3 py-2 border border-slate-200 group"
  >
    <span className="text-sm text-nowrap">
      <strong className="font-semibold">
        {value.length > 1
          ? pluralFilterLabels[filterKey]
          : singularFilterLabels[filterKey]}
      </strong>
      :{" "}
      <span className="no-underline group-hover:underline">
        {value.join(", ")}
      </span>
    </span>
    <Cross2Icon className="size-3 text-slate-500 group-hover:text-slate-700" />
  </Link>
);

export default function AppliedFilters({
  filters,
  className,
  searchParams,
  ...otherProps
}: {
  filters: Filters;
  searchParams: { [key: string]: string | string[] | undefined };
} & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex flex-wrap gap-2", className)} {...otherProps}>
      {(Object.entries(filters) as Entries<Filters>)
        .filter((kv): kv is [keyof Filters, string[]] => kv[1] !== undefined)
        .map(([key, value]) => (
          <Filter
            key={key}
            filterKey={key}
            value={value}
            searchParams={searchParams}
          />
        ))}
    </div>
  );
}
