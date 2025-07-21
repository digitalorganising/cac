class BargainingUnitDecision {
    decision_date string
    appropriate_unit_differs bool @description("Does the decided unit differ AT ALL, including if amended, from that proposed in the initial application?")
    new_bargaining_unit_description string? @description("Null if appropriate unit does not differ from proposed. Otherwise, the defined bargaining unit exactly as written but excluding any address")
    lawyer_present bool @description("Whether any legal counsel, lawyers or solicitors were present at the hearing for either the union or the employer")
}

function ExtractBargainingUnitDecision(decision_document: string) -> BargainingUnitDecision {
  client DefaultClient
  prompt #"
    Given the CAC bargaining unit decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ DateFormatPrompt() }}

    {{ ctx.output_format }}
  "#
}
