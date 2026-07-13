import { Suspense } from "react";
import Link from "next/link";
import { ChevronDownIcon, Cross2Icon } from "@radix-ui/react-icons";
import { filterLabels } from "@/components/facets/common";
import { MultiSelectDesktop } from "@/components/facets/MultiSelect";
import { InputTriggerButton } from "@/components/ui/input-trigger-button";
import { getFacets } from "@/lib/queries/facets";
import {
  appSearchParamsCache,
  appSearchParamsSerializer,
  deleteParamValue,
} from "@/lib/search-params";

const triggerClassName = "w-64 sm:w-72 justify-between text-base px-4 py-2.5";

function UnionFilterFallback() {
  return (
    <InputTriggerButton
      loading={true}
      aria-label="Unions filter"
      className={triggerClassName}
      icon={<ChevronDownIcon className="size-4 opacity-50" />}
    >
      Unions
    </InputTriggerButton>
  );
}

async function UnionFilterControl() {
  const facets = await getFacets({});
  const options = facets.multiSelect["parties.unions"].map(
    ({ value, label, count }) => ({
      value: value.toString(),
      label: `${label ?? value} (${count})`,
    }),
  );

  return (
    <MultiSelectDesktop
      label={filterLabels["parties.unions"] ?? "Unions"}
      name="parties.unions"
      options={options}
      className={triggerClassName}
    />
  );
}

function formatUnionList(unions: string[]): string {
  if (unions.length === 1) {
    return unions[0];
  }
  if (unions.length === 2) {
    return `${unions[0]} and ${unions[1]}`;
  }
  return `${unions.slice(0, -1).join(", ")}, and ${unions[unions.length - 1]}`;
}

type Props = {
  unions: string[];
};

export default function DashboardUnionFilter({ unions }: Props) {
  const hasUnionFilter = unions.length > 0;
  const params = appSearchParamsCache.all();
  const clearHref = `/dashboard${appSearchParamsSerializer(
    deleteParamValue(params, "parties.unions"),
  )}`;

  return (
    <div className="rounded-lg border bg-card text-card-foreground shadow-xs my-3 md:my-6 p-4 xs:p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <div className="min-w-0 sm:basis-1/2 space-y-1">
          <h2 className="text-base font-semibold tracking-tight">
            {hasUnionFilter ? "Filtered by union" : "Filter by union"}
          </h2>
          <p className="text-sm text-muted-foreground">
            {hasUnionFilter ? (
              <>
                Metrics below are limited to outcomes involving{" "}
                <span className="font-medium text-foreground">
                  {formatUnionList(unions)}
                </span>
                . Cross-union comparison charts are hidden while a filter is
                applied.
              </>
            ) : (
              <>
                Narrow every chart to one or more unions. Cross-union
                comparison charts are hidden while a filter is applied.
              </>
            )}
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-2 sm:basis-1/2">
          <Suspense fallback={<UnionFilterFallback />}>
            <UnionFilterControl />
          </Suspense>
          {hasUnionFilter ? (
            <Link
              href={clearHref}
              className="flex items-center gap-x-2 rounded-md border border-slate-200 bg-transparent px-3 py-2.5 text-sm font-semibold hover:underline"
            >
              Clear filter
              <Cross2Icon className="size-3 text-slate-500" />
            </Link>
          ) : null}
        </div>
      </div>
    </div>
  );
}
