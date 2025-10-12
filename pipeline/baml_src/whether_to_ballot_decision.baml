enum QualifyingCondition {
    GoodIndustrialRelations @description("If a ballot should be held in the interests of good industrial relations")
    EvidenceMembersOpposed @description("If there is evidence that members of the union are opposed to it conducting collective bargaining")
    MembershipEvidenceDoubts @description("ONLY if present as per 22(4), NOT if the membership level itself is in doubt")
}

class WhetherToBallotDecision {
    decision_date string
    decision_to_ballot bool
    majority_membership bool
    qualifying_conditions QualifyingCondition[]

    @@assert(consistent_qualifying_conditions, {{ this.qualifying_conditions|length|bool == this.majority_membership|bool }})
}

function ExtractWhetherToBallotDecision(decision_document: string) -> WhetherToBallotDecision {
  client ThinkingClient
  prompt #"
    Given the CAC whether-to-ballot decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}

    {{ DateFormatPrompt() }}

    Before you answer, show your reasoning for these points, then answer as above.

    1. Was the panel satisfied that the majority of workers in the bargaining unit were members of the union?
    2. If there will be a ballot AND the answer to 1 is YES: extract a list of the qualifying conditions that WERE met.
    3. If majority_membership is false then qualifying_conditions MUST be an empty list.
  "#
}