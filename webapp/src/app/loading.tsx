import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <>
      <div className="mt-20 xs:mt-24 sm:mt-25" />
      <section className="container space-y-4 xs:space-y-5 sm:space-y-6 my-6 xs:my-7 sm:my-8 xs:my-16 px-0">
        <Card>
          <Skeleton className="w-2/3 h-4 m-3" />
          <CardContent className="flex flex-col md:flex-row space-x-4 w-full space-y-4">
            <div className="md:w-1/2 space-y-4">
              <Skeleton className="w-1/3 h-4" />
              <Skeleton className="w-1/2 h-4" />
              <Skeleton className="w-2/3 h-4" />
              <Skeleton className="w-5/6 h-4" />
              <Skeleton className="w-1/2 h-4" />
              <Skeleton className="w-2/3 h-4" />
            </div>
            <div className="md:w-1/2 space-y-4">
              <Skeleton className="w-2/3 h-4" />
              <Skeleton className="w-1/2 h-4" />
              <Skeleton className="w-3/4 h-4" />
              <Skeleton className="w-1/4 h-4" />
              <Skeleton className="w-2/5 h-4" />
              <Skeleton className="w-2/3 h-4" />
            </div>
          </CardContent>
        </Card>
      </section>
    </>
  );
}
