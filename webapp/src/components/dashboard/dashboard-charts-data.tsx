import {
  getApplicationsPerUnion,
  getBargainingUnitSizeVsTurnout,
  getBargainingUnitSizes,
  getCategoryCounts,
  getTimeToAcceptance,
  getTimeToConclusion,
} from "@/lib/queries/dashboard";
import ApplicationsPerUnionChartClient from "./ApplicationsPerUnionChart";
import BargainingUnitSizeChartClient from "./BargainingUnitSizeChart";
import BargainingUnitSizeVsTurnoutChartClient from "./BargainingUnitSizeVsTurnoutChart";
import CategoryCountCardsClient from "./CategoryCountCards";
import TimeToAcceptanceChartClient from "./TimeToAcceptanceChart";
import TimeToConclusionChartClient from "./TimeToConclusionChart";

export async function CategoryCountCards() {
  const data = await getCategoryCounts();
  return <CategoryCountCardsClient data={data} />;
}

export async function ApplicationsPerUnionChart() {
  const data = await getApplicationsPerUnion();
  return <ApplicationsPerUnionChartClient data={data} />;
}

export async function BargainingUnitSizeChart() {
  const data = await getBargainingUnitSizes();
  return <BargainingUnitSizeChartClient data={data} />;
}

export async function TimeToAcceptanceChart() {
  const data = await getTimeToAcceptance();
  return <TimeToAcceptanceChartClient data={data} />;
}

export async function TimeToConclusionChart() {
  const data = await getTimeToConclusion();
  return <TimeToConclusionChartClient data={data} />;
}

export async function BargainingUnitSizeVsTurnoutChart() {
  const data = await getBargainingUnitSizeVsTurnout();
  return <BargainingUnitSizeVsTurnoutChartClient data={data} />;
}
