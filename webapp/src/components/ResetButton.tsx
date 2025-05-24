"use client";

import { Cross2Icon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { usePathname, useSearchParams, useRouter } from "next/navigation";
import { createFilterHref } from "@/lib/filtering";
import { useMemo } from "react";

type Props = {
  forInput: string;
};
export default function ResetButton({ forInput }: Props) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const filterHref = useMemo(
    () =>
      createFilterHref({
        searchParams: Object.fromEntries(searchParams.entries()),
        resetOnNavigate: new Set(["page"]),
      }),
    [searchParams],
  );
  const router = useRouter();

  const reset = () => {
    const urlObject = filterHref.delete("query");
    const params = new URLSearchParams(
      Object.entries(
        urlObject.query as Record<string, string | string[] | undefined>,
      ).flatMap(([key, value]) =>
        Array.isArray(value)
          ? value.map((v) => [key, v])
          : value === undefined
            ? []
            : [[key, value]],
      ),
    );
    const pathname = urlObject.pathname ?? "/";
    return router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <Button
      type="reset"
      variant="secondary"
      title="Clear"
      className="aspect-square cursor-pointer"
      onClick={reset}
    >
      <Cross2Icon />
    </Button>
  );
}
