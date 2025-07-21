class BargainingDecision {
    decision_date string
    cac_involvement_date string
}

function ExtractBargainingDecision(decision_document: string) -> BargainingDecision {
  client DefaultClient
  prompt #"
    Given the CAC bargaining decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    Ignore information related to the history of the case and find the date at which any party requested the CAC to assist in determining the method of bargaining.
    {{ DateFormatPrompt() }}

    {{ ctx.output_format }}
  "#
}
