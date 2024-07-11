class BallotResult {
    eligible_workers int
    spoiled_ballots int
    votes_in_favor int
    votes_against int
    start_ballot_period string @description("ISO8601 date string")
    end_ballot_period string @description("ISO8601 date string")
}

class RecognitionDecision {
  union_recognized bool
  ballot BallotResult? @description("Null if there was no ballot")
  good_relations_contested bool @description("Did the employer think that the ballot should be held in the interests of good industrial relations?")
}

function ExtractRecognitionDecision(decision_document: string) -> RecognitionDecision {
  client Claude
  prompt #"
    Given the CAC recognition decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}
  "#
}
