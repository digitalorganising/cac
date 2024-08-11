class Panel {
  case_manager string
  panel_members string[]
}

class AcceptanceDecision {
  decision_date string @description("ISO8601 date")
  union_name string
  employer_name string
  employer_hostility int @description("A number between 0 and 100 reflecting the level of employer hostility and opposition to union recognition, where 1.0 is the most hostile")
  success bool @description("Whether the application was successful")
  rejection_reasons RejectionReason[] @description("If the application was not sucessful, why was it rejected? Empty if application was successful")
  application_date string @description("An ISO8601 date string for the date the application was received by the CAC")
  end_of_acceptance_period string? @description("The date for the end of the acceptance period after any extensions")
  panel Panel
  bargaining_unit BargainingUnit
  bargaining_unit_agreed bool @description("Whether the employer agreed with the bargaining unit")
}

function ExtractAcceptanceDecision(decision_document: string) -> AcceptanceDecision {
  client Claude
  prompt #"
    Given the CAC acceptance decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    1. Extract a list of the sentences related to bargaining unit size and membership numbers.
    2. Extract a list of the names of the panel members and the case manager. Now give a list of their names without any titles/honorifics/roles/postnominals. Use this list when constructing your response.

    {{ ctx.output_format }}
  "#
}
