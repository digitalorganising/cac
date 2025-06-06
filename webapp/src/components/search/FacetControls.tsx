import { filterLabels } from "./common";
import { Facets } from "@/lib/queries/facets";
import { Entries } from "type-fest";
import FacetSelect from "./FacetSelect";
import { DateRange } from "../ui/date-range";
import EventDateSelect from "./EventDateSelect";

export default async function FacetControls({
  facetsPromise,
}: {
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  const bucketControls = (
    Object.entries(filterLabels) as Entries<typeof filterLabels>
  ).map(([name, label]) => {
    const buckets = facets.bucketed[name];
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
          value,
          label: `${label ?? value} (${count})`,
        }))}
      />
    );
  });

  return (
    <>
      {bucketControls}
      <EventDateSelect />
    </>
  );
}
