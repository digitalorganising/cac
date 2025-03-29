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
    <CardHeader className="space-y-0 xs:space-x-2 block xs:flex flex-row-reverse items-center justify-between">
      <a
        href={outcome.cacUrl}
        target="_blank"
        className="float-right m-1 flex flex-row items-center justify-center text-nowrap xs:space-x-2 rounded-full border px-2.5 py-0.5 text-xs border-transparent bg-slate-200 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 hover:bg-slate-300"
      >
        <span className="hidden xs:inline">Last updated:&nbsp;</span>
        <time className="hidden xs:inline" dateTime={outcome.lastUpdated}>
          {dayjs(outcome.lastUpdated).format("D MMMM YYYY")}
        </time>
        <ExternalLinkIcon className="size-3" />
      </a>
      <CardTitle className="text-md xs:text-xl">{outcome.title}</CardTitle>
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
