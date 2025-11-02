import { Suspense } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";

type Props = {
  title: string;
  description: string;
  children: React.ReactNode;
  className?: string;
};

export default async function DashboardCard({
  title,
  description,
  children,
  className,
}: Props) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <Suspense fallback={<div>Loading...</div>}>{children}</Suspense>
      </CardContent>
    </Card>
  );
}
