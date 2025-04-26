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
  // const res = await fetch("http://localhost:9200/outcomes-indexed/_search", {
  //   method: "POST",
  //   headers: {
  //     "Content-Type": "application/json",
  //   },
  //   body: JSON.stringify({
  //     from,
  //     size,
  //     track_total_hits: true,
  //     query: {
  //       bool: {
  //         should: query
  //           ? [
  //               {
  //                 match: {
  //                   all_decisions: query,
  //                 },
  //               },
  //             ]
  //           : [{ match_all: {} }],
  //         filter: [
  //           unions && { match: { "filter.parties.unions": unions } },
  //           employer && { match: { "filter.parties.employer": employer } },
  //         ].filter(Boolean),
  //       },
  //     },
  //     sort: [
  //       { _score: { order: "desc" } },
  //       { last_updated: { order: "desc" } },
  //     ],
  //     _source: ["display"],
  //   }),
  // });
  // const data = await res.json();
  // const totalHits = data.hits.total.value;
  // return {
  //   size: totalHits,
  //   docs: data.hits.hits.map((hit: any) => hit._source.display),
  // };
  return {
    size: 1,
    docs: [
      {
        reference: "TUR1/1420(2024)",
        ballot: {
          inFavor: {
            percentVotes: 100,
            percentBU: 77.08333333333333,
            n: 74,
          },
          eligible: 96,
          against: {
            percentVotes: 0,
            percentBU: 0,
            n: 0,
          },
          spoiled: {
            percentVotes: 0,
            percentBU: 0,
            n: 0,
          },
          turnoutPercent: 77.08333333333333,
        },
        lastUpdated: "2025-03-10T16:26:13+00:00",
        parties: {
          unions: ["UCU"],
          employer: "BIMM University",
        },
        state: {
          label: "Recognised",
          value: "recognized",
        },
        title: "UCU & BIMM University",
        cacUrl:
          "https://www.gov.uk/government/publications/cac-outcome-ucu-bimm-university",
        bargainingUnit: {
          size: 118,
          description:
            "All salaried staff at pay scale 5 and below at the Brighton campus",
          membership: 12,
        },
        events: [
          {
            date: "2024-08-12",
            type: {
              label: "Application received",
              value: "application_received",
            },
          },
          {
            date: "2024-10-02",
            description:
              "Bargaining unit: All salaried staff at pay scale 5 and below at the Brighton campus",
            type: {
              label: "Application accepted",
              value: "application_accepted",
            },
          },
          {
            date: "2025-02-17",
            description: "Postal ballot; 96 eligible workers.",
            type: {
              label: "Ballot held",
              value: "ballot_held",
            },
          },
          {
            date: "2025-03-10",
            description: "74 votes in favour; 0 votes against.",
            type: {
              label: "Union recognised",
              value: "union_recognized",
            },
          },
        ],
        keyDates: {
          outcomeConcluded: "2025-03-10",
          methodAgreed: undefined,
          applicationReceived: "2024-08-12",
        },
      },
    ],
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
  console.log(outcomes);
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
