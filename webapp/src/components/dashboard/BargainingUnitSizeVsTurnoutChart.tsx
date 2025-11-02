"use client";

import { useMemo } from "react";
import { Cell, ComposedChart, Line, Scatter, XAxis, YAxis } from "recharts";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
} from "@/components/ui/chart";
import { BargainingUnitSizeVsTurnoutData } from "@/lib/queries/dashboard";

type Props = {
  data: BargainingUnitSizeVsTurnoutData;
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
  regression: {
    label: "Regression Line",
    color: "hsl(0, 0%, 50%)",
  },
};

const MAX_X = 1000;

const linearRegression = (data: BargainingUnitSizeVsTurnoutData) => {
  if (data.length === 0) return undefined;

  const n = data.length;
  let sumX = 0;
  let sumY = 0;
  let sumXY = 0;
  let sumXX = 0;
  for (const point of data) {
    sumX += point.size;
    sumY += point.turnout;
    sumXY += point.size * point.turnout;
    sumXX += point.size * point.size;
  }
  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;
  return { slope, intercept };
};

export default function BargainingUnitSizeVsTurnoutChart({ data }: Props) {
  const filteredData = useMemo(
    () => data.filter((d) => d.size <= MAX_X),
    [data],
  );
  const regression = useMemo(
    () => linearRegression(filteredData),
    [filteredData],
  );
  return (
    <ChartContainer config={chartConfig} className="h-[400px] w-full">
      <ComposedChart margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <XAxis
          type="number"
          dataKey="size"
          name="Bargaining Unit Size"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          domain={[0, MAX_X]}
          tickCount={20}
          label={{
            value: "Bargaining Unit Size",
            position: "insideBottom",
            offset: -5,
            style: { textAnchor: "middle" },
          }}
        />
        <YAxis
          type="number"
          dataKey="turnout"
          name="Turnout %"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          domain={[0, 100]}
          label={{
            value: "Turnout %",
            angle: -90,
            position: "insideLeft",
            style: { textAnchor: "middle" },
          }}
        />
        <ChartTooltip
          cursor={{ strokeDasharray: "3 3" }}
          content={({ active, payload }) => {
            if (active && payload && payload[0]) {
              const point = payload[0].payload as {
                size: number;
                turnout: number;
                title: string;
              };
              return (
                <div className="border-border/50 bg-background rounded-lg border px-2.5 py-1.5 text-xs shadow-xl">
                  <div className="font-medium mb-1.5">{point.title}</div>
                  <div className="text-muted-foreground">
                    Turnout: {point.turnout.toFixed(1)}%
                  </div>
                </div>
              );
            }
            return null;
          }}
        />
        {regression && (
          <Line
            name="regression"
            type="linear"
            dataKey="turnout"
            activeDot={false}
            dot={false}
            data={[
              { size: 0, turnout: regression.intercept },
              {
                size: MAX_X,
                turnout: regression.intercept + regression.slope * MAX_X,
              },
            ]}
            stroke="var(--color-regression)"
            strokeWidth={1}
            strokeDasharray="4 4"
          />
        )}
        <Scatter dataKey="turnout" name="Turnout" data={filteredData}>
          {filteredData.map((d) => (
            <Cell
              key={`${d.size}-${d.turnout}-${d.title}`}
              fill={
                d.success
                  ? "var(--color-successful)"
                  : "var(--color-unsuccessful)"
              }
            />
          ))}
        </Scatter>
      </ComposedChart>
    </ChartContainer>
  );
}
