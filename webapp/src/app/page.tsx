import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import OutcomeCard from "@/components/OutcomeCard";

const outcomes = [
  "The",
  "quick",
  "brown",
  "fox",
  "jumps",
  "over",
  "the",
  "lazy",
  "dog",
].map((title) => ({ title }));

export default function Home() {
  return (
    <main className="container max-w-screen-lg">
      <h1 className="text-5xl font-extrabold text-center mt-12">
        CAC Outcomes
      </h1>
      <div className="flex flex-col max-xs:space-y-2 xs:flex-row xs:space-x-2 my-12 max-w-2xl mx-auto">
        <Input placeholder="Search outcomes and decision documents..." />
        <Button>
          <Search className="mr-2 h-4 w-4" />
          Search outcomes
        </Button>
      </div>
      <section className="container space-y-6 my-16 px-0">
        {outcomes.map((outcome) => (
          <OutcomeCard outcome={outcome} />
        ))}
      </section>
    </main>
  );
}
