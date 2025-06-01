import { filterLabels } from "./common";
import { Facets, getFacets, GetOutcomesOptions } from "@/lib/outcomes";
import { Entries } from "type-fest";
import FacetSelect from "./FacetSelect";

export default async function FacetControls({
  facetsPromise,
}: {
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  const facetEntries = Object.entries(facets) as Entries<Facets>;
  return facetEntries.map(([name, facetValues]) => (
    <FacetSelect
      key={name}
      label={filterLabels[name]}
      name={name}
      form="outcomes-search-form"
      options={facetValues.map(({ value, label, count }) => ({
        value,
        label: `${label ?? value} (${count})`,
      }))}
    />
  ));
}
