class ValidityDecision {
    decision_date string
    valid bool
    rejection_reasons RejectionReason[] @description("What was the FINAL decision's reason for rejection? Empty if application was successful")
    new_bargaining_unit BargainingUnit
    petition_signatures int? @description("The number of names/signatures on the petition/survey, before any verification or cross-checking or other removal/redaction, if the union used one (null if no petition)")

    @@assert(consistent_rejection_reasons, {{ this.valid != this.rejection_reasons|length|bool }})
}

function ExtractValidityDecision(decision_document: string) -> ValidityDecision {
  client DefaultClient
  prompt #"
    Given the CAC validity decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}

    {{ BargainingUnitThinkingPrompt() }}
  "#
}
