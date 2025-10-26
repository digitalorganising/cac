import { Input } from "./input";
import { Label } from "./label";

const ensureNumber = (value: string) => Number(value.replace(/\D/, ""));

export function SliderInput({
  name,
  label,
  value,
  onChange,
  form,
  editable = true,
}: {
  name: string;
  label: string;
  value: number | string;
  onChange: (value: number) => void;
  form?: string;
  editable?: boolean;
}) {
  return (
    <div>
      <Label htmlFor={name} className="text-xs">
        {label}
      </Label>
      <Input
        id={name}
        className="w-16 text-center text-sm h-8 px-1 py-0"
        type="text"
        value={value}
        onChange={(e) => onChange(ensureNumber(e.target.value))}
        form={form}
        disabled={!editable}
      />
    </div>
  );
}
