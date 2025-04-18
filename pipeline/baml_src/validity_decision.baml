class ValidityDecision {
    decision_date string
    valid bool
    rejection_reasons RejectionReason[] @description("What was the FINAL decision's reason for rejection? Empty if application was successful")
    new_bargaining_unit BargainingUnit
}

function ExtractValidityDecision(decision_document: string) -> ValidityDecision {
  client DefaultClient
  prompt #"
    Given the CAC validity decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}

    Before you answer, outline all the information you know about the composition of the new bargaining unit.
  "#
}
