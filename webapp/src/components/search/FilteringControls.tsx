import {
  Facets,
  getFacets,
  GetFacetsOptions,
  MultiSelectFacet,
} from "@/lib/queries/facets";
import AppliedFilters, { type FilterEntries } from "./AppliedFilters";
import FacetControls from "./FacetControls";
import { Suspense } from "react";
import { filterLabels } from "./common";
import { SelectTrigger } from "../ui/multi-select";
import { arr } from "@/lib/utils";
import { DateRange } from "../ui/date-range";
import { appSearchParamsCache } from "@/lib/search-params";
import { Entries } from "type-fest";

type Props = {
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
          label:
            Object.values(
              facets.multiSelect[key as MultiSelectFacet] ?? {},
            )?.find((f) => f.value === entry.value)?.label ?? entry.value,
        })),
      ],
    ),
  ) as FilterEntries;
  return <AppliedFilters filterEntries={filterEntriesWithLabels} />;
}

export default function FilteringControls({ options }: Props) {
  const facetsPromise = getFacets(options);
  const params = appSearchParamsCache.all();
  const appliedFilters = Object.fromEntries(
    Object.entries(params)
      .filter((kv) => kv[0] in filterLabels && kv[1] !== null)
      .map(([key, value]) => [key, arr(value).map((v) => ({ value: v }))]),
  ) as FilterEntries;
  return (
    <div className="my-4 space-y-2">
      <div className="flex flex-wrap gap-2">
        <Suspense fallback={<AppliedFilters filterEntries={appliedFilters} />}>
          <AppliedLabelledFilters
            filterEntries={appliedFilters}
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
