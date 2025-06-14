import {
  BarChartIcon,
  ChevronDownIcon,
  Cross2Icon,
  MixerHorizontalIcon,
} from "@radix-ui/react-icons";
import { Loader2Icon } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import { Entries } from "type-fest";
import {
  Facets,
  GetFacetsOptions,
  MultiSelectFacet,
  getFacets,
} from "@/lib/queries/facets";
import {
  appSearchParamsCache,
  appSearchParamsSerializer,
} from "@/lib/search-params";
import { arr } from "@/lib/utils";
import { Button } from "../ui/button";
import CountBadge from "../ui/count-badge";
import { DateRange } from "../ui/date-range";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { InputTriggerButton } from "../ui/input-trigger-button";
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
        <InputTriggerButton
          key={label}
          loading={true}
          aria-label={`${label} filter`}
          icon={<ChevronDownIcon className="size-4 opacity-50" />}
        >
          {label}
        </InputTriggerButton>
      ))}
      <DateRange loading={true} />
      <InputTriggerButton loading={true} icon={<BarChartIcon />}>
        Bargaining Unit Size
      </InputTriggerButton>
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
          label: Object.values(
            facets.multiSelect[key as MultiSelectFacet] ?? {},
          )?.find((f) => f.value === entry.value)?.label,
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
          <DialogContent
            className="w-full h-[calc(100%-(var(--spacing)*18)+1px)] block top-0 left-0 translate-none rounded-b-none"
            sheet={
              <div className="fixed h-18 z-250 bottom-0 left-0 bg-white border-t border-gray-200 w-full p-4 flex justify-end items-center gap-2">
                <DialogClose asChild>
                  <Button className="cursor-pointer" variant="outline" asChild>
                    <Link
                      href={
                        appSearchParamsSerializer({ query: params.query }) ||
                        "/"
                      }
                    >
                      Clear all
                    </Link>
                  </Button>
                </DialogClose>
                <DialogClose asChild>
                  <Button className="cursor-pointer">Show results</Button>
                </DialogClose>
              </div>
            }
          >
            <DialogHeader>
              <DialogTitle>Filters</DialogTitle>
              <DialogDescription className="sr-only">
                Filters for searching outcomes
              </DialogDescription>
            </DialogHeader>
            {appliedFilters["reference"] ? (
              <DialogClose asChild>
                <Link
                  href={
                    appSearchParamsSerializer({
                      ...params,
                      reference: null,
                    }) || "/"
                  }
                  className="flex p-2 mb-2 mt-3 text-sm w-full items-center space-x-2 justify-center mx-auto border border-slate-200 bg-slate-100 rounded-md"
                >
                  <div>
                    <span className="font-medium">Reference:</span>{" "}
                    {appliedFilters["reference"].map((r) => r.value).join(", ")}
                  </div>
                  <button
                    className="cursor-pointer"
                    title="Clear reference filter"
                  >
                    <Cross2Icon className="size-3" />
                  </button>
                </Link>
              </DialogClose>
            ) : null}
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
