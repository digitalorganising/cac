import { useEffect, useTransition } from "react";
import { useQueryState, UseQueryStateReturn } from "nuqs";
import { useTopLoader } from "nextjs-toploader";
import { AppSearchParams, appSearchParamsParser } from "./search-params";

type AppSearchParamsParser = typeof appSearchParamsParser;

type DefaultValue<K extends keyof AppSearchParamsParser> =
  AppSearchParamsParser[K] extends {
    defaultValue: NonNullable<AppSearchParams[K]>;
  }
    ? NonNullable<AppSearchParams[K]>
    : undefined;

export const useAppQueryState = <const K extends keyof AppSearchParamsParser>(
  key: K,
): UseQueryStateReturn<AppSearchParams[K], DefaultValue<K>> => {
  const loader = useTopLoader();
  const [isLoading, startTransition] = useTransition();
  const qs = useQueryState(
    key,
    appSearchParamsParser[key].withOptions({ startTransition, shallow: false }),
  ) as UseQueryStateReturn<AppSearchParams[K], DefaultValue<K>>;

  useEffect(() => {
    if (isLoading) {
      loader.start();
    } else {
      loader.done();
    }
  }, [isLoading]);

  return qs;
};
