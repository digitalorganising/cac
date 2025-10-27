import { SearchParams } from "nuqs/server";
import { FacetingControls } from "@/components/facets";
import { PAGE_SIZE } from "@/lib/queries/outcomes";
import { appSearchParamsToOutcomesOptions } from "@/lib/queries/util";
import { appSearchParamsCache } from "@/lib/search-params";

export default async function DefaultFaceting({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await appSearchParamsCache.parse(searchParams);
  const options = appSearchParamsToOutcomesOptions(PAGE_SIZE, params);
  return <FacetingControls options={options} />;
}
