import { NextRequest } from "next/server";
import { createLoader } from "nuqs/server";
import { getOutcomes } from "@/lib/queries/outcomes";
import { appSearchParamsToOutcomesOptions } from "@/lib/queries/util";
import { appSearchParamsParser } from "@/lib/search-params";

const loadParams = createLoader(appSearchParamsParser);

export async function GET(request: NextRequest) {
  const searchParams = await loadParams(request.nextUrl.searchParams);
  const options = appSearchParamsToOutcomesOptions(15, searchParams);
  const outcomes = await getOutcomes(options);

  const currentPage = searchParams.page || 1;
  const totalPages = Math.ceil(outcomes.size / 15);

  const pageLink = (n: number) =>
    `${request.nextUrl.origin}/api/outcomes?${new URLSearchParams({
      ...Object.fromEntries(request.nextUrl.searchParams),
      page: String(n),
    })}`;

  const links = {
    nextPage: currentPage < totalPages ? pageLink(currentPage + 1) : undefined,
    previousPage: currentPage > 1 ? pageLink(currentPage - 1) : undefined,
  };

  return Response.json({
    totalResults: outcomes.size,
    ...links,
    outcomes: outcomes.docs,
  });
}
