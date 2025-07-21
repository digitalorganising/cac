class BallotResult {
    eligible_workers int
    spoiled_ballots int
    votes_in_favor int
    votes_against int
    start_ballot_period string @description("ballot start date - date of ballot paper dispatch if postal")
    end_ballot_period string @description("ballot end date")
}

class RecognitionDecision {
    decision_date string
    union_recognized bool
    form_of_ballot FormOfBallot? @description("Null if there was no ballot")
    ballot BallotResult? @alias("ballot_result") 
    good_relations_contested bool @description("Was the ballot held in the interests of good industrial relations regardless of membership numbers?")

    @@assert(ballot_existence, {{ this.ballot|bool == this.form_of_ballot|bool }})
}

function ExtractRecognitionDecision(decision_document: string) -> RecognitionDecision {
  client DefaultClient
  prompt #"
    Given the CAC recognition decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}

    {{ DateFormatPrompt() }}

    Before you answer, if there was a ballot held, outline the following step by step:
    - The number of eligible workers / ballot papers sent out
    - The number of spoiled ballots, the number of votes in favor, and the number of votes against
    Any number which isn't present is a zero.
  "#
}
