import dayjs from "dayjs";
import Link from "next/link";
import { Fragment } from "react";
import { ExternalLinkIcon } from "@radix-ui/react-icons";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Timeline } from "@/components/timeline/timeline";
import DecisionTimelineItem from "@/components/DecisionTimelineItem";
import { Outcome, OutcomeState } from "@/lib/types";
import { formatDuration } from "@/lib/duration";
import BallotResults from "@/components/BallotResults";
import { cn } from "@/lib/utils";

type Props = {
  outcome: Outcome;
  className?: string;
};

const classForState = (outcomeState: OutcomeState): string => {
  switch (outcomeState.value) {
    case "withdrawn":
    case "closed":
      return "bg-slate-200";
    case "pending_application_decision":
    case "pending_recognition_decision":
    case "balloting":
      return "bg-amber-200";
    case "recognized":
    case "method_agreed":
      return "bg-green-300";
    case "not_recognized":
    case "application_rejected":
      return "bg-red-300";
  }
};

const BargainingUnit = ({
  membership,
  size,
}: Required<Outcome>["bargainingUnit"]) => (
  <span
    className={cn(
      "rounded-md inline-block bg-slate-200",
      membership ? "pl-2 xs:pl-2.5" : "px-2 xs:px-2.5 py-0.5 xs:py-1",
    )}
  >
    {size} workers
    {membership ? (
      <span
        className={cn(
          "inline-block pr-2 xs:pr-2.5 pl-1 xs:pl-1.5 ml-3 xs:ml-3.5 py-0.5 xs:py-1 bg-slate-300 rounded-r-md relative z-20",
          "after:content-['_'] after:-skew-x-12 xs:after:-skew-x-16 after:origin-top-right after:absolute after:top-0 after:left-0",
          "after:bg-slate-300 after:w-[16px] after:h-full after:-z-10",
        )}
      >
        {membership} union members
      </span>
    ) : null}
  </span>
);

const OutcomeDetails = ({ outcome, className }: Props) => (
  <dl
    className={cn(
      "m-2 max-md:mt-0 lg:m-4 grid grid-cols-[minmax(160px,_1fr)_auto] lg:grid-cols-[160px_minmax(auto,_100%)] auto-rows-min items-baseline",
      "xs:gap-x-2 md:gap-x-4 xs:gap-y-0.5 lg:gap-y-3",
      "[&>dt]:font-medium [&>dt]:col-start-1 [&>dd]:col-start-1 lg:[&>dd]:col-start-2 max-lg:[&>dt]:mt-2.5",
      className,
    )}
  >
    <dt>Status</dt>
    <dd className="whitespace-nowrap">
      <span
        className={cn(
          "rounded-md px-2.5 py-0.5 inline-block overflow-hidden align-top text-ellipsis max-w-full",
          classForState(outcome.state),
        )}
      >
        {outcome.state.label}
      </span>
    </dd>

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
            className="text-primary underline underline-offset-4 hover:font-medium"
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
        className="text-primary underline underline-offset-4 hover:font-medium"
      >
        {outcome.parties.employer}
      </Link>
    </dd>

    {outcome.bargainingUnit ? (
      <>
        <dt>Bargaining unit</dt>
        <dd>
          <BargainingUnit {...outcome.bargainingUnit} />
        </dd>
      </>
    ) : null}

    {outcome.ballot ? (
      <>
        <dt>Ballot results:</dt>
        <dd className="col-start-1! col-span-2">
          <BallotResults {...outcome.ballot} />
        </dd>
      </>
    ) : null}
  </dl>
);

const OutcomeCard = ({ outcome }: Props) => (
  <Card>
    <CardHeader className="space-y-0 xs:space-x-2 block xs:flex flex-row-reverse items-center justify-between mb-2">
      <a
        href={outcome.cacUrl}
        target="_blank"
        className="size-6 xs:size-auto p-0 float-right xs:m-1 flex flex-row items-center justify-center text-nowrap xs:space-x-2 rounded-full border xs:px-2.5 xs:py-0.5 text-xs border-transparent bg-slate-200 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 hover:bg-slate-300"
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
    <CardContent className="flex flex-col md:flex-row sm:space-x-4 w-full">
      <Timeline className="ml-2 md:w-1/2">
        {outcome.events.map((e) => (
          <DecisionTimelineItem
            key={e.type.value}
            event={e}
            timelineId={outcome.reference}
          />
        ))}
      </Timeline>
      <OutcomeDetails outcome={outcome} className="md:w-1/2" />
    </CardContent>
  </Card>
);

export default OutcomeCard;
