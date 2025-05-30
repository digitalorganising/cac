"use client";

import { useOptimisticFilterRouter } from "@/lib/useOptimisticFilterRouter";
import MultiSelect from "@/components/ui/multi-select";
import { arr } from "@/lib/utils";

export default function Facets() {
  const filterRouter = useOptimisticFilterRouter({
    resetOnNavigate: new Set(["page"]),
  });
  const selected = new Set(arr(filterRouter.params["parties.unions"] ?? []));

  const handleSelect = (value: string, checked: boolean) => {
    if (checked) {
      filterRouter.add("parties.unions", value);
    } else {
      filterRouter.delete("parties.unions", value);
    }
  };

  return (
    <div className="flex justify-center items-center md:justify-end pl-2">
      <MultiSelect
        options={["Prospect", "PCS", "Unite the Union"]}
        onSelect={handleSelect}
        selected={selected}
        label="Union"
        name="parties.union"
        form="outcomes-search-form"
      />
    </div>
  );
}
