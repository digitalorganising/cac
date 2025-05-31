import { Suspense } from "react";
import StreamingMultiSelect from "./StreamingMultiSelect";
import { SelectTrigger } from "@/components/ui/multi-select";
import { filterLabels } from "./common";

const facets = ["parties.unions", "state", "events.type"] as const;

export default function Facets({
  facetsPromise,
}: {
  facetsPromise: Promise<
    Record<string, { value: string; label?: string; count: number }[]>
  >;
}) {
  return (
    <div className="flex justify-center items-center md:justify-start gap-4 py-4">
      <Suspense
        fallback={facets.map((name) => (
          <SelectTrigger disabled key={name}>
            {filterLabels[name]}
          </SelectTrigger>
        ))}
      >
        {facets.map((name) => (
          <StreamingMultiSelect
            key={name}
            label={filterLabels[name]}
            name={name}
            promiseOptions={facetsPromise.then((facets) =>
              facets[name].map(({ value, label, count }) => ({
                value,
                label: `${label ?? value} (${count})`,
              })),
            )}
            form="outcomes-search-form"
          />
        ))}
      </Suspense>
    </div>
  );
}
