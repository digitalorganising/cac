import OutcomeCard from "@/components/outcome-card/OutcomeCard";
import OutcomePagination from "@/components/search/OutcomePagination";
import { getOutcomes } from "@/lib/outcomes";
import {
  AppQueryParams,
  appQueryParamsToOutcomesOptions,
  createFilterHref,
} from "@/lib/filtering";
import AppliedFilters from "@/components/search/AppliedFilters";
import ResultListControls from "@/components/search/ResultListControls";
import Facets from "@/components/search/Facets";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<AppQueryParams>;
}) {
  const pageSize = 15;
  const params = await searchParams;
  const filterHref = createFilterHref({
    searchParams: params,
    resetOnNavigate: new Set(["query", "page", "reference"]),
    pathname: "/",
  });
  const options = appQueryParamsToOutcomesOptions(pageSize, params);
  const outcomes = await getOutcomes(options);
  return (
    <>
      <AppliedFilters
        params={params}
        className="my-4"
        filterHref={filterHref}
      />
      <Facets />
      <ResultListControls
        nResults={outcomes.size}
        pageSize={pageSize}
        hasQuery={options.query !== undefined}
      />
      <section className="container space-y-4 xs:space-y-5 sm:space-y-6 my-3 px-0">
        {outcomes.docs.map((outcome) => (
          <OutcomeCard
            key={outcome.reference}
            outcome={outcome}
            filterHref={filterHref}
            showDebugView={params.debug !== undefined}
          />
        ))}
      </section>
      <div className="flex justify-center md:justify-end">
        <OutcomePagination totalPages={Math.ceil(outcomes.size / pageSize)} />
      </div>
    </>
  );
}
