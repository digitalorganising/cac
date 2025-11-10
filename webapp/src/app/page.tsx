import { SearchParams } from "nuqs/server";
import { FacetingControls } from "@/components/facets";
import OutcomeCard from "@/components/outcome-card/OutcomeCard";
import OutcomePagination from "@/components/search/OutcomePagination";
import ResultListControls from "@/components/search/ResultListControls";
import { PAGE_SIZE, getOutcomes } from "@/lib/queries/outcomes";
import { appSearchParamsToOutcomesOptions } from "@/lib/queries/util";
import { appSearchParamsCache } from "@/lib/search-params";
import { Outcome } from "@/lib/types";

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await appSearchParamsCache.parse(searchParams);
  if (!!params.reference) {
    const options = appSearchParamsToOutcomesOptions(PAGE_SIZE, params);
    const outcomes = await getOutcomes(options, params.debug);
    if (outcomes.size === 1) {
      return {
        title: outcomes.docs[0].title,
      };
    }
  }
  if (!!params.query) {
    return {
      title: params.query,
    };
  }
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await appSearchParamsCache.parse(searchParams);
  const options = appSearchParamsToOutcomesOptions(PAGE_SIZE, params);
  const outcomes = getOutcomes(options, params.debug);
  return (
    <>
      <FacetingControls options={options} />
      <OutcomesResults
        outcomes={outcomes}
        hasQuery={params.query !== null}
        page={params.page}
        debug={params.debug}
      />
    </>
  );
}

async function OutcomesResults({
  outcomes,
  hasQuery,
  page,
  debug,
}: {
  outcomes: Promise<{ size: number; docs: Outcome[] }>;
  hasQuery: boolean;
  page: number;
  debug: boolean;
}) {
  const { size, docs } = await outcomes;
  return (
    <>
      <ResultListControls nResults={size} hasQuery={hasQuery}>
        <OutcomePagination
          className="hidden md:block"
          totalPages={Math.ceil(size / PAGE_SIZE)}
          page={page}
        />
      </ResultListControls>
      <section className="container space-y-4 xs:space-y-5 sm:space-y-6 my-3 px-0">
        {docs.map((outcome) => (
          <OutcomeCard
            key={outcome.reference}
            outcome={outcome}
            showDebugView={debug}
          />
        ))}
      </section>
      <div className="flex justify-center md:justify-end">
        <OutcomePagination
          totalPages={Math.ceil(size / PAGE_SIZE)}
          page={page}
        />
      </div>
    </>
  );
}
