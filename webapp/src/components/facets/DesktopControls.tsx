import {
  BarChartIcon,
  ChevronDownIcon,
  ClockIcon,
} from "@radix-ui/react-icons";
import { Entries } from "type-fest";
import { Facets } from "@/lib/queries/facets";
import { DateRange } from "../ui/date-range";
import { InputTriggerButton } from "../ui/input-trigger-button";
import { BargainingUnitSizeSelect } from "./BargainingUnitSizeSelect";
import { DurationSelect } from "./DurationSelect";
import { EventDateSelect } from "./EventDateSelect";
import { MultiSelectDesktop } from "./MultiSelect";
import { filterLabels } from "./common";

export function DesktopControlsFallback() {
  return (
    <>
      {["Unions", "Status", "Events"].map((label) => (
        <InputTriggerButton
          key={label}
          loading={true}
          aria-label={`${label} filter`}
          icon={<ChevronDownIcon className="size-4 opacity-50" />}
        >
          {label}
        </InputTriggerButton>
      ))}
      <DateRange loading={true} />
      <InputTriggerButton loading={true} icon={<BarChartIcon />}>
        Bargaining Unit Size
      </InputTriggerButton>
      <InputTriggerButton loading={true} icon={<ClockIcon />}>
        Duration
      </InputTriggerButton>
    </>
  );
}

export default async function DesktopControls({
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
        <MultiSelectDesktop
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
      <DurationSelect />
    </>
  );
}
