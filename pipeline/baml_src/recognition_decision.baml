class BallotResult {
    eligible_workers int
    spoiled_ballots int
    votes_in_favor int
    votes_against int
    start_ballot_period string @description("ISO8601 date string")
    end_ballot_period string @description("ISO8601 date string")
}

class RecognitionDecision {
    decision_date string @description("ISO8601 date")
    union_recognized bool
    form_of_ballot FormOfBallot? @description("Null if there was no ballot")
    ballot BallotResult? @description("Null if there was no ballot")
    good_relations_contested bool @description("Was the ballot held in the interests of good industrial relations regardless of membership numbers?")
}

function ExtractRecognitionDecision(decision_document: string) -> RecognitionDecision {
  client DefaultClient
  prompt #"
    Given the CAC recognition decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}
  "#
}
