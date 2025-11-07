import { Card, CardContent } from "@/components/ui/card";
import { CategoryCounts } from "@/lib/queries/dashboard";
import { cn } from "@/lib/utils";
import { Skeleton } from "../ui/skeleton";

type Props = {
  data?: CategoryCounts;
};

function CountCard({
  title,
  count,
  colorClass,
}: {
  title: string;
  count?: number;
  colorClass: string;
}) {
  return (
    <Card>
      <CardContent className="py-4 xs:py-6 h-full">
        <div className="flex flex-col items-center justify-center space-y-1 xs:space-y-2 h-full">
          <div
            className={cn(`text-4xl sm:text-5xl font-extrabold`, colorClass)}
          >
            {count?.toLocaleString() ?? <Skeleton className="w-full h-10" />}
          </div>
          <div className="text-xs xs:text-sm font-medium text-muted-foreground">
            {title}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function CategoryCountCards({ data }: Props) {
  return (
    <>
      <CountCard
        title="Successful"
        count={data?.successful}
        colorClass="text-green-600 dark:text-green-500"
      />
      <CountCard
        title="Unsuccessful"
        count={data?.unsuccessful}
        colorClass="text-red-600 dark:text-red-500"
      />
      <CountCard
        title="Pending"
        count={data?.pending}
        colorClass="text-amber-600 dark:text-amber-500"
      />
      <CountCard
        title="Withdrawn"
        count={data?.withdrawn}
        colorClass="text-slate-600 dark:text-slate-400"
      />
    </>
  );
}
