"use client";

import {
  Cross2Icon,
  MagnifyingGlassIcon,
  UpdateIcon,
} from "@radix-ui/react-icons";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useFormStatus } from "react-dom";
import ResetButton from "./ResetButton";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

function SearchInput() {
  const params = useSearchParams();

  return (
    <Input
      placeholder="Search outcomes..."
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
          <Input placeholder="Search outcomes..." name="query" />
          <Button
            type="reset"
            variant="secondary"
            title="Clear"
            className="hidden xs:flex aspect-square cursor-pointer"
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
      <div className="relative w-full flex xs:space-x-2">
        <SearchInput />
        <ResetButton
          forInput="query"
          className="absolute xs:static right-1 top-1/2 -translate-y-1/2 xs:translate-none max-xs:bg-white max-xs:bg-opacity-80 max-xs:size-7 max-xs:hover:bg-white"
        />
      </div>
      <SubmitButton />
    </Suspense>
  );
}
