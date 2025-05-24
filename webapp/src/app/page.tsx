import OutcomeCard from "@/components/outcome-card/OutcomeCard";
import OutcomePagination from "@/components/OutcomePagination";
import { getOutcomes } from "@/lib/outcomes";
import { createFilterHref } from "@/lib/filtering";
import AppliedFilters from "@/components/filters/AppliedFilters";

type Param = string | string[] | undefined;

type QueryParams = Record<
  "query" | "page" | "parties.unions" | "parties.employer" | "reference",
  Param
>;

const singleValue = (value: Param): string | undefined =>
  Array.isArray(value) ? value[value.length - 1] : value;

const multiValue = (value: Param): string[] | undefined =>
  value !== undefined ? (Array.isArray(value) ? value : [value]) : undefined;

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<QueryParams>;
}) {
  const pageSize = 15;
  const params = await searchParams;
  const filterHref = createFilterHref({
    searchParams: params,
    resetOnNavigate: new Set(["query", "page", "reference"]),
  });
  const options = {
    from: pageSize * (parseInt(singleValue(params.page) ?? "1") - 1),
    size: pageSize,
    query: singleValue(params.query),
    "parties.unions": multiValue(params["parties.unions"]),
    "parties.employer": multiValue(params["parties.employer"]),
    reference: multiValue(params.reference),
  };
  const { from, size, query: _q, ...filters } = options;
  const outcomes = await getOutcomes(options);
  return (
    <>
      <AppliedFilters
        className="my-4"
        filters={filters}
        filterHref={filterHref}
      />
      <OutcomePagination totalPages={Math.ceil(outcomes.size / pageSize)} />
      <section className="container space-y-4 xs:space-y-5 sm:space-y-6 my-6 xs:my-7 sm:my-8 xs:my-16 px-0">
        {outcomes.docs.map((outcome) => (
          <OutcomeCard
            key={outcome.reference}
            outcome={outcome}
            filterHref={filterHref}
          />
        ))}
      </section>
      <OutcomePagination totalPages={Math.ceil(outcomes.size / pageSize)} />
    </>
  );
}
