import Form from "next/form";
import { SearchIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import OutcomeCard from "@/components/outcome-card/OutcomeCard";
import OutcomePagination from "@/components/OutcomePagination";
import ResetButton from "@/components/ResetButton";
import { getOutcomes } from "@/lib/outcomes";
import AppliedFilters from "@/components/filters/AppliedFilters";
import { createFilterHref } from "@/lib/filtering";

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
    <main className="container max-w-(--breakpoint-xl) px-4 xs:px-5 sm:px-6 pb-6">
      <h1 className="text-5xl font-extrabold text-center mt-8 xs:mt-10 sm:mt-12">
        CAC Outcomes
      </h1>
      <Form action="" className="my-8 xs:my-12 max-w-2xl mx-auto">
        <div className="flex flex-col max-xs:space-y-2 xs:flex-row xs:space-x-2 ">
          {" "}
          <Input
            defaultValue={options.query}
            placeholder="Search outcomes and decision documents..."
            name="query"
          />
          <ResetButton forInput="query" />
          <Button type="submit" className="cursor-pointer">
            <SearchIcon />
            Search outcomes
          </Button>
        </div>
        <AppliedFilters
          className="my-4"
          filters={filters}
          filterHref={filterHref}
        />
      </Form>
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
    </main>
  );
}
