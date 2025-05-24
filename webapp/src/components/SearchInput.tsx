"use client";

import { Input } from "./ui/input";
import { useSearchParams } from "next/navigation";

export default function SearchInput() {
  const params = useSearchParams();
  return (
    <Input
      defaultValue={params.get("query") ?? ""}
      placeholder="Search outcomes and decision documents..."
      name="query"
    />
  );
}
