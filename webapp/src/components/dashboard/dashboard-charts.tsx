import { type DashboardData } from "@/lib/queries/dashboard";
import ApplicationsPerUnionChartClient from "./ApplicationsPerUnionChart";
import AverageDurationCardsClient from "./AverageDurationCards";
import BargainingUnitSizeChartClient from "./BargainingUnitSizeChart";
import BargainingUnitSizeVsTurnoutChartClient from "./BargainingUnitSizeVsTurnoutChart";
import CategoryCountCardsClient from "./CategoryCountCards";
import TimeToAcceptanceChartClient from "./TimeToAcceptanceChart";
import TimeToConclusionChartClient from "./TimeToConclusionChart";

// Wrapper components that await the promise
export async function CategoryCountCards({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return <CategoryCountCardsClient data={data.categoryCounts} />;
}

export async function ApplicationsPerUnionChart({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return <ApplicationsPerUnionChartClient data={data.applicationsPerUnion} />;
}

export async function BargainingUnitSizeChart({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return <BargainingUnitSizeChartClient data={data.bargainingUnitSizes} />;
}

export async function TimeToAcceptanceChart({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return <TimeToAcceptanceChartClient data={data.timeToAcceptance} />;
}

export async function TimeToConclusionChart({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return <TimeToConclusionChartClient data={data.timeToConclusion} />;
}

export async function BargainingUnitSizeVsTurnoutChart({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return (
    <BargainingUnitSizeVsTurnoutChartClient
      data={data.bargainingUnitSizeVsTurnout}
    />
  );
}

export async function AverageDurationCards({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return <AverageDurationCardsClient data={data.averageDurations} />;
}
