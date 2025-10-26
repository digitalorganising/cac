import { Entries } from "type-fest";
import { Facets } from "@/lib/queries/facets";
import { appSearchParamsCache } from "@/lib/search-params";
import { Accordion } from "../ui/accordion";
import { BargainingUnitSizeSelectMobile } from "./BargainingUnitSizeSelect";
import { DurationSelectMobile } from "./DurationSelect";
import { EventDateSelectMobile } from "./EventDateSelect";
import { FacetSelectMobile } from "./FacetSelect";
import { filterLabels } from "./common";

export default async function MobileFacetControls({
  facetsPromise,
}: {
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
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
        <EventDateSelectMobile />
        <BargainingUnitSizeSelectMobile
          bins={facets.histogram["bargainingUnit.size"].map(
            ({ value, count }) => ({
              value: Number(value),
              freq: count,
            }),
          )}
        />
        <DurationSelectMobile />
      </Accordion>
    </div>
  );
}
