import { Search as SearchIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import OutcomeCard from "@/components/OutcomeCard";
import OutcomePagination from "@/components/OutcomePagination";

type GetOutcomesOptions = {
  from: number;
  size: number;
};

const getOutcomes = async ({ from, size }: GetOutcomesOptions) => {
  const res = await fetch("http://localhost:9200/outcomes-indexed/_search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from,
      size,
    }),
  });
  const data = await res.json();
  const totalHits = data.hits.total;
  return {
    size: totalHits,
    docs: data.hits.hits.map((hit: any) => hit._source),
  };
};

export default async function Home({}) {
  const outcomes = await getOutcomes({ from: 0, size: 15 });
  return (
    <main className="container max-w-screen-lg px-5 xs:px-8">
      <h1 className="text-5xl font-extrabold text-center mt-12">
        CAC Outcomes
      </h1>
      <form className="flex flex-col max-xs:space-y-2 xs:flex-row xs:space-x-2 my-12 max-w-2xl mx-auto">
        <Input placeholder="Search outcomes and decision documents..." />
        <Button>
          <SearchIcon className="mr-2 h-4 w-4" />
          Search outcomes
        </Button>
      </form>
      <section className="container space-y-6 my-16 px-0">
        {outcomes.docs.map((outcome: any) => (
          <OutcomeCard outcome={outcome} />
        ))}
      </section>
      <OutcomePagination />
    </main>
  );
}
