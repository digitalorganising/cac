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
import { TopIndustrialSectionsData } from "@/lib/queries/dashboard";

type Props = {
  data: TopIndustrialSectionsData;
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

const CHART_MARGIN = { top: 8, right: 16, left: 4, bottom: 8 };

export default function TopIndustrialSectionsChart({ data }: Props) {
  if (data.length === 0) {
    return null;
  }

  return (
    <ChartContainer
      config={chartConfig}
      className="h-[400px] w-full text-[0.675rem] xs:text-xs"
    >
      <BarChart
        layout="vertical"
        data={data}
        margin={CHART_MARGIN}
        barCategoryGap="18%"
      >
        <XAxis
          type="number"
          allowDecimals={false}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
        />
        <YAxis
          type="category"
          dataKey="section"
          width={200}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          interval={0}
        />
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
          radius={[0, 4, 4, 0]}
        />
      </BarChart>
    </ChartContainer>
  );
}
