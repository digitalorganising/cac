"use client";

import MultiSelect from "@/components/ui/multi-select";
import { AppQueryParams } from "@/lib/filtering";
import { useOptimisticFilterRouter } from "@/lib/useOptimisticFilterRouter";
import { arr } from "@/lib/utils";
import { use } from "react";

type MultiSelectProps = React.ComponentProps<typeof MultiSelect>;

export default function StreamingMultiSelect({
  promiseOptions,
  ...props
}: Omit<MultiSelectProps, "options" | "selected" | "onSelect"> & {
  promiseOptions: Promise<MultiSelectProps["options"]>;
  name: keyof AppQueryParams;
}) {
  const filterRouter = useOptimisticFilterRouter({
    resetOnNavigate: new Set(["page"]),
  });
  const selected = new Set(arr(filterRouter.params[props.name] ?? []));
  const options = use(promiseOptions);

  const handleSelect = (value: string, checked: boolean) => {
    if (checked) {
      filterRouter.add(props.name, value);
    } else {
      filterRouter.delete(props.name, value);
    }
  };

  return (
    <MultiSelect
      {...props}
      options={options}
      selected={selected}
      onSelect={handleSelect}
    />
  );
}
