import { Card, CardContent } from "@/components/ui/card";
import { formatSecondsDuration } from "@/lib/duration";
import { AverageDurations } from "@/lib/queries/dashboard";
import { cn } from "@/lib/utils";
import { Skeleton } from "../ui/skeleton";

type Props = {
  data?: AverageDurations;
};

function DurationCard({
  title,
  duration,
  colorClass,
}: {
  title: string;
  duration?: number;
  colorClass: string;
}) {
  return (
    <Card>
      <CardContent className="py-4 xs:py-6 h-full">
        <div className="flex flex-col items-center justify-center space-y-1 xs:space-y-2 h-full">
          <div
            className={cn(`text-2xl sm:text-3xl font-extrabold`, colorClass)}
          >
            {duration !== undefined ? (
              formatSecondsDuration(duration)
            ) : (
              <Skeleton className="w-full h-10" />
            )}
          </div>
          <div className="text-xs xs:text-sm font-medium text-muted-foreground text-center">
            {title}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function AverageDurationCards({ data }: Props) {
  return (
    <>
      <DurationCard
        title="Avg. Time to Success"
        duration={data?.successful}
        colorClass="text-green-600 dark:text-green-500"
      />
      <DurationCard
        title="Avg. Time to Failure"
        duration={data?.unsuccessful}
        colorClass="text-red-600 dark:text-red-500"
      />
      <DurationCard
        title="Avg. Duration (Pending)"
        duration={data?.pending}
        colorClass="text-amber-600 dark:text-amber-500"
      />
      <DurationCard
        title="Avg. Time to Withdrawal"
        duration={data?.withdrawn}
        colorClass="text-slate-600 dark:text-slate-400"
      />
    </>
  );
}
