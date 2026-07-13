"use client";

import { Bar, BarChart, XAxis, YAxis } from "recharts";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { RecognitionToMethodAgreedData } from "@/lib/queries/dashboard";
import { CHART_MARGIN } from "./DashboardCard";

type Props = {
  data: RecognitionToMethodAgreedData;
};

const chartConfig: ChartConfig = {
  count: {
    label: "Outcomes",
    color: "hsl(221, 83%, 53%)",
  },
};

export default function RecognitionToMethodAgreedChart({ data }: Props) {
  return (
    <ChartContainer config={chartConfig} className="h-[400px] w-full">
      <BarChart data={data} margin={CHART_MARGIN}>
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
            offset: -10,
            style: { textAnchor: "middle" },
          }}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          allowDecimals={false}
        />
        <ChartTooltip
          content={
            <ChartTooltipContent
              labelFormatter={(_, payload) => {
                const timeRange = payload?.[0]?.payload?.timeRange;
                if (timeRange === undefined) return "";
                if (Number(timeRange) === 51) {
                  return "51+ weeks";
                }
                return `${timeRange}-${Number(timeRange) + 1} weeks`;
              }}
            />
          }
        />
        <Bar dataKey="count" fill="var(--color-count)" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ChartContainer>
  );
}
