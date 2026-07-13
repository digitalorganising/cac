import { Suspense } from "react";
import { SearchParams } from "nuqs/server";
import AverageDurationCardsClient from "@/components/dashboard/AverageDurationCards";
import CategoryCountCardsClient from "@/components/dashboard/CategoryCountCards";
import DashboardCard from "@/components/dashboard/DashboardCard";
import DashboardUnionFilter from "@/components/dashboard/DashboardUnionFilter";
import {
  ApplicationsPerUnionChart,
  ApplicationsPerUnionPer1000MembersChart,
  ApplicationsReceivedPerMonthChart,
  AverageDurationCards,
  BargainingUnitSizeChart,
  BargainingUnitSizeVsTurnoutChart,
  CategoryCountCards,
  RecognitionToMethodAgreedChart,
  TimeToAcceptanceChart,
  TimeToConclusionChart,
  TopIndustrialSectionsChart,
} from "@/components/dashboard/dashboard-charts";
import { getAllDashboardData } from "@/lib/queries/dashboard";
import { appSearchParamsCache } from "@/lib/search-params";

export const metadata = {
  title: "Dashboard",
};

export default async function Dashboard({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await appSearchParamsCache.parse(searchParams);
  const unions = params["parties.unions"];
  const hasUnionFilter = unions.length > 0;
  const dashboardDataPromise = getAllDashboardData(
    hasUnionFilter ? { "parties.unions": unions } : {},
  );

  return (
    <div className="mt-12">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-6">
        <Suspense fallback={<CategoryCountCardsClient data={undefined} />}>
          <CategoryCountCards
            promise={dashboardDataPromise}
            unions={unions}
          />
        </Suspense>
        <Suspense fallback={<AverageDurationCardsClient data={undefined} />}>
          <AverageDurationCards promise={dashboardDataPromise} />
        </Suspense>
      </div>
      <DashboardUnionFilter unions={unions} />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-6">
        {!hasUnionFilter && (
          <>
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
          </>
        )}
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
        <DashboardCard
          className="col-span-2"
          title="Recognition to method agreed"
          description="Distribution of time between union recognition and declared bargaining method agreed"
        >
          <RecognitionToMethodAgreedChart promise={dashboardDataPromise} />
        </DashboardCard>
        <DashboardCard
          className="col-span-2"
          title="Top industrial sections"
          description="The ten most common industry sections among employers with company data"
        >
          <TopIndustrialSectionsChart promise={dashboardDataPromise} />
        </DashboardCard>
      </div>
    </div>
  );
}
