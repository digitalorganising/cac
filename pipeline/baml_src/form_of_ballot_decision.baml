enum FormOfBallot {
    Postal
    Workplace
    Combination
}

class FormOfBallotDecision {
    form_of_ballot FormOfBallot
    employer_preferred FormOfBallot
    union_preferred FormOfBallot
}

function ExtractFormOfBallotDecision(decision_document: string) -> FormOfBallotDecision {
  client Claude
  prompt #"
    Given the CAC form-of-ballot decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}
  "#
}