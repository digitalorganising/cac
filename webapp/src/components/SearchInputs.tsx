"use client";

import { Suspense } from "react";
import { Input } from "./ui/input";
import { useSearchParams } from "next/navigation";
import ResetButton from "./ResetButton";
import { Button } from "./ui/button";
import {
  Cross2Icon,
  MagnifyingGlassIcon,
  UpdateIcon,
} from "@radix-ui/react-icons";
import { useFormStatus } from "react-dom";

function SearchInput() {
  const params = useSearchParams();

  return (
    <Input
      placeholder="Search outcomes and decision documents..."
      name="query"
      defaultValue={params.get("query") ?? ""}
    />
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" className="cursor-pointer" disabled={pending}>
      {pending ? (
        <UpdateIcon className="animate-spin" />
      ) : (
        <MagnifyingGlassIcon />
      )}
      Search outcomes
    </Button>
  );
}

export default function SearchInputs() {
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
          <Button type="submit" className="cursor-pointer">
            <MagnifyingGlassIcon />
            Search outcomes
          </Button>
        </>
      }
    >
      <SearchInput />
      <ResetButton forInput="query" />
      <SubmitButton />
    </Suspense>
  );
}
