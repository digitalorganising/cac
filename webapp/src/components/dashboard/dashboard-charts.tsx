import { type DashboardData } from "@/lib/queries/dashboard";
import ApplicationsPerUnionChartClient from "./ApplicationsPerUnionChart";
import ApplicationsPerUnionPer1000MembersChartClient from "./ApplicationsPerUnionPer1000MembersChart";
import ApplicationsReceivedPerMonthChartClient from "./ApplicationsReceivedPerMonthChart";
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

export async function ApplicationsPerUnionPer1000MembersChart({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return (
    <ApplicationsPerUnionPer1000MembersChartClient
      data={data.applicationsPerUnion}
    />
  );
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

export async function ApplicationsReceivedPerMonthChart({
  promise,
}: {
  promise: Promise<DashboardData>;
}) {
  const data = await promise;
  return (
    <ApplicationsReceivedPerMonthChartClient
      data={data.applicationsReceivedPerMonth}
    />
  );
}
