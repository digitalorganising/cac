import { ChevronDownIcon } from "@radix-ui/react-icons";
import { LabelledCheckbox } from "./checkbox";
import CountBadge from "./count-badge";
import { InputTriggerButton } from "./input-trigger-button";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";
import { ScrollArea } from "./scroll-area";

type Props = {
  label: string;
  name: string;
  options: { label: string; value: string }[];
  selected: Set<string>;
  onSelect: (value: string, checked: boolean) => void;
  onClearAll?: () => void;
  form?: string;
  loading?: boolean;
};

export default function MultiSelect({
  label,
  name,
  options,
  selected,
  onSelect,
  onClearAll,
  form,
  loading,
}: Props) {
  return (
    <Popover modal={true}>
      {Array.from(selected).map((value) => (
        <input
          type="hidden"
          name={name}
          value={value}
          form={form}
          key={value}
        />
      ))}
      <PopoverTrigger asChild>
        <InputTriggerButton
          role="combobox"
          aria-label={`${label} filter`}
          loading={loading}
          icon={<ChevronDownIcon className="size-4 opacity-50" />}
        >
          {label}
          {selected.size ? <CountBadge count={selected.size} /> : null}
        </InputTriggerButton>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-fit p-0">
        <ScrollArea
          className="[&>[data-radix-scroll-area-viewport]]:max-h-[300px] p-2"
          type="auto"
        >
          {options.map((option) => (
            <LabelledCheckbox
              key={option.value}
              id={option.value}
              label={option.label}
              checked={selected.has(option.value)}
              onCheckedChange={(newChecked) => {
                onSelect(
                  option.value,
                  newChecked === "indeterminate" ? false : newChecked,
                );
              }}
            />
          ))}
        </ScrollArea>
        {onClearAll ? (
          <div className="p-0.5 border-t border-slate-200 flex justify-center items-center">
            <button
              aria-label="Clear all"
              className="text-center text-sm px-3 py-1 rounded-sm hover:bg-slate-100"
              onClick={onClearAll}
            >
              Clear all
            </button>
          </div>
        ) : null}
      </PopoverContent>
    </Popover>
  );
}
