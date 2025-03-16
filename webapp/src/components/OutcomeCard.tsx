import dayjs from "dayjs";
import { ExternalLinkIcon } from "@radix-ui/react-icons";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Timeline } from "@/components/timeline/timeline";
import DecisionTimelineItem from "@/components/DecisionTimelineItem";
import { Outcome } from "@/lib/types";

type Props = {
  outcome: Outcome;
};

const OutcomeCard = ({ outcome }: Props) => (
  <Card>
    <CardHeader className="space-y-0 flex flex-row items-end justify-between">
      <CardTitle className="text-xl">{outcome.title}</CardTitle>
      <div className="flex flex-row space-x-2">
        <a
          className="flex flex-row items-center justify-center space-x-2 rounded-full border px-2.5 py-0.5 text-xs border-transparent bg-slate-200 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 hover:bg-slate-300"
          href={outcome.cacUrl}
          target="_blank"
        >
          Last updated:&nbsp;
          <time dateTime={outcome.lastUpdated}>
            {dayjs(outcome.lastUpdated).format("D MMMM YYYY")}
          </time>
          <ExternalLinkIcon className="size-3" />
        </a>
      </div>
    </CardHeader>
    <CardContent>
      <Timeline className="ml-2">
        {outcome.events.map((e) => (
          <DecisionTimelineItem key={e.type.value} event={e} />
        ))}
      </Timeline>
    </CardContent>
  </Card>
);

export default OutcomeCard;
