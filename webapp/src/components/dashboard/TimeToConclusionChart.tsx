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
import { TimeToConclusionData } from "@/lib/queries/dashboard";

type Props = {
  data: TimeToConclusionData;
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
};

export default function TimeToConclusionChart({ data }: Props) {
  return (
    <ChartContainer config={chartConfig} className="h-[400px] w-full">
      <BarChart
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
      >
        <XAxis
          dataKey="timeRange"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          type="number"
          domain={[0, 104]}
          tickCount={20}
          label={{
            value: "Weeks",
            position: "insideBottom",
            offset: -5,
            style: { textAnchor: "middle" },
          }}
        />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
        <Bar dataKey="successful" stackId="a" fill="var(--color-successful)" />
        <Bar
          dataKey="unsuccessful"
          stackId="a"
          fill="var(--color-unsuccessful)"
        />
      </BarChart>
    </ChartContainer>
  );
}
