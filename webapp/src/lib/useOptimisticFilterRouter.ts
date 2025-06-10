import { usePathname, useSearchParams } from "next/navigation";
import { useRouter } from "nextjs-toploader/app";
import { createFilterHref } from "./filtering";
import { AppQueryParams } from "./types";
import { useMemo, useOptimistic, useTransition } from "react";
import type { UrlObject } from "node:url";

// Vile!
const urlSearchParamsToObject = <T>(searchParams: URLSearchParams): T => {
  const obj: T = {} as T;
  for (const [key, value] of searchParams.entries()) {
    if (Array.isArray(obj[key as keyof T])) {
      (obj[key as keyof T] as string[]).push(value);
    } else {
      (obj[key as keyof T] as string[]) = [value];
    }
  }
  return obj;
};

type RouterFn = (key: keyof AppQueryParams, value: string | string[]) => void;

type FilterRouter = {
  params: AppQueryParams;
  replaceAll: RouterFn;
  replace: RouterFn;
  add: RouterFn;
  delete: (key: keyof AppQueryParams, value?: string | string[]) => void;
};

export function useOptimisticFilterRouter({
  resetOnNavigate,
}: {
  resetOnNavigate: Set<keyof AppQueryParams>;
}): FilterRouter {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();

  const paramsObject = useMemo(
    () => urlSearchParamsToObject<AppQueryParams>(searchParams),
    [searchParams],
  );

  const [optimisticParams, setOptimisticParams] = useOptimistic(paramsObject);
  const [isPending, startTransition] = useTransition();

  const filterHref = useMemo(
    () =>
      createFilterHref({
        searchParams: optimisticParams,
        pathname,
        resetOnNavigate,
      }),
    [pathname, optimisticParams, resetOnNavigate],
  );

  const doTransition =
    (newHref: { urlObject: UrlObject; urlString: string }) => () => {
      setOptimisticParams((pendingParams) => {
        const a = {
          ...pendingParams,
          ...(newHref.urlObject.query as AppQueryParams),
        } as AppQueryParams;
        return a;
      });
      router.push(newHref.urlString);
    };

  return {
    params: optimisticParams,
    replaceAll: (key, value) => {
      startTransition(doTransition(filterHref.replaceAll(key, value)));
    },
    replace: (key, value) => {
      startTransition(doTransition(filterHref.replace(key, value)));
    },
    add: (key, value) => {
      startTransition(doTransition(filterHref.add(key, value)));
    },
    delete: (key, value) => {
      startTransition(doTransition(filterHref.delete(key, value)));
    },
  };
}
