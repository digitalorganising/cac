"use client";

import { Card, CardContent } from "@/components/ui/card";
import { CategoryCounts } from "@/lib/queries/dashboard";
import { Skeleton } from "../ui/skeleton";

type Props = {
  data?: CategoryCounts;
};

export default function CategoryCountCards({ data }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="text-5xl font-extrabold text-green-600 dark:text-green-500">
              {data?.successful.toLocaleString() ?? (
                <Skeleton className="w-full h-10" />
              )}
            </div>
            <div className="text-sm font-medium text-muted-foreground">
              Successful
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="text-5xl font-extrabold text-red-600 dark:text-red-500">
              {data?.unsuccessful.toLocaleString() ?? (
                <Skeleton className="w-full h-10" />
              )}
            </div>
            <div className="text-sm font-medium text-muted-foreground">
              Unsuccessful
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="text-5xl font-extrabold text-amber-600 dark:text-amber-500">
              {data?.pending.toLocaleString() ?? (
                <Skeleton className="w-full h-10" />
              )}
            </div>
            <div className="text-sm font-medium text-muted-foreground">
              Pending
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="text-5xl font-extrabold text-slate-600 dark:text-slate-400">
              {data?.withdrawn.toLocaleString() ?? (
                <Skeleton className="w-full h-10" />
              )}
            </div>
            <div className="text-sm font-medium text-muted-foreground">
              Withdrawn
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
