class Para35Decision {
  decision_date string
  application_date string
  application_can_proceed bool @description("Is the conclusion to proceed, or to reject the application?")
}

function ExtractPara35Decision(decision_document: string) -> Para35Decision {
  client DefaultClient
  prompt #"
    Given the CAC para 35 decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ DateFormatPrompt() }}

    {{ ctx.output_format }}
  "#
}