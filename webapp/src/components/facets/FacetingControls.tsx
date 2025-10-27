import { Suspense } from "react";
import { Facets, GetFacetsOptions, getFacets } from "@/lib/queries/facets";
import { appSearchParamsCache } from "@/lib/search-params";
import { arr } from "@/lib/utils";
import AppliedFilters, {
  AppliedLabelledFilters,
  type FilterEntries,
} from "./AppliedFilters";
import DesktopControls, { DesktopControlsFallback } from "./DesktopControls";
import MobileControls from "./MobileControls";
import MobileDialog from "./MobileDialog";
import { filterLabels } from "./common";

type Props = {
  options: GetFacetsOptions;
};

function DesktopControlsWithSuspense({
  appliedFilters,
  facetsPromise,
}: {
  appliedFilters: FilterEntries;
  facetsPromise: Promise<Facets>;
}) {
  return (
    <>
      <Suspense fallback={<AppliedFilters filterEntries={appliedFilters} />}>
        <AppliedLabelledFilters
          filterEntries={appliedFilters}
          facetsPromise={facetsPromise}
        />
      </Suspense>
      <div className="flex flex-wrap items-center justify-start gap-x-3 xl:gap-x-4 gap-y-3 py-4">
        <Suspense fallback={<DesktopControlsFallback />}>
          <DesktopControls facetsPromise={facetsPromise} />
        </Suspense>
      </div>
    </>
  );
}

export default function FacetingControls({ options }: Props) {
  const facetsPromise = getFacets(options, appSearchParamsCache.get("debug"));
  const params = appSearchParamsCache.all();
  const appliedFilters = Object.fromEntries(
    Object.entries(params)
      .filter((kv) => kv[0] in filterLabels && kv[1] !== null)
      .map(([key, value]) => [key, arr(value).map((v) => ({ value: v }))]),
  ) as FilterEntries;
  return (
    <>
      <div className="my-4 space-y-2 hidden sm:block">
        <DesktopControlsWithSuspense
          appliedFilters={appliedFilters}
          facetsPromise={facetsPromise}
        />
      </div>
      <div className="sm:hidden">
        <MobileDialog
          nAppliedFilters={Object.values(appliedFilters).flat().length}
          reference={appliedFilters["reference"] as { value: string }[]}
        >
          <MobileControls facetsPromise={facetsPromise} />
        </MobileDialog>
      </div>
    </>
  );
}
