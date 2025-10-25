import { SearchParams } from "nuqs/server";
import OutcomeCard from "@/components/outcome-card/OutcomeCard";
import OutcomePagination from "@/components/search/OutcomePagination";
import ResultListControls from "@/components/search/ResultListControls";
import { PAGE_SIZE, getOutcomes } from "@/lib/queries/outcomes";
import { appSearchParamsToOutcomesOptions } from "@/lib/queries/util";
import { appSearchParamsCache } from "@/lib/search-params";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await appSearchParamsCache.parse(searchParams);
  const options = appSearchParamsToOutcomesOptions(PAGE_SIZE, params);
  const outcomes = await getOutcomes(options, params.debug);
  return (
    <>
      <ResultListControls
        nResults={outcomes.size}
        hasQuery={params.query !== null}
      >
        <OutcomePagination
          className="hidden md:block"
          totalPages={Math.ceil(outcomes.size / PAGE_SIZE)}
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
          totalPages={Math.ceil(outcomes.size / PAGE_SIZE)}
          page={params.page}
        />
      </div>
    </>
  );
}
