"use client";

import { Bar, BarChart, XAxis, YAxis } from "recharts";
import {
  ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { BargainingUnitSizeData } from "@/lib/queries/dashboard";

type Props = {
  data: BargainingUnitSizeData;
};

const chartConfig: ChartConfig = {
  successful: {
    label: "Successful",
    color: "hsl(142, 76%, 36%)",
  },
  unsuccessful: {
    label: "Unsuccessful",
    color: "hsl(0, 84%, 60%)",
  },
  pending: {
    label: "Pending",
    color: "hsl(38, 92%, 50%)",
  },
  withdrawn: {
    label: "Withdrawn",
    color: "hsl(215, 16%, 47%)",
  },
};

export default function BargainingUnitSizeChart({ data }: Props) {
  return (
    <ChartContainer config={chartConfig} className="h-[400px] w-full">
      <BarChart
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        <XAxis
          dataKey="sizeRange"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          type="number"
          domain={[0, 500]}
          tickCount={20}
        />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
        <Bar dataKey="withdrawn" stackId="a" fill="var(--color-withdrawn)" />
        <Bar dataKey="pending" stackId="a" fill="var(--color-pending)" />
        <Bar
          dataKey="unsuccessful"
          stackId="a"
          fill="var(--color-unsuccessful)"
        />
        <Bar dataKey="successful" stackId="a" fill="var(--color-successful)" />
      </BarChart>
    </ChartContainer>
  );
}
