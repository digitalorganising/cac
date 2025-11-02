import { Suspense } from "react";
import CategoryCountCardsClient from "@/components/dashboard/CategoryCountCards";
import DashboardCard from "@/components/dashboard/DashboardCard";
import {
  ApplicationsPerUnionChart,
  BargainingUnitSizeChart,
  BargainingUnitSizeVsTurnoutChart,
  CategoryCountCards,
  TimeToAcceptanceChart,
  TimeToConclusionChart,
} from "@/components/dashboard/dashboard-charts-data";

export default function Dashboard() {
  return (
    <div className="space-y-6 mt-12">
      <div className="mb-8">
        <Suspense fallback={<CategoryCountCardsClient data={undefined} />}>
          <CategoryCountCards />
        </Suspense>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          className="lg:col-span-2"
          title="Applications per Union"
          description="Breakdown of applications by union, showing successful, unsuccessful, pending, and withdrawn cases"
        >
          <ApplicationsPerUnionChart />
        </DashboardCard>
        {/* <DashboardCard
          title="Time to Acceptance"
          description="Distribution of time taken from application to acceptance"
        >
          <TimeToAcceptanceChart />
        </DashboardCard> */}
        <DashboardCard
          className="lg:col-span-3"
          title="Bargaining Unit Sizes"
          description="Distribution of bargaining unit sizes across different outcome categories"
        >
          <BargainingUnitSizeChart />
        </DashboardCard>
        <DashboardCard
          className="lg:col-span-2"
          title="Time to Conclusion"
          description="Distribution of time taken to reach conclusion, comparing successful and unsuccessful outcomes"
        >
          <TimeToConclusionChart />
        </DashboardCard>
        <DashboardCard
          className="lg:col-span-3"
          title="Bargaining Unit Size vs Ballot Turnout"
          description="Relationship between bargaining unit size and ballot turnout percentage"
        >
          <BargainingUnitSizeVsTurnoutChart />
        </DashboardCard>
      </div>
    </div>
  );
}
