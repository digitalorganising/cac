import Form from "next/form";
import { SearchIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import OutcomeCard from "@/components/OutcomeCard";
import OutcomePagination from "@/components/OutcomePagination";
import ResetButton from "@/components/ResetButton";

type GetOutcomesOptions = {
  from: number;
  size: number;
  query?: string;
};

const getOutcomes = async ({
  from,
  size,
  query,
}: GetOutcomesOptions): Promise<{ size: number; docs: any[] }> => {
  const res = await fetch("http://localhost:9200/outcomes-indexed/_search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from,
      size,
      track_total_hits: true,
      query: query
        ? {
            match: {
              all_decisions: query,
            },
          }
        : undefined,
      sort: [
        { _score: { order: "desc" } },
        { last_updated: { order: "desc" } },
      ],
    }),
  });
  const data = await res.json();
  const totalHits = data.hits.total.value;
  return {
    size: totalHits,
    docs: data.hits.hits.map((hit: any) => hit._source),
  };
};

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ query?: string; page?: number }>;
}) {
  const pageSize = 15;
  const params = await searchParams;
  const outcomes = await getOutcomes({
    from: pageSize * ((params.page ?? 1) - 1),
    size: pageSize,
    query: params.query,
  });
  return (
    <main className="container max-w-screen-lg px-5 xs:px-8">
      <h1 className="text-5xl font-extrabold text-center mt-12">
        CAC Outcomes
      </h1>
      <Form
        action=""
        className="flex flex-col max-xs:space-y-2 xs:flex-row xs:space-x-2 my-12 max-w-2xl mx-auto"
      >
        <Input
          defaultValue={params.query}
          placeholder="Search outcomes and decision documents..."
          name="query"
        />
        <ResetButton forInput="query" />
        <Button type="submit">
          <SearchIcon />
          Search outcomes
        </Button>
      </Form>
      <OutcomePagination totalPages={Math.ceil(outcomes.size / pageSize)} />
      <section className="container space-y-6 my-16 px-0">
        {outcomes.docs.map((outcome: any) => (
          <OutcomeCard key={outcome.reference} outcome={outcome} />
        ))}
      </section>
      <OutcomePagination totalPages={Math.ceil(outcomes.size / pageSize)} />
    </main>
  );
}
