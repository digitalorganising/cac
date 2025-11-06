import { Card, CardContent } from "@/components/ui/card";
import { formatSecondsDuration } from "@/lib/duration";
import { AverageDurations } from "@/lib/queries/dashboard";
import { Skeleton } from "../ui/skeleton";

type Props = {
  data?: AverageDurations;
};

export default function AverageDurationCards({ data }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="text-3xl font-extrabold text-green-600 dark:text-green-500">
              {data?.successful !== undefined ? (
                formatSecondsDuration(data.successful)
              ) : (
                <Skeleton className="w-full h-10" />
              )}
            </div>
            <div className="text-sm font-medium text-muted-foreground">
              Avg. Time to Completion (Successful)
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="text-3xl font-extrabold text-red-600 dark:text-red-500">
              {data?.unsuccessful !== undefined ? (
                formatSecondsDuration(data.unsuccessful)
              ) : (
                <Skeleton className="w-full h-10" />
              )}
            </div>
            <div className="text-sm font-medium text-muted-foreground">
              Avg. Time to Completion (Unsuccessful)
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="text-3xl font-extrabold text-amber-600 dark:text-amber-500">
              {data?.pending !== undefined ? (
                formatSecondsDuration(data.pending)
              ) : (
                <Skeleton className="w-full h-10" />
              )}
            </div>
            <div className="text-sm font-medium text-muted-foreground">
              Avg. Duration (Pending)
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="text-3xl font-extrabold text-slate-600 dark:text-slate-400">
              {data?.withdrawn !== undefined ? (
                formatSecondsDuration(data.withdrawn)
              ) : (
                <Skeleton className="w-full h-10" />
              )}
            </div>
            <div className="text-sm font-medium text-muted-foreground">
              Avg. Time to Completion (Withdrawn)
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
