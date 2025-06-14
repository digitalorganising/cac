import { BallotStats, OutcomeBallot } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";

const VoteBar = ({
  result,
  label,
  colorClassName,
}: {
  result: BallotStats;
  label: string;
  colorClassName: string;
}) => {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div
          className={cn("h-full", colorClassName)}
          style={{
            width: `${result.percentBU}%`,
          }}
        />
      </TooltipTrigger>
      <TooltipContent>
        <p>
          {label} -{" "}
          <strong className="text-semibold">
            {result.percentBU.toFixed(1)}%
          </strong>{" "}
          ({result.n})
        </p>
      </TooltipContent>
    </Tooltip>
  );
};

const VoteListItem = ({
  colorClassName,
  children,
}: {
  colorClassName: string;
  children: React.ReactNode;
}) => {
  return (
    <li className="flex items-center gap-2">
      <span
        className={cn(
          "inline-block self-stretch min-h-7 w-1 xs:w-1.5 rounded-full",
          colorClassName,
        )}
      />
      <span className="flex-1 leading-tight">{children}</span>
    </li>
  );
};

const Strong = ({ children }: { children: React.ReactNode }) => (
  <strong className="font-semibold">{children}</strong>
);

const ChartLabel = ({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLSpanElement>) => (
  <span
    className={cn(
      "absolute text-nowrap inline-block -translate-x-1/2 text-xs text-slate-800 ",
      className,
    )}
    {...props}
  >
    {children}
  </span>
);

const Arrow = ({
  direction,
  className,
  ...props
}: { direction: "up" | "down" } & React.HTMLAttributes<HTMLSpanElement>) => (
  <span
    className={cn(
      "absolute h-0 w-0 border-transparent border-l-6 border-r-6 -translate-x-1/2",
      direction === "up"
        ? "border-b-slate-800 border-b-6"
        : "border-t-slate-800 border-t-6",
      className,
    )}
    {...props}
  />
);

export default function BallotResults({
  turnoutPercent,
  eligible,
  inFavor,
  against,
  spoiled,
}: OutcomeBallot) {
  return (
    <div>
      <div className="w-full relative py-6 my-2 xs:my-1">
        <div className="w-full h-8 lg:h-10 bg-slate-200 flex rounded-md overflow-hidden relative">
          <TooltipProvider delayDuration={0}>
            <VoteBar
              colorClassName="bg-green-400"
              result={inFavor}
              label="In favour"
            />
            <VoteBar
              colorClassName="bg-red-400"
              result={against}
              label="Against"
            />
            <VoteBar
              colorClassName="bg-gray-400"
              result={spoiled}
              label="Spoiled"
            />
            <VoteBar
              colorClassName="bg-slate-200"
              result={{
                percentVotes: 0,
                n: eligible - inFavor.n - against.n - spoiled.n,
                percentBU: 100 - turnoutPercent,
              }}
              label="Non-voting"
            />
          </TooltipProvider>
        </div>
        <Arrow direction="down" className="left-[40%] top-4.5" />
        <Arrow
          direction="up"
          className="bottom-4.5"
          style={{ left: `${turnoutPercent / 2}%` }}
        />
        <ChartLabel className="top-0 left-[40%]">
          Required turnout in favour (40%)
        </ChartLabel>
        <ChartLabel
          className="bottom-0"
          style={{ left: `${turnoutPercent / 2}%` }}
        >
          Vote majority
        </ChartLabel>
      </div>
      <ul className="border-slate-200 border rounded-md mt-2 xs:mt-4 p-2 xs:p-3 text-sm xs:text-base space-y-3">
        <VoteListItem colorClassName="bg-slate-200">
          Of <Strong>{eligible}</Strong> eligible workers,{" "}
          <Strong>{turnoutPercent.toFixed(1)}%</Strong> (
          {inFavor.n + against.n + spoiled.n}) voted.
        </VoteListItem>
        <VoteListItem colorClassName="bg-green-400">
          <Strong>{inFavor.percentBU.toFixed(1)}%</Strong> ({inFavor.n}) voted
          in favour of recognition (
          <Strong>{inFavor.percentVotes.toFixed(1)}%</Strong> of all votes)
          {inFavor.percentVotes > 50 ? (
            <>
              , <Strong>{inFavor.percentBU >= 40 ? "more" : "less"}</Strong>{" "}
              than the required 40%.
            </>
          ) : null}
        </VoteListItem>
        <VoteListItem colorClassName="bg-red-400">
          <Strong>{against.percentBU.toFixed(1)}%</Strong> ({against.n}) voted
          against recognition (
          <Strong>{against.percentVotes.toFixed(1)}%</Strong> of all votes)
        </VoteListItem>
        <VoteListItem colorClassName="bg-gray-400">
          <Strong>{spoiled.percentVotes.toFixed(1)}%</Strong> ({spoiled.n}) of
          ballots were spoiled.
        </VoteListItem>
      </ul>
    </div>
  );
}
