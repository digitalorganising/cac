"use client";

import Form from "next/form";
import { Input } from "./ui/input";
import ResetButton from "./ResetButton";
import { Button } from "./ui/button";
import { MagnifyingGlassIcon } from "@radix-ui/react-icons";
import { useSearchParams } from "next/navigation";

export default function SearchForm() {
  const params = useSearchParams();
  return (
    <Form action="" className="my-8 xs:my-12 max-w-2xl mx-auto">
      <div className="flex flex-col max-xs:space-y-2 xs:flex-row xs:space-x-2 ">
        <Input
          defaultValue={params.get("query") ?? ""}
          placeholder="Search outcomes and decision documents..."
          name="query"
        />
        <ResetButton forInput="query" />
        <Button type="submit" className="cursor-pointer">
          <MagnifyingGlassIcon />
          Search outcomes
        </Button>
      </div>
    </Form>
  );
}
