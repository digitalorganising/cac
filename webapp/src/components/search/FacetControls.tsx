import { Entries } from "type-fest";
import { Facets } from "@/lib/queries/facets";
import BargainingUnitSizeSelect from "./BargainingUnitSizeSelect";
import EventDateSelect from "./EventDateSelect";
import { FacetSelectDesktop } from "./FacetSelect";
import { filterLabels } from "./common";

export default async function FacetControls({
  facetsPromise,
}: {
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  return (
    <>
      {(
        Object.entries(facets.multiSelect) as Entries<Facets["multiSelect"]>
      ).map(([name, buckets]) => (
        <FacetSelectDesktop
          key={name}
          label={filterLabels[name] ?? ""}
          name={name}
          form="outcomes-search-form"
          options={buckets.map(({ value, label, count }) => ({
            value: value.toString(),
            label: `${label ?? value} (${count})`,
          }))}
        />
      ))}
      <EventDateSelect />
      <BargainingUnitSizeSelect
        bins={facets.histogram["bargainingUnit.size"].map(
          ({ value, count }) => ({
            value: Number(value),
            freq: count,
          }),
        )}
      />
    </>
  );
}
