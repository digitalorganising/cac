"use client";

import { Suspense } from "react";
import { Input } from "./ui/input";
import { useSearchParams } from "next/navigation";
import ResetButton from "./ResetButton";
import { Button } from "./ui/button";
import { Cross2Icon } from "@radix-ui/react-icons";

function SuspendedSearchInput() {
  const params = useSearchParams();

  return (
    <Input
      placeholder="Search outcomes and decision documents..."
      name="query"
      defaultValue={params.get("query") ?? ""}
    />
  );
}

export default function SearchInput() {
  return (
    <Suspense
      fallback={
        <>
          <Input
            placeholder="Search outcomes and decision documents..."
            name="query"
          />
          <Button
            type="reset"
            variant="secondary"
            title="Clear"
            className="aspect-square cursor-pointer"
          >
            <Cross2Icon />
          </Button>
        </>
      }
    >
      <SuspendedSearchInput />
      <ResetButton forInput="query" />
    </Suspense>
  );
}
