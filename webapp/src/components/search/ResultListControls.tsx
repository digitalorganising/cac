"use client";

import { SortKey, sortKeys } from "@/lib/filtering";
import OutcomePagination from "./OutcomePagination";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRouter } from "nextjs-toploader/app";
import { useFilterHref } from "@/lib/useFilterHref";

const sortKeyLabels: Record<SortKey, string> = {
  relevance: "Relevance",
  lastUpdated: "Last updated",
  applicationDate: "Application date",
  concludedDate: "Date of conclusion",
  bargainingUnitSize: "Bargaining unit size",
};

type Props = {
  nResults: number;
  pageSize: number;
};

export default function ResultListControls({ nResults, pageSize }: Props) {
  const router = useRouter();
  const filterHref = useFilterHref({ resetOnNavigate: new Set(["page"]) });

  return (
    <div className="flex justify-center items-center md:justify-end pl-2">
      <div className="mr-auto">
        <strong className="font-bold">{nResults}</strong>{" "}
        {nResults === 1 ? "result" : "results"}
      </div>
      <Select
        defaultValue="relevance"
        form="outcomes-search-form"
        name="sort"
        onValueChange={(value) => {
          router.push(filterHref.replace("sort", value).urlString);
        }}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {sortKeys.map((key) => (
            <SelectItem key={key} value={key}>
              {sortKeyLabels[key]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <OutcomePagination
        className="hidden md:block"
        totalPages={Math.ceil(nResults / pageSize)}
      />
    </div>
  );
}
