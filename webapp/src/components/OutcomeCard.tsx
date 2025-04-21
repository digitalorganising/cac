import dayjs from "dayjs";
import Link from "next/link";
import { Fragment } from "react";
import { ExternalLinkIcon } from "@radix-ui/react-icons";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Timeline } from "@/components/timeline/timeline";
import DecisionTimelineItem from "@/components/DecisionTimelineItem";
import { Outcome } from "@/lib/types";
import { formatDuration } from "@/lib/duration";
import BallotResults from "@/components/BallotResults";
import { cn } from "@/lib/utils";

type Props = {
  outcome: Outcome;
  className?: string;
};

const OutcomeDetails = ({ outcome, className }: Props) => (
  <dl
    className={cn(
      "p-2 max-sm:pt-0 md:p-4 grid auto-cols auto-rows-min xs:gap-x-2 md:gap-x-4 xs:gap-y-1 md:gap-y-2 [&>dt]:font-bold xs:[&>dd]:col-start-2 max-sm:[&>dt]:mt-2",
      className,
    )}
  >
    <dt>Status</dt>
    <dd>{outcome.state.label}</dd>

    <dt>Duration</dt>
    <dd>
      {formatDuration(outcome.keyDates)}
      {outcome.keyDates.outcomeConcluded ? null : (
        <>
          {" "}
          <i className="italic text-muted-foreground">(ongoing)</i>
        </>
      )}
    </dd>

    <dt>Union</dt>
    <dd>
      {outcome.parties.unions.map((unionName, i) => (
        <Fragment key={unionName}>
          <Link
            href={`/?parties.unions=${encodeURIComponent(unionName)}`}
            className="font-medium text-primary underline underline-offset-4"
          >
            {unionName}
          </Link>
          {i !== outcome.parties.unions.length - 1 ? ", " : null}
        </Fragment>
      ))}
    </dd>

    <dt>Employer</dt>
    <dd>
      <Link
        href={`/?parties.employer=${encodeURIComponent(outcome.parties.employer)}`}
        className="font-medium text-primary underline underline-offset-4"
      >
        {outcome.parties.employer}
      </Link>
    </dd>

    {outcome.bargainingUnit?.size ? (
      <>
        <dt>Bargaining unit size</dt>
        <dd>{outcome.bargainingUnit.size}</dd>
      </>
    ) : null}

    {outcome.bargainingUnit?.membership ? (
      <>
        <dt>Union membership</dt>
        <dd>{outcome.bargainingUnit.membership}</dd>
      </>
    ) : null}

    {outcome.ballot ? <BallotResults {...outcome.ballot} /> : null}
  </dl>
);

const OutcomeCard = ({ outcome }: Props) => (
  <Card>
    <CardHeader className="space-y-0 xs:space-x-2 block xs:flex flex-row-reverse items-center justify-between">
      <a
        href={outcome.cacUrl}
        target="_blank"
        className="size-6 xs:size-auto p-0 float-right m-1 flex flex-row items-center justify-center text-nowrap xs:space-x-2 rounded-full border xs:px-2.5 xs:py-0.5 text-xs border-transparent bg-slate-200 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 hover:bg-slate-300"
      >
        <span className="hidden xs:inline">
          Last updated:&nbsp;
          <time className="hidden xs:inline" dateTime={outcome.lastUpdated}>
            {dayjs(outcome.lastUpdated).format("D MMMM YYYY")}
          </time>
        </span>
        <ExternalLinkIcon className="size-3" />
      </a>
      <CardTitle className="text-md xs:text-xl">{outcome.title}</CardTitle>
    </CardHeader>
    <CardContent className="flex flex-col md:flex-row md:justify-between sm:gap-4">
      <Timeline className="ml-2 md:w-1/2">
        {outcome.events.map((e) => (
          <DecisionTimelineItem key={e.type.value} event={e} />
        ))}
      </Timeline>
      <OutcomeDetails outcome={outcome} className="md:w-1/2" />
    </CardContent>
  </Card>
);

export default OutcomeCard;
