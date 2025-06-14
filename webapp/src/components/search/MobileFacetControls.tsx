import Link from "next/link";
import { Entries } from "type-fest";
import { Facets } from "@/lib/queries/facets";
import {
  appSearchParamsCache,
  appSearchParamsSerializer,
} from "@/lib/search-params";
import { Accordion } from "../ui/accordion";
import { Button } from "../ui/button";
import { DialogClose } from "../ui/dialog";
import { FacetSelectMobile } from "./FacetSelect";
import { filterLabels } from "./common";

export default async function MobileFacetControls({
  facetsPromise,
}: {
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  const query = appSearchParamsCache.get("query");
  return (
    <div>
      <Accordion type="multiple">
        {(
          Object.entries(facets.multiSelect) as Entries<Facets["multiSelect"]>
        ).map(([name, buckets]) => (
          <FacetSelectMobile
            key={name}
            label={filterLabels[name] ?? ""}
            name={name}
            options={buckets.map((bucket) => ({
              value: bucket.value.toString(),
              label: `${bucket.label ?? bucket.value} (${bucket.count})`,
            }))}
          />
        ))}
      </Accordion>
      <div className="fixed bottom-0 left-0 bg-white border-t border-gray-200 w-full p-4 flex justify-end items-center gap-2">
        <Button className="cursor-pointer" variant="outline" asChild>
          <Link href={appSearchParamsSerializer({ query }) || "/"}>
            Clear all
          </Link>
        </Button>
        <DialogClose asChild>
          <Button className="cursor-pointer">Show results</Button>
        </DialogClose>
      </div>
    </div>
  );
}
