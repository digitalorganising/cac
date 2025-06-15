class AcceptanceDecision {
  decision_date string
  success bool @description("Whether the application was successful")
  rejection_reasons RejectionReason[] @description("If the application was not successful, why was it rejected by the CAC? Empty if application was successful")
  application_date string @description("The date the application was received - not the date it was submitted, if these differ")
  end_of_acceptance_period string? @description("The date for the end of the acceptance period after any extensions")
  bargaining_unit BargainingUnit
  bargaining_unit_agreed bool @description("Whether the employer agreed with the bargaining unit")
  petition_signatures int? @description("The number of names/signatures on the petition/survey, before any verification or cross-checking or other removal/redaction, if the union used one (null if no petition)")

  @@assert(consistent_rejection_reasons, {{ this.success != this.rejection_reasons|length|bool }})
  @@assert(consistent_bu_size, {{ this.bargaining_unit.size_considered == this.bargaining_unit.size|bool }})
}

function ExtractAcceptanceDecision(decision_document: string) -> AcceptanceDecision {
  client DefaultClient
  prompt #"
    Given the CAC acceptance decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}

    {{ BargainingUnitThinkingPrompt() }}
  "#
}
