class Panel {
  case_manager string
  panel_members string[]
}

class BargainingUnit {
  description string @description("Not including the address if given")
  agreed bool @description("Whether the employer agreed with the bargaining unit")
  size int @description("Size determined after all checks.")
  claimed_membership int @description("Union members in the bargaining unit initially claimed by the union. Be careful to count only members, not all workers.")
  membership int @description("Union members in the bargaining unit as determined by the case manager")
  supporters int @description("Workers in the bargaining unit likely to favour union recognition as entitled to conduct collective bargaining")
}

class AcceptanceDecision {
  union_name string
  employer_name string
  employer_hostility int @description("A number between 0 and 100 reflecting the level of employer hostility and opposition to union recognition, where 1.0 is the most hostile")
  success bool @description("Whether the application was successful")
  application_date string @description("An ISO8601 date string for the date the application was received by the CAC")
  end_of_acceptance_period string @description("The date for the end of the acceptance period after any extensions")
  panel Panel
  bargaining_unit BargainingUnit
}

function ExtractAcceptanceDecision(decision_document: string) -> AcceptanceDecision {
  client Claude
  prompt #"
    Given the CAC acceptance decision document below, 

    <doc>
    {{ decision_document }}
    </doc>

    1. Extract a list of the sentences related to bargaining unit size and membership numbers.
    3. Extract a list of the names of the panel members and the case manager. Now give a list of their names without any titles/honorifics/roles/postnominals. Use this list when constructing your response.
    4. Given the above, extract all of the details as specified. 

    {{ ctx.output_format }}
  "#
}
