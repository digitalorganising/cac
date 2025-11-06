"use client";

import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { ApplicationsReceivedPerMonthData } from "@/lib/queries/dashboard";

type Props = {
  data: ApplicationsReceivedPerMonthData;
};

const chartConfig: ChartConfig = {
  count: {
    label: "Applications",
    color: "hsl(221, 83%, 53%)",
  },
};

export default function ApplicationsReceivedPerMonthChart({ data }: Props) {
  return (
    <ChartContainer config={chartConfig} className="h-[400px] w-full">
      <LineChart
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="month"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          tickFormatter={(value) => {
            const date = new Date(value);
            return date.toLocaleDateString("en-GB", {
              month: "short",
              year: "numeric",
            });
          }}
          label={{
            value: "Month",
            position: "insideBottom",
            offset: -5,
            style: { textAnchor: "middle" },
          }}
        />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} />
        <ChartTooltip
          content={({ active, payload }) => {
            if (!active || !payload || payload.length === 0) return null;
            const data = payload[0]
              .payload as ApplicationsReceivedPerMonthData[0];
            const date = new Date(data.month);
            return (
              <div className="border-border/50 bg-background rounded-lg border px-2.5 py-1.5 text-xs shadow-xl">
                <div className="font-medium mb-1.5">
                  {date.toLocaleDateString("en-GB", {
                    month: "long",
                    year: "numeric",
                  })}
                </div>
                <div className="text-muted-foreground">
                  Applications: {data.count}
                </div>
              </div>
            );
          }}
        />
        <Line
          type="linear"
          dataKey="count"
          stroke="var(--color-count)"
          strokeWidth={2}
          dot={true}
        />
      </LineChart>
    </ChartContainer>
  );
}
