import { ExternalLinkIcon } from "@radix-ui/react-icons";
import dayjs from "dayjs";
import Link from "next/link";
import { Fragment } from "react";
import BallotResults from "@/components/outcome-card/BallotResults";
import { Timeline } from "@/components/timeline/timeline";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDuration } from "@/lib/duration";
import {
  addParamValue,
  appSearchParamsCache,
  appSearchParamsSerializer,
} from "@/lib/search-params";
import { Outcome, OutcomeState } from "@/lib/types";
import { cn } from "@/lib/utils";
import { getStateCategory } from "@/lib/utils";
import DebugView from "./DebugView";
import DecisionTimelineItem from "./DecisionTimelineItem";

type Props = {
  outcome: Outcome;
  className?: string;
  showDebugView?: boolean;
};

const classForState = (outcomeState: OutcomeState): string => {
  const category = getStateCategory(outcomeState);
  switch (category) {
    case "withdrawn":
      return "bg-slate-200";
    case "pending":
      return "bg-amber-200";
    case "successful":
      return "bg-green-300";
    case "unsuccessful":
      return "bg-red-300";
    default:
      return "bg-slate-200";
  }
};

const BargainingUnit = ({
  membership,
  size,
}: Required<Outcome>["bargainingUnit"]) => (
  <span
    className={cn(
      "rounded-md inline-block",
      size ? "bg-slate-200" : "bg-orange-200",
      membership ? "pl-2 xs:pl-2.5" : "px-2 xs:px-2.5 py-0.5 xs:py-1",
    )}
  >
    {size ? `${size} workers` : "Size not stated"}
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

const OutcomeDetails = ({ outcome, className }: Props) => {
  const params = appSearchParamsCache.all();
  return (
    <dl
      className={cn(
        "grid grid-cols-[minmax(160px,_1fr)_auto] lg:grid-cols-[160px_minmax(auto,_100%)] auto-rows-min items-baseline",
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
              href={appSearchParamsSerializer(
                addParamValue(params, "parties.unions", unionName),
              )}
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
          href={appSearchParamsSerializer(
            addParamValue(params, "parties.employer", outcome.parties.employer),
          )}
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

      {outcome.bargainingUnit?.locations &&
      outcome.bargainingUnit.locations.length === 1 ? (
        <>
          <dt>Location</dt>
          <dd>{outcome.bargainingUnit.locations[0]}</dd>
        </>
      ) : outcome.bargainingUnit?.locations &&
        outcome.bargainingUnit.locations.length > 1 ? (
        <>
          <dt>Locations</dt>
          <dd>
            <ul className="list-disc list-inside">
              {outcome.bargainingUnit.locations.map((location) => (
                <li key={location}>{location}</li>
              ))}
            </ul>
          </dd>
        </>
      ) : null}

      {outcome.bargainingUnit?.petitionSignatures ? (
        <>
          <dt>Supporting petition</dt>
          <dd>{outcome.bargainingUnit.petitionSignatures} signatures</dd>
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
};

const OutcomeCard = ({ outcome, showDebugView = false }: Props) => (
  <Card>
    <CardHeader className="space-y-0 space-x-3 flex flex-row items-center justify-between mb-2">
      <Link
        href={appSearchParamsSerializer({ reference: outcome.reference })}
        className="flex items-center gap-x-2 group"
      >
        <CardTitle className="text-md xs:text-xl group-hover:underline">
          {outcome.title}
        </CardTitle>
      </Link>
      <Link
        aria-label="View this outcome on gov.uk"
        href={outcome.cacUrl}
        target="_blank"
        className="shrink-0 self-start size-6 xs:size-auto p-0 xs:m-1 flex flex-row items-center justify-center text-nowrap xs:space-x-2 rounded-full border xs:px-2.5 xs:py-0.5 text-xs border-transparent bg-slate-200 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 hover:bg-slate-300"
      >
        <span className="hidden xs:inline">
          Last updated:&nbsp;
          <time className="hidden xs:inline" dateTime={outcome.lastUpdated}>
            {dayjs(outcome.lastUpdated).format("D MMMM YYYY")}
          </time>
        </span>
        <ExternalLinkIcon className="size-3" />
      </Link>
    </CardHeader>
    <CardContent className="flex flex-col p-3 md:p-5 md:pt-2.5 md:flex-row sm:space-x-4 w-full">
      <Timeline className="md:w-1/2">
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
    {showDebugView ? <DebugView outcome={outcome} /> : null}
  </Card>
);

export default OutcomeCard;
