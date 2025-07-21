class ValidityDecision {
    decision_date string
    valid bool
    rejection_reasons RejectionReason[] @description("What was the FINAL decision's reason for rejection? Empty if application was successful")
    new_bargaining_unit BargainingUnit

    @@assert(consistent_rejection_reasons, {{ this.valid != this.rejection_reasons|length|bool }})
}

function ExtractValidityDecision(decision_document: string) -> ValidityDecision {
  client DefaultClient
  prompt #"
    Given the CAC validity decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ DateFormatPrompt() }}

    {{ ctx.output_format }}

    {{ BargainingUnitThinkingPrompt() }}
  "#
}
