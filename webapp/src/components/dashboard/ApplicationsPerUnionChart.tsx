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
import { ApplicationsPerUnionData } from "@/lib/queries/dashboard";
import { CHART_MARGIN } from "./DashboardCard";

type Props = {
  data: ApplicationsPerUnionData;
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

// Incredibly lazy but also incredibly pragmatic
const fixNames = (
  entry: ApplicationsPerUnionData[number],
): ApplicationsPerUnionData[number] => ({
  ...entry,
  union: (() => {
    switch (entry.union) {
      case "United Voices of the World":
        return "UWV";
      case "Unite the Union":
        return "Unite";
      default:
        return entry.union;
    }
  })(),
});

export default function ApplicationsPerUnionChart({ data }: Props) {
  return (
    <ChartContainer config={chartConfig} className="h-[400px] w-full">
      <BarChart data={data.map(fixNames)} margin={CHART_MARGIN}>
        <XAxis
          dataKey="union"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          angle={-45}
          textAnchor="end"
          height={70}
          interval={0}
        />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent className="flex-wrap" />} />
        <Bar
          dataKey="withdrawn"
          stackId="a"
          fill="var(--color-withdrawn)"
          radius={[0, 0, 0, 0]}
        />
        <Bar
          dataKey="pending"
          stackId="a"
          fill="var(--color-pending)"
          radius={[0, 0, 0, 0]}
        />
        <Bar
          dataKey="unsuccessful"
          stackId="a"
          fill="var(--color-unsuccessful)"
          radius={[0, 0, 0, 0]}
        />
        <Bar
          dataKey="successful"
          stackId="a"
          fill="var(--color-successful)"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ChartContainer>
  );
}
