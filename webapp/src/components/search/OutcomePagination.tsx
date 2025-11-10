import React from "react";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import {
  appSearchParamsCache,
  appSearchParamsSerializer,
} from "@/lib/search-params";

export default function OutcomePagination({
  totalPages,
  page = 1,
  ...props
}: {
  totalPages: number;
  page?: number;
} & React.ComponentProps<typeof Pagination>) {
  const params = appSearchParamsCache.all();
  const pageUrl = (n: number): string => {
    return appSearchParamsSerializer({ ...params, page: n }) || "/";
  };
  const pageNumbers = () => {
    if (totalPages <= 1) {
      return [1];
    }

    const maxDisplayed = 7;
    const pages: (number | "...")[] = [1];

    const startEllipsis = totalPages > maxDisplayed && page > maxDisplayed - 3;
    const endEllipsis =
      totalPages > maxDisplayed && page < totalPages - maxDisplayed + 4;

    if (startEllipsis) {
      pages.push("...");
    }

    const startIndex = startEllipsis
      ? Math.max(2, Math.min(page - 1, totalPages - maxDisplayed + 3))
      : 2;
    const endIndex = endEllipsis
      ? Math.min(totalPages - 1, Math.max(page + 1, maxDisplayed - 2))
      : totalPages - 1;
    for (let i = startIndex; i <= endIndex; i++) {
      pages.push(i);
    }

    if (endEllipsis) {
      pages.push("...");
    }

    // Always end with the last page
    if (pages[pages.length - 1] !== totalPages) {
      pages.push(totalPages);
    }

    return pages;
  };

  const pages = pageNumbers();

  return (
    <Pagination {...props}>
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            className={
              page === 1 ? "pointer-events-none opacity-30" : undefined
            }
            href={page === 1 ? "" : pageUrl(page - 1)}
          />
        </PaginationItem>
        {pages.map((p, index) =>
          p === "..." ? (
            <PaginationEllipsis key={`ellipsis-${index}`} />
          ) : (
            <PaginationItem key={p}>
              <PaginationLink href={pageUrl(p)} isActive={p === page}>
                {p}
              </PaginationLink>
            </PaginationItem>
          ),
        )}
        <PaginationItem
          className={
            page === totalPages || totalPages === 0
              ? "pointer-events-none opacity-30"
              : undefined
          }
        >
          <PaginationNext
            href={
              page === totalPages || totalPages === 0 ? "" : pageUrl(page + 1)
            }
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}
