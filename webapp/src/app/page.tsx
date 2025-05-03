import Form from "next/form";
import { SearchIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import OutcomeCard from "@/components/OutcomeCard";
import OutcomePagination from "@/components/OutcomePagination";
import ResetButton from "@/components/ResetButton";
import { Outcome } from "@/lib/types";

type GetOutcomesOptions = {
  from: number;
  size: number;
  query?: string;
  "parties.unions"?: string;
  "parties.employer"?: string;
};

const getOutcomes = async ({
  from,
  size,
  query,
  "parties.unions": unions,
  "parties.employer": employer,
}: GetOutcomesOptions): Promise<{ size: number; docs: Outcome[] }> => {
  const res = await fetch("http://localhost:9200/outcomes-indexed/_search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from,
      size,
      track_total_hits: true,
      query: {
        bool: {
          should: query
            ? [
                {
                  match: {
                    all_decisions: query,
                  },
                },
              ]
            : [{ match_all: {} }],
          filter: [
            unions && { match: { "filter.parties.unions": unions } },
            employer && { match: { "filter.parties.employer": employer } },
          ].filter(Boolean),
        },
      },
      sort: [
        { _score: { order: "desc" } },
        { last_updated: { order: "desc" } },
      ],
      _source: ["display"],
    }),
  });
  const data = await res.json();
  const totalHits = data.hits.total.value;
  return {
    size: totalHits,
    docs: data.hits.hits.map((hit: any) => hit._source.display),
  };
};

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
    <main className="container max-w-(--breakpoint-lg) px-5 xs:px-8">
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
