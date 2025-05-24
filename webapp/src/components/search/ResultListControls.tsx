"use client";

import OutcomePagination from "./OutcomePagination";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRouter } from "nextjs-toploader/app";
import { useFilterHref } from "@/lib/useFilterHref";
import { SortKey, SortOrder } from "@/lib/filtering";

type Props = {
  nResults: number;
  pageSize: number;
  sortKey?: SortKey;
  sortOrder?: SortOrder;
};

export default function ResultListControls({
  nResults,
  pageSize,
  sortKey,
  sortOrder,
}: Props) {
  const router = useRouter();
  const filterHref = useFilterHref({ resetOnNavigate: new Set(["page"]) });

  return (
    <div className="flex justify-center items-center md:justify-end pl-2">
      <div className="mr-auto">
        <strong className="font-bold">{nResults}</strong>{" "}
        {nResults === 1 ? "result" : "results"}
      </div>

      <Select
        defaultValue={`${sortKey ?? "relevance"}-${sortOrder ?? "desc"}`}
        form="outcomes-search-form"
        name="sort"
        onValueChange={(value) => {
          if (value === "relevance-desc") {
            router.push(filterHref.delete("sort").urlString);
          }
          router.push(filterHref.replace("sort", value).urlString);
        }}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="relevance-desc">Relevance</SelectItem>
          <SelectItem value="bargainingUnitSize-desc">
            Bargaining unit size (largest to smallest)
          </SelectItem>
          <SelectItem value="bargainingUnitSize-asc">
            Bargaining unit size (smallest to largest)
          </SelectItem>

          <SelectItem value="lastUpdated-desc">
            Last updated (newest to oldest)
          </SelectItem>
          <SelectItem value="lastUpdated-asc">
            Last updated (oldest to newest)
          </SelectItem>

          <SelectItem value="applicationDate-desc">
            Application date (newest to oldest)
          </SelectItem>
          <SelectItem value="applicationDate-asc">
            Application date (oldest to newest)
          </SelectItem>

          <SelectItem value="concludedDate-desc">
            Date of conclusion (newest to oldest)
          </SelectItem>
          <SelectItem value="concludedDate-asc">
            Date of conclusion (oldest to newest)
          </SelectItem>
        </SelectContent>
      </Select>

      <OutcomePagination
        className="hidden md:block"
        totalPages={Math.ceil(nResults / pageSize)}
      />
    </div>
  );
}
