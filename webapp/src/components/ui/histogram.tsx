import { Bar, BarChart, Cell } from "recharts";
import { ChartContainer } from "./chart";
import { cn } from "@/lib/utils";

export type Bin = { value: number; freq: number };

export default function Histogram({
  bins,
  min,
  max,
  className,
}: {
  bins: Bin[];
  min: number;
  max: number;
  className?: string;
}) {
  return (
    <ChartContainer config={{}} className={cn("px-3", className)}>
      <BarChart data={bins} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
        <Bar dataKey="freq" isAnimationActive={false}>
          {bins.map((bin) => (
            <Cell
              key={bin.value}
              fill={
                bin.value >= min && bin.value <= max
                  ? "var(--color-primary)"
                  : "var(--color-secondary)"
              }
            />
          ))}
        </Bar>
      </BarChart>
    </ChartContainer>
  );
}
