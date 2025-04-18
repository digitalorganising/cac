class AcceptanceDecision {
  decision_date string
  employer_hostility int @description("A number between 0 and 100 reflecting the level of employer hostility and opposition to union recognition, where 1.0 is the most hostile")
  success bool @description("Whether the application was successful")
  rejection_reasons RejectionReason[] @description("If the application was not successful, why was it rejected by the CAC? Empty if application was successful")
  application_date string @description("The date the application was received - not the date it was submitted, if these differ")
  end_of_acceptance_period string? @description("The date for the end of the acceptance period after any extensions")
  bargaining_unit BargainingUnit
  bargaining_unit_agreed bool @description("Whether the employer agreed with the bargaining unit")
}

function ExtractAcceptanceDecision(decision_document: string) -> AcceptanceDecision {
  client DefaultClient
  prompt #"
    Given the CAC acceptance decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}

    Before you answer, outline everything you know about the composition of the bargaining unit.
  "#
}
