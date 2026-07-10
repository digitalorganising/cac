import { Facets, companyMultiSelectFacetNames, coreMultiSelectFacetNames } from "@/lib/queries/facets";
import { Accordion } from "../ui/accordion";
import { BargainingUnitSizeSelectMobile } from "./BargainingUnitSizeSelect";
import { DurationSelectMobile } from "./DurationSelect";
import { EventDateSelectMobile } from "./EventDateSelect";
import { MultiSelectMobile } from "./MultiSelect";
import { filterLabels } from "./common";

export default async function MobileControls({
  facetsPromise,
}: {
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  const renderMultiSelect = (names: readonly (keyof Facets["multiSelect"])[]) =>
    names.map((name) => (
      <MultiSelectMobile
        key={name}
        label={filterLabels[name] ?? ""}
        name={name}
        options={facets.multiSelect[name].map((bucket) => ({
          value: bucket.value.toString(),
          label: `${bucket.label ?? bucket.value} (${bucket.count})`,
        }))}
      />
    ));

  return (
    <div>
      <Accordion type="multiple">
        {renderMultiSelect(coreMultiSelectFacetNames)}
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
        {renderMultiSelect(companyMultiSelectFacetNames)}
      </Accordion>
    </div>
  );
}
