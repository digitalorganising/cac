import { Suspense } from "react";
import AverageDurationCardsClient from "@/components/dashboard/AverageDurationCards";
import CategoryCountCardsClient from "@/components/dashboard/CategoryCountCards";
import DashboardCard from "@/components/dashboard/DashboardCard";
import {
  ApplicationsPerUnionChart,
  ApplicationsPerUnionPer1000MembersChart,
  ApplicationsReceivedPerMonthChart,
  AverageDurationCards,
  BargainingUnitSizeChart,
  BargainingUnitSizeVsTurnoutChart,
  CategoryCountCards,
  TimeToAcceptanceChart,
  TimeToConclusionChart,
} from "@/components/dashboard/dashboard-charts";
import { getAllDashboardData } from "@/lib/queries/dashboard";

export const metadata = {
  title: "Dashboard",
};

export default function Dashboard() {
  const dashboardDataPromise = getAllDashboardData();

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-6 mt-12">
      <Suspense fallback={<CategoryCountCardsClient data={undefined} />}>
        <CategoryCountCards promise={dashboardDataPromise} />
      </Suspense>
      <Suspense fallback={<AverageDurationCardsClient data={undefined} />}>
        <AverageDurationCards promise={dashboardDataPromise} />
      </Suspense>
      <DashboardCard
        className="col-span-2"
        title="Applications per Union"
        description="Breakdown of applications by union, showing successful, unsuccessful, pending, and withdrawn cases"
      >
        <ApplicationsPerUnionChart promise={dashboardDataPromise} />
      </DashboardCard>
      <DashboardCard
        className="col-span-2"
        title="Applications by total membership"
        description="Number of applications by each union, normalized by membership size (per 1000 members)."
      >
        <ApplicationsPerUnionPer1000MembersChart
          promise={dashboardDataPromise}
        />
      </DashboardCard>
      <DashboardCard
        className="col-span-2"
        title="Applications Received Per Month"
        description="Number of applications received per month over the last 3 years"
      >
        <ApplicationsReceivedPerMonthChart promise={dashboardDataPromise} />
      </DashboardCard>
      <DashboardCard
        className="col-span-2"
        title="Bargaining Unit Sizes"
        description="Distribution of bargaining unit sizes across different outcome categories"
      >
        <BargainingUnitSizeChart promise={dashboardDataPromise} />
      </DashboardCard>
      <DashboardCard
        className="col-span-2"
        title="Bargaining Unit Size vs Ballot Turnout"
        description="Relationship between bargaining unit size and ballot turnout percentage"
      >
        <BargainingUnitSizeVsTurnoutChart promise={dashboardDataPromise} />
      </DashboardCard>
      <DashboardCard
        className="col-span-2"
        title="Time to Conclusion"
        description="Distribution of time taken to reach conclusion, comparing successful and unsuccessful outcomes"
      >
        <TimeToConclusionChart promise={dashboardDataPromise} />
      </DashboardCard>
      <DashboardCard
        className="col-span-2"
        title="Time to Acceptance"
        description="Distribution of time taken from application to acceptance, split by accepted and rejected decisions"
      >
        <TimeToAcceptanceChart promise={dashboardDataPromise} />
      </DashboardCard>
    </div>
  );
}
