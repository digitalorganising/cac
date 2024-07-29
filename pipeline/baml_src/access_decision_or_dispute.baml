class AccessArrangementDecision {
  favors Party? @description("Will the union or the employer be happier with the decision? Null if mixed")
  description string @description("1-sentence description of the decided access arrangement")
}

class UnfairPracticeDisputeDecision {
  upheld bool @description("Is the claim of unfair practice upheld?")
  complainant Party @description("Which party submitted a complaint to the CAC?")
}

class AccessDecisionOrDispute {
    decision_date string @description("ISO8601 date")
    details UnfairPracticeDisputeDecision | AccessArrangementDecision @alias("decision") 
}

function ExtractAccessDecisionOrDispute(decision_document: string) -> AccessDecisionOrDispute {
  client Claude
  prompt #"
    Given the CAC document below,

    <doc>
    {{ decision_document }}
    </doc>

    1. What is the preferred outcome of (a) the union and (b) the employer?
    2. What is the outcome that the CAC decided upon?
    3. Is this more similar to one of the preferred outcomes, or is the decision a mix that doesn't clearly favor one party?

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
