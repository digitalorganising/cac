class Panel {
  case_manager string
  panel_members string[]
}

class BargainingUnit {
  description string @description("Not including the address if given")
  agreed bool @description("Whether the employer agreed with the bargaining unit")
  size int
  claimed_membership int @description("Union members stated by the union to be among the total workers in the bargaining unit")
  membership int @description("Union members in the bargaining unit as determined by the case manager")
}

class Petition {
  source string @description("Either 'employer' or 'union'")
  in_favor int @alias("n") @description("The number of signatories if the petition is in favour of recognition. Otherwise, the number of signatories who specificall indicated support for recognition.")
  in_bargaining_unit int @description("Those of the above who are in the bargaining unit")
  members int
  non_members int
}

class AcceptanceDecision {
  union_name string
  employer_name string
  success bool @description("Whether the application was successful")
  application_date string @description("An ISO8601 date string for the date the application was received by the CAC")
  end_of_acceptance_period string @description("The date for the end of the acceptance period after any extensions")
  panel Panel @description("Just the names, not their roles or titles")
  bargaining_unit BargainingUnit
  petitions Petition[] @description("The details of any petitions/surveys/etc that were used as support check. This is empty if there were no petitions or surveys used.")
}

function ExtractAcceptanceDecision(decision_document: string) -> AcceptanceDecision {
  client Claude
  prompt #"
    {{ _.role("system") }}
    You are a UK trade union head of legal, and are an expert in statutory union recognition.
    You are very thorough and work step-by-step to make sure your numbers are correct.
    You are paid £1000 for each document that you analyze without errors.

    {{ _.role("user") }}
    Read the following CAC application acceptance decision and return the details as specified below.

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}
  "#
}
