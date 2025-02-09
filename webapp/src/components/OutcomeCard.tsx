import dayjs from "dayjs";
import { ExternalLinkIcon } from "@radix-ui/react-icons";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Timeline, TimelineItem } from "@/components/timeline/timeline";

type Outcome = {
  outcome_title: string;
  outcome_url: string;
  last_updated: string;
  derived_query: {
    union_name: string;
    employer_name: string;
  };
  extracted_data: {
    [decision: string]:
      | undefined
      | {
          decision_date: string;
        };
  };
  documents: object[];
};

type Props = {
  outcome: Outcome;
};

const formatJSON = ({ documents, ...outcome }: Outcome): string =>
  JSON.stringify(outcome, null, 2);

const getTimeline = (outcome: Outcome) =>
  Object.entries(outcome.extracted_data ?? {})
    .map(([decisionType, decision]) => ({
      decisionType,
      date: decision?.decision_date ?? outcome.last_updated,
    }))
    .toSorted((a, b) => dayjs(a.date).diff(b.date));

const OutcomeCard = ({ outcome }: Props) => (
  <Card>
    <CardHeader className="space-y-0 flex flex-row items-end justify-between">
      <CardTitle className="text-xl">{outcome.outcome_title}</CardTitle>
      <div className="flex flex-row space-x-2">
        <a
          className="flex flex-row items-center justify-center space-x-2 rounded-full border px-2.5 py-0.5 text-xs border-transparent bg-slate-200 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 hover:bg-slate-300"
          href={outcome.outcome_url}
          target="_blank"
        >
          Last updated:&nbsp;
          <time dateTime={outcome.last_updated}>
            {dayjs(outcome.last_updated).format("D MMMM YYYY")}
          </time>
          <ExternalLinkIcon className="size-3" />
        </a>
      </div>
    </CardHeader>
    <CardContent>
      {/*<pre>{formatJSON(outcome)}</pre>*/}
      <Timeline className="ml-2">
        {getTimeline(outcome).map(({ date, decisionType }) => (
          <TimelineItem
            key={decisionType}
            date={date}
            title={decisionType}
            description="Lorem ipsum dolor sit amet"
            status="completed"
          />
        ))}
      </Timeline>
    </CardContent>
  </Card>
);

export default OutcomeCard;
