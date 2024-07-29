class ValidityDecision {
    decision_date string @description("ISO8601 format")
    valid bool
    rejection_reasons RejectionReason[] @description("If the new unit was not valid, why? Empty if application was successful")
    new_bargaining_unit BargainingUnit
}

function ExtractValidityDecision(decision_document: string) -> ValidityDecision {
  client Claude
  prompt #"
    Given the CAC validity decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}
  "#
}
