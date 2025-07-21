class FormOfBallotDecision {
    decision_date string
    form_of_ballot FormOfBallot
    employer_preferred FormOfBallot
    union_preferred FormOfBallot
}

function ExtractFormOfBallotDecision(decision_document: string) -> FormOfBallotDecision {
  client DefaultClient
  prompt #"
    Given the CAC form-of-ballot decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}

    {{ DateFormatPrompt() }}

    Before you answer that a ballot preference is either Postal or Workplace,
    please show your working to be sure it is not a Combination:
  "#
}
