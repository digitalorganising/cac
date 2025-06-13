import { SearchParams } from "nuqs/server";
import OutcomeCard from "@/components/outcome-card/OutcomeCard";
import OutcomePagination from "@/components/search/OutcomePagination";
import { getOutcomes } from "@/lib/queries/outcomes";
import ResultListControls from "@/components/search/ResultListControls";
import FilteringControls from "@/components/search/FilteringControls";
import { appSearchParamsCache } from "@/lib/search-params";
import { appSearchParamsToOutcomesOptions } from "@/lib/queries/util";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const pageSize = 15;
  const params = await appSearchParamsCache.parse(searchParams);
  const options = appSearchParamsToOutcomesOptions(pageSize, params);
  const outcomes = await getOutcomes(options);
  return (
    <>
      <FilteringControls options={options} />
      <ResultListControls
        nResults={outcomes.size}
        hasQuery={params.query !== null}
      >
        <OutcomePagination
          className="hidden md:block"
          totalPages={Math.ceil(outcomes.size / pageSize)}
          page={params.page}
        />
      </ResultListControls>
      <section className="container space-y-4 xs:space-y-5 sm:space-y-6 my-3 px-0">
        {outcomes.docs.map((outcome) => (
          <OutcomeCard
            key={outcome.reference}
            outcome={outcome}
            showDebugView={!!params.debug}
          />
        ))}
      </section>
      <div className="flex justify-center md:justify-end">
        <OutcomePagination
          totalPages={Math.ceil(outcomes.size / pageSize)}
          page={params.page}
        />
      </div>
    </>
  );
}
