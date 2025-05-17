import Form from "next/form";
import { SearchIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import OutcomeCard from "@/components/OutcomeCard";
import OutcomePagination from "@/components/OutcomePagination";
import ResetButton from "@/components/ResetButton";
import { Outcome } from "@/lib/types";
import { getOutcomes } from "@/lib/outcomes";

type QueryParams = {
  query?: string;
  page?: number;
  "parties.unions"?: string;
  "parties.employer"?: string;
};

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<QueryParams>;
}) {
  const pageSize = 15;
  const { page, ...params } = await searchParams;
  const outcomes = await getOutcomes({
    from: pageSize * ((page ?? 1) - 1),
    size: pageSize,
    ...params,
  });
  return (
    <main className="container max-w-(--breakpoint-xl) px-5 xs:px-8 pb-6">
      <h1 className="text-5xl font-extrabold text-center mt-12">
        CAC Outcomes
      </h1>
      <Form
        action=""
        className="flex flex-col max-xs:space-y-2 xs:flex-row xs:space-x-2 my-8 xs:my-12 max-w-2xl mx-auto"
      >
        <Input
          defaultValue={params.query}
          placeholder="Search outcomes and decision documents..."
          name="query"
        />
        <ResetButton forInput="query" />
        <Button type="submit" className="cursor-pointer">
          <SearchIcon />
          Search outcomes
        </Button>
      </Form>
      <OutcomePagination totalPages={Math.ceil(outcomes.size / pageSize)} />
      <section className="container space-y-6 my-8 xs:my-16 px-0">
        {outcomes.docs.map((outcome) => (
          <OutcomeCard key={outcome.reference} outcome={outcome} />
        ))}
      </section>
      <OutcomePagination totalPages={Math.ceil(outcomes.size / pageSize)} />
    </main>
  );
}
