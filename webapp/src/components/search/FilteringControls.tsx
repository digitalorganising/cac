import { FilterHref } from "@/lib/filtering";
import { Filters } from "@/lib/types";
import { Facets, getFacets, GetFacetsOptions } from "@/lib/queries/facets";
import AppliedFilters, { FilterEntries } from "./AppliedFilters";
import FacetControls from "./FacetControls";
import { Suspense } from "react";
import { filterLabels } from "./common";
import { SelectTrigger } from "../ui/multi-select";
import { arr } from "@/lib/utils";
import { DateRange } from "../ui/date-range";

type Props = {
  filterHref: FilterHref;
  options: GetFacetsOptions;
};

function FacetFallback() {
  return (
    <>
      {["Unions", "Status", "Events"].map((label) => (
        <SelectTrigger
          key={label}
          loading={true}
          aria-label={`${label} filter`}
        >
          {label}
        </SelectTrigger>
      ))}
      <DateRange />
    </>
  );
}

async function AppliedLabelledFilters({
  filterEntries,
  filterHref,
  facetsPromise,
}: {
  filterEntries: Record<keyof Filters, { value: string; label?: string }[]>;
  filterHref: FilterHref;
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  const filterEntriesWithLabels = Object.fromEntries(
    Object.entries(filterEntries).map(([key, entries]) => [
      key,
      entries.map((entry) => ({
        ...entry,
        label:
          facets.bucketed[key as keyof Facets["bucketed"]]?.find(
            (f) => f.value === entry.value,
          )?.label ?? entry.value,
      })),
    ]),
  ) as FilterEntries;
  return (
    <AppliedFilters
      filterEntries={filterEntriesWithLabels}
      filterHref={filterHref}
    />
  );
}

export default function FilteringControls({ filterHref, options }: Props) {
  const facetsPromise = getFacets(options);
  const appliedFilters = Object.fromEntries(
    Object.entries(filterHref.params)
      .filter(
        (kv): kv is [keyof Filters, string | string[]] =>
          kv[0] in filterLabels && kv[1] !== undefined,
      )
      .map(([key, value]) => [key, arr(value).map((v) => ({ value: v }))]),
  ) as FilterEntries;
  return (
    <div className="my-4 space-y-2">
      <div className="flex flex-wrap gap-2">
        <Suspense
          fallback={
            <AppliedFilters
              filterEntries={appliedFilters}
              filterHref={filterHref}
            />
          }
        >
          <AppliedLabelledFilters
            filterEntries={appliedFilters}
            filterHref={filterHref}
            facetsPromise={facetsPromise}
          />
        </Suspense>
      </div>
      <div className="flex flex-wrapitems-center justify-start gap-4 py-4">
        <Suspense fallback={<FacetFallback />}>
          <FacetControls facetsPromise={facetsPromise} />
        </Suspense>
      </div>
    </div>
  );
}
