import { Cross2Icon, MixerHorizontalIcon } from "@radix-ui/react-icons";
import { Loader2Icon } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import {
  appSearchParamsCache,
  appSearchParamsSerializer,
} from "@/lib/search-params";
import { Button } from "../ui/button";
import CountBadge from "../ui/count-badge";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";

export default function MobileDialog({
  nAppliedFilters,
  reference,
  children,
}: {
  nAppliedFilters: number;
  reference?: { value: string }[];
  children: React.ReactNode;
}) {
  const params = appSearchParamsCache.all();
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="w-full bg-slate-100 py-4 xs:py-6 mt-2 mb-3"
          title="Filters"
        >
          <MixerHorizontalIcon />
          Filters
          {nAppliedFilters > 0 ? <CountBadge count={nAppliedFilters} /> : null}
        </Button>
      </DialogTrigger>
      <DialogContent
        className="w-full h-[calc(100%-(var(--spacing)*18)+1px)] block top-0 left-0 translate-none rounded-b-none"
        sheet={
          <div className="fixed h-18 z-250 bottom-0 left-0 bg-white border-t border-gray-200 w-full p-4 flex justify-end items-center gap-2">
            <DialogClose asChild>
              <Button className="cursor-pointer" variant="outline" asChild>
                <Link
                  href={
                    appSearchParamsSerializer({ query: params.query }) || "/"
                  }
                >
                  Clear all
                </Link>
              </Button>
            </DialogClose>
            <DialogClose asChild>
              <Button className="cursor-pointer">Show results</Button>
            </DialogClose>
          </div>
        }
      >
        <DialogHeader>
          <DialogTitle>Filters</DialogTitle>
          <DialogDescription className="sr-only">
            Filters for searching outcomes
          </DialogDescription>
        </DialogHeader>
        {reference ? (
          <DialogClose asChild>
            <Link
              href={
                appSearchParamsSerializer({
                  ...params,
                  reference: null,
                }) || "/"
              }
              className="flex p-2 mb-2 mt-3 text-sm w-full items-center space-x-2 justify-center mx-auto border border-slate-200 bg-slate-100 rounded-md"
            >
              <div>
                <span className="font-medium">Reference:</span>{" "}
                {reference.map((r) => r.value).join(", ")}
              </div>
              <button className="cursor-pointer" title="Clear reference filter">
                <Cross2Icon className="size-3" />
              </button>
            </Link>
          </DialogClose>
        ) : null}
        <Suspense
          fallback={
            <div className="w-full h-full relative">
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 animate-spin">
                <Loader2Icon className="size-10" />
              </div>
            </div>
          }
        >
          {children}
        </Suspense>
      </DialogContent>
    </Dialog>
  );
}
