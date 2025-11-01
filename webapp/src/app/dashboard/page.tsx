import {
  ApplicationsPerUnionChart,
  BargainingUnitSizeChart,
  CategoryCountCards,
  TimeToAcceptanceChart,
  TimeToConclusionChart,
} from "@/components/dashboard/dashboard-charts-data";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Dashboard() {
  return (
    <div className="space-y-6 mt-12">
      <div className="mb-8">
        <CategoryCountCards />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Applications per Union</CardTitle>
            <CardDescription>
              Breakdown of applications by union, showing successful,
              unsuccessful, pending, and withdrawn cases
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ApplicationsPerUnionChart />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Time to Acceptance</CardTitle>
            <CardDescription>
              Distribution of time taken from application to acceptance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TimeToAcceptanceChart />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Bargaining Unit Sizes</CardTitle>
            <CardDescription>
              Distribution of bargaining unit sizes across different outcome
              categories
            </CardDescription>
          </CardHeader>
          <CardContent>
            <BargainingUnitSizeChart />
          </CardContent>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Time to Conclusion</CardTitle>
            <CardDescription>
              Distribution of time taken to reach conclusion, comparing
              successful and unsuccessful outcomes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TimeToConclusionChart />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
