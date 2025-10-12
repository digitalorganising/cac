class AcceptanceDecision {
  decision_date string
  success bool @description("Whether the application was successful")
  rejection_reasons RejectionReason[] @description("The specific reasons given by the panel in the document (empty if application was successful)")
  application_date string
  end_of_acceptance_period string? @description("The date for the end of the acceptance period after any extensions")
  bargaining_unit BargainingUnit
  bargaining_unit_agreed bool @description("Whether the employer agreed with the bargaining unit - must be a boolean!")
  petition_signatures int? @description("The number of entries on any union petition/survey/etc regardless of veracity and before any revisions or exclusions or contradicting statements (null if no petition)")

  @@assert(consistent_rejection_reasons, {{ this.success != this.rejection_reasons|length|bool }})
  @@assert(consistent_bu_size, {{ this.bargaining_unit.size_considered == this.bargaining_unit.size|bool }})
}

function ExtractAcceptanceDecision(decision_document: string) -> AcceptanceDecision {
  client ThinkingClient
  prompt #"
    Given the CAC acceptance decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ DateFormatPrompt() }}

    {{ ctx.output_format }}

    {{ BargainingUnitThinkingPrompt() }}
  "#
}
