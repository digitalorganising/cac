"use client";

import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { usePathname, useSearchParams } from "next/navigation";

export default function OutcomePagination({
  totalPages,
}: {
  totalPages: number;
}) {
  const pathname = usePathname();
  const params = useSearchParams();
  const currentPage = Number(params.get("page") ?? 1);
  const pageUrl = (n: number): string => {
    const p = new URLSearchParams(params);
    p.set("page", n.toString());
    return `${pathname}?${p.toString()}`;
  };

  const pageNumbers = () => {
    if (totalPages <= 1) {
      return [1];
    }

    const maxDisplayed = 7;
    const pages: (number | "...")[] = [1];

    const startEllipsis =
      totalPages > maxDisplayed && currentPage > maxDisplayed - 3;
    const endEllipsis =
      totalPages > maxDisplayed && currentPage < totalPages - maxDisplayed + 4;

    if (startEllipsis) {
      pages.push("...");
    }

    const startIndex = startEllipsis
      ? Math.max(2, Math.min(currentPage - 1, totalPages - maxDisplayed + 3))
      : 2;
    const endIndex = endEllipsis
      ? Math.min(totalPages - 1, Math.max(currentPage + 1, maxDisplayed - 2))
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
    <Pagination>
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            className={
              currentPage === 1 ? "pointer-events-none opacity-30" : undefined
            }
            href={currentPage === 1 ? "" : pageUrl(currentPage - 1)}
          />
        </PaginationItem>
        {pages.map((p, index) =>
          p === "..." ? (
            <PaginationEllipsis key={`ellipsis-${index}`} />
          ) : (
            <PaginationItem key={p}>
              <PaginationLink href={pageUrl(p)} isActive={p === currentPage}>
                {p}
              </PaginationLink>
            </PaginationItem>
          ),
        )}
        <PaginationItem
          className={
            currentPage === totalPages
              ? "pointer-events-none opacity-30"
              : undefined
          }
        >
          <PaginationNext
            href={currentPage === totalPages ? "" : pageUrl(currentPage + 1)}
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}
