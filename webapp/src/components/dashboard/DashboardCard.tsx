import { Suspense } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Skeleton } from "../ui/skeleton";

type Props = {
  title: string;
  description: string;
  children: React.ReactNode;
  className?: string;
};

export const CHART_MARGIN = { top: 15, right: 40, left: -10, bottom: 10 };

function ChartLoading() {
  return <Skeleton className="w-full h-[400px]" />;
}

export default async function DashboardCard({
  title,
  description,
  children,
  className,
}: Props) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <Suspense fallback={<ChartLoading />}>{children}</Suspense>
      </CardContent>
    </Card>
  );
}
