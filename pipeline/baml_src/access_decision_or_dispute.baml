class AccessArrangementDecision {
  decision_type "access_arrangement"
  favors Party? @description("Will the union or the employer be happier with the decision? Null if mixed")
  description string @description("1-sentence description of the decided access arrangement including location, date/time, etc")
}

class UnfairPracticeDisputeDecision {
  decision_type "unfair_practice_dispute"
  upheld bool @description("Is the claim of unfair practice upheld?")
  complainant Party @description("Which party submitted a complaint to the CAC?")
}

class AccessDecisionOrDispute {
    decision_date string
    details UnfairPracticeDisputeDecision | AccessArrangementDecision @alias("decision")
}

function ExtractAccessDecisionOrDispute(decision_document: string) -> AccessDecisionOrDispute {
  client DefaultClient
  prompt #"
    Given the CAC document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ DateFormatPrompt() }}

    {{ ctx.output_format }}

    Choose the decision_type as follows and based on the structure of the respective objects,
    giving your reasoning before answering:
    - access_arrangement: the parties cannot agree on access arrangements for the ballot and this decision determines access
    - unfair_practice_dispute: there is some other dispute about unfair practices taking place during the access period,
      or a dispute on already agreed access arrangements

  "#
}
