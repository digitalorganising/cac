import { Suspense } from "react";
import AverageDurationCardsClient from "@/components/dashboard/AverageDurationCards";
import CategoryCountCardsClient from "@/components/dashboard/CategoryCountCards";
import DashboardCard from "@/components/dashboard/DashboardCard";
import {
  ApplicationsPerUnionChart,
  AverageDurationCards,
  BargainingUnitSizeChart,
  BargainingUnitSizeVsTurnoutChart,
  CategoryCountCards,
  TimeToAcceptanceChart,
  TimeToConclusionChart,
} from "@/components/dashboard/dashboard-charts";
import { getAllDashboardData } from "@/lib/queries/dashboard";

export default function Dashboard() {
  const dashboardDataPromise = getAllDashboardData();

  return (
    <div className="space-y-6 mt-12">
      <div className="mb-8 space-y-6">
        <Suspense fallback={<CategoryCountCardsClient data={undefined} />}>
          <CategoryCountCards promise={dashboardDataPromise} />
        </Suspense>
        <Suspense fallback={<AverageDurationCardsClient data={undefined} />}>
          <AverageDurationCards promise={dashboardDataPromise} />
        </Suspense>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          className="lg:col-span-2"
          title="Applications per Union"
          description="Breakdown of applications by union, showing successful, unsuccessful, pending, and withdrawn cases"
        >
          <ApplicationsPerUnionChart promise={dashboardDataPromise} />
        </DashboardCard>
        {/* <DashboardCard
          title="Time to Acceptance"
          description="Distribution of time taken from application to acceptance"
        >
         
            <TimeToAcceptanceChart promise={dashboardDataPromise} />
        </DashboardCard> */}
        <DashboardCard
          className="lg:col-span-3"
          title="Bargaining Unit Sizes"
          description="Distribution of bargaining unit sizes across different outcome categories"
        >
          <BargainingUnitSizeChart promise={dashboardDataPromise} />
        </DashboardCard>
        <DashboardCard
          className="lg:col-span-2"
          title="Time to Conclusion"
          description="Distribution of time taken to reach conclusion, comparing successful and unsuccessful outcomes"
        >
          <TimeToConclusionChart promise={dashboardDataPromise} />
        </DashboardCard>
        <DashboardCard
          className="lg:col-span-3"
          title="Bargaining Unit Size vs Ballot Turnout"
          description="Relationship between bargaining unit size and ballot turnout percentage"
        >
          <BargainingUnitSizeVsTurnoutChart promise={dashboardDataPromise} />
        </DashboardCard>
      </div>
    </div>
  );
}
