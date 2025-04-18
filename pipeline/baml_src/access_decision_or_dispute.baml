class AccessArrangementDecision {
  decision_type "a decision on access arrangements in advance of a ballot, or during it with a pause"
  favors Party? @description("Will the union or the employer be happier with the decision? Null if mixed")
  description string @description("1-sentence description of the decided access arrangement")
}

class UnfairPracticeDisputeDecision {
  decision_type "a decision on an unfair practice dispute during the access period"
  upheld bool @description("Is the claim of unfair practice upheld?")
  complainant Party @description("Which party submitted a complaint to the CAC?")
}

class AccessDecisionOrDispute {
    decision_date string
    details UnfairPracticeDisputeDecision | AccessArrangementDecision @alias("decision") @description("details of the decision")
}

function ExtractAccessDecisionOrDispute(decision_document: string) -> AccessDecisionOrDispute {
  client DefaultClient
  prompt #"
    Given the CAC document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}
  "#
}

test TestName {
  functions [ExtractAccessDecisionOrDispute]
  args {
    decision_document #"
      hello world
    "#
  }
}
