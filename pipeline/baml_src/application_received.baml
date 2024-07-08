class ApplicationReceived {
    date_received string @description("ISO8601 date string")
}

function ExtractApplicationReceived(statement: string) -> ApplicationReceived {
  client Claude
  prompt #"
    Given this statement, extract the data as specified.

    {{ statement }}

    {{ ctx.output_format }}
  "#
}
