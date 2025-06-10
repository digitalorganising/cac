import { filterLabels } from "./common";
import { Facets } from "@/lib/queries/facets";
import { Entries } from "type-fest";
import FacetSelect from "./FacetSelect";
import EventDateSelect from "./EventDateSelect";
import BargainingUnitSizeSelect from "./BargainingUnitSizeSelect";

export default async function FacetControls({
  facetsPromise,
}: {
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  const bucketControls = (
    Object.entries(filterLabels) as Entries<typeof filterLabels>
  ).map(([name, label]) => {
    const buckets = facets.bucketed[name as keyof Facets["bucketed"]];
    if (!buckets) {
      return null;
    }
    return (
      <FacetSelect
        key={name}
        label={label}
        name={name}
        form="outcomes-search-form"
        options={buckets.map(({ value, label, count }) => ({
          value: value.toString(),
          label: `${label ?? value} (${count})`,
        }))}
      />
    );
  });

  return (
    <>
      {bucketControls}
      <EventDateSelect />
      <BargainingUnitSizeSelect
        bins={facets.bucketed["bargainingUnit.size"].map(
          ({ value, count }) => ({
            value: Number(value),
            freq: count,
          }),
        )}
      />
    </>
  );
}
