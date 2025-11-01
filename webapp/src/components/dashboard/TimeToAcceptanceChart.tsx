"use client";

import { Bar, BarChart, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartConfig,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { TimeToAcceptanceData } from "@/lib/queries/dashboard";

type Props = {
  data: TimeToAcceptanceData;
};

const chartConfig: ChartConfig = {
  count: {
    label: "Applications",
    color: "hsl(221, 83%, 53%)",
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
          label={{
            value: "Weeks",
            position: "insideBottom",
            offset: -5,
            style: { textAnchor: "middle" },
          }}
        />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="count" fill="var(--color-count)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ChartContainer>
  );
}

