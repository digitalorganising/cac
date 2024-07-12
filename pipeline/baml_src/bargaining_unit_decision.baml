class BargainingUnitDecision {
    decision_date string @description("ISO8601 format")
    appropriate_unit_differs bool @description("Does the decided unit differ AT ALL, including if amended, from that proposed in the initial application?")
    new_bargaining_unit_description string? @description("Null if appropriate unit does not differ from proposed.") 
}

function ExtractBargainingUnitDecision(decision_document: string) -> BargainingUnitDecision {
  client Claude
  prompt #"
    Given the CAC bargaining unit decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    Extract all the sentences related to the bargaining unit finally decided upon by the CAC (the appropriate unit).
    Was the unit initially proposed by the union amended at all? 

    {{ ctx.output_format }}
  "#
}
