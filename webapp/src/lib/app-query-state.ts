import { useTopLoader } from "nextjs-toploader";
import { Options, UseQueryStateReturn, useQueryState } from "nuqs";
import { useEffect, useTransition } from "react";
import { AppSearchParams, appSearchParamsParser } from "./search-params";

type AppSearchParamsParser = typeof appSearchParamsParser;

type DefaultValue<K extends keyof AppSearchParamsParser> =
  AppSearchParamsParser[K] extends {
    defaultValue: NonNullable<AppSearchParams[K]>;
  }
    ? NonNullable<AppSearchParams[K]>
    : undefined;

const opts: Options = {
  shallow: false,
  scroll: true,
};

export const useAppQueryState = <const K extends keyof AppSearchParamsParser>(
  key: K,
): UseQueryStateReturn<AppSearchParams[K], DefaultValue<K>> => {
  const loader = useTopLoader();
  const [isLoading, startTransition] = useTransition();
  const qs = useQueryState(
    key,
    appSearchParamsParser[key].withOptions({ startTransition, ...opts }),
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
