import { OutcomeBallot } from "@/lib/types";

export default function BallotResults({
  turnoutPercent,
  eligible,
  inFavor,
  against,
  spoiled,
}: OutcomeBallot) {
  return (
    <>
      <dt>Ballot results</dt>
      <dd>
        <ul>
          <li>
            {turnoutPercent.toFixed(1)}% turnout ({eligible} total workers)
          </li>
          <li>
            {inFavor.percentVotes.toFixed(1)}% in favour ({inFavor.n} votes,{" "}
            {inFavor.percentBU.toFixed(1)}% of those eligible)
          </li>
          <li>
            {against.percentVotes.toFixed(1)}% against ({against.n} votes)
          </li>
          {spoiled.n > 0 ? (
            <li>
              {spoiled.percentVotes.toFixed(1)}% spoiled ({spoiled.n} votes)
            </li>
          ) : null}
        </ul>
      </dd>
    </>
  );
}
