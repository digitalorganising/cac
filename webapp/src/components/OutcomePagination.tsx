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

  const pages = (
    currentPage === 1
      ? [1, 2, 3]
      : currentPage === totalPages
        ? [totalPages - 2, totalPages - 1, totalPages]
        : [currentPage - 1, currentPage, currentPage + 1]
  ).filter((p) => p <= totalPages);

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
        {pages.map((p) => (
          <PaginationItem
            key={p}
            className={
              pages.length === 1 ? "pointer-events-none opacity-30" : undefined
            }
          >
            <PaginationLink href={pageUrl(p)} isActive={p === currentPage}>
              {p}
            </PaginationLink>
          </PaginationItem>
        ))}
        {pages[pages.length - 1] !== totalPages ? (
          <>
            <PaginationItem>
              <PaginationEllipsis />
            </PaginationItem>
            <PaginationItem>
              <PaginationLink href={pageUrl(totalPages)}>
                {totalPages}
              </PaginationLink>
            </PaginationItem>
          </>
        ) : null}
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
