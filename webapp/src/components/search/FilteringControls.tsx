import { MixerHorizontalIcon } from "@radix-ui/react-icons";
import { Loader2Icon } from "lucide-react";
import { Suspense } from "react";
import { Entries } from "type-fest";
import {
  Facets,
  GetFacetsOptions,
  MultiSelectFacet,
  getFacets,
} from "@/lib/queries/facets";
import { appSearchParamsCache } from "@/lib/search-params";
import { arr } from "@/lib/utils";
import { Button } from "../ui/button";
import CountBadge from "../ui/count-badge";
import { DateRange } from "../ui/date-range";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { HistogramSliderTrigger } from "../ui/histogram-slider";
import { SelectTrigger } from "../ui/multi-select";
import AppliedFilters, { type FilterEntries } from "./AppliedFilters";
import FacetControls from "./FacetControls";
import MobileFacetControls from "./MobileFacetControls";
import { filterLabels } from "./common";

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
      <DateRange loading={true} />
      <HistogramSliderTrigger loading={true}>
        Bargaining Unit Size
      </HistogramSliderTrigger>
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
  const facetsPromise = getFacets(options, appSearchParamsCache.get("debug"));
  const params = appSearchParamsCache.all();
  const appliedFilters = Object.fromEntries(
    Object.entries(params)
      .filter((kv) => kv[0] in filterLabels && kv[1] !== null)
      .map(([key, value]) => [key, arr(value).map((v) => ({ value: v }))]),
  ) as FilterEntries;
  const nAppliedFilters = Object.values(appliedFilters).flat().length;
  return (
    <>
      <div className="my-4 space-y-2 hidden sm:block">
        <div className="flex flex-wrap gap-2">
          <Suspense
            fallback={<AppliedFilters filterEntries={appliedFilters} />}
          >
            <AppliedLabelledFilters
              filterEntries={appliedFilters}
              facetsPromise={facetsPromise}
            />
          </Suspense>
        </div>
        <div className="flex flex-wrap items-center justify-start gap-x-3 xl:gap-x-4 gap-y-3 py-4">
          <Suspense fallback={<FacetFallback />}>
            <FacetControls facetsPromise={facetsPromise} />
          </Suspense>
        </div>
      </div>
      <div className="sm:hidden">
        <Dialog>
          <DialogTrigger asChild>
            <Button
              variant="outline"
              className="w-full bg-slate-100 py-4 xs:py-6 mt-2 mb-3"
              title="Filters"
            >
              <MixerHorizontalIcon />
              Filters
              {nAppliedFilters > 0 ? (
                <CountBadge count={nAppliedFilters} />
              ) : null}
            </Button>
          </DialogTrigger>
          <DialogContent className="size-full block">
            <DialogHeader>
              <DialogTitle>Filters</DialogTitle>
            </DialogHeader>
            <Suspense
              fallback={
                <div className="w-full h-full relative">
                  <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 animate-spin">
                    <Loader2Icon className="size-10" />
                  </div>
                </div>
              }
            >
              <MobileFacetControls facetsPromise={facetsPromise} />
            </Suspense>
          </DialogContent>
        </Dialog>
      </div>
    </>
  );
}
