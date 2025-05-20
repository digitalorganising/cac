import { BallotStats, OutcomeBallot } from "@/lib/types";
import {
  TooltipProvider,
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "./ui/tooltip";
import { cn } from "@/lib/utils";

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

export default function BallotResults({
  turnoutPercent,
  eligible,
  inFavor,
  against,
  spoiled,
}: OutcomeBallot) {
  return (
    <div>
      <div className="w-full relative py-5.5">
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
        <div className="absolute h-9.5 lg:h-11.5 border-l border-slate-600 left-[40%] top-4" />
        <div
          className="absolute h-9.5 lg:h-11.5 border-l border-slate-600 bottom-4"
          style={{ left: `${turnoutPercent / 2}%` }}
        />

        <span className="absolute bg-white text-nowrap top-0 inline-block left-[40%] -translate-x-1/2 text-xs text-slate-600 border-b border-slate-600">
          Required turnout in favour (40%)
        </span>
        <span
          className="absolute bg-white text-nowrap bottom-0 inline-block text-xs text-slate-600 -translate-x-1/2 border-t border-slate-600"
          style={{ left: `${turnoutPercent / 2}%` }}
        >
          Majority
        </span>
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
