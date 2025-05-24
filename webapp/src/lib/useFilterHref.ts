import { usePathname, useSearchParams } from "next/navigation";
import { AppQueryParams, createFilterHref } from "./filtering";
import { useMemo } from "react";

export function useFilterHref({
  resetOnNavigate,
}: {
  resetOnNavigate: Set<keyof AppQueryParams>;
}) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  return useMemo(
    () =>
      createFilterHref({
        searchParams: Object.fromEntries(
          searchParams.entries(),
        ) as AppQueryParams,
        pathname,
        resetOnNavigate,
      }),
    [pathname, searchParams, resetOnNavigate],
  );
}
