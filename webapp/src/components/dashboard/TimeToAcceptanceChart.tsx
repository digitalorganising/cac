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
import { TimeToAcceptanceData } from "@/lib/queries/dashboard";

type Props = {
  data: TimeToAcceptanceData;
};

const chartConfig: ChartConfig = {
  accepted: {
    label: "Accepted",
    color: "hsl(142, 76%, 36%)",
  },
  rejected: {
    label: "Rejected",
    color: "hsl(0, 84%, 60%)",
  },
};

export default function TimeToAcceptanceChart({ data }: Props) {
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
          domain={[0, 52]}
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
        <Bar dataKey="accepted" stackId="a" fill="var(--color-accepted)" />
        <Bar dataKey="rejected" stackId="a" fill="var(--color-rejected)" />
      </BarChart>
    </ChartContainer>
  );
}
