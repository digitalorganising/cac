class Panel {
  case_handler string @description("The name of the case handler, without title or postnominals etc")
  panel_members string[] @description("The names of the panel members, without titles or postnominals etc")
}

class BargainingUnit {
  description string
  agreed bool @description("Whether the employer agreed with the proposed bargaining unit")
  size int
  membership int @description("The membership level after confirmation (if necessary)")
  delta int @description("The difference between the initially claimed and the confirmed membership")
}

class AdditionalSupportCheck {
  name string @alias("k") @description("The title of any circulated survey/petition or, if not applicable, a short description of the form of support check")
  turnout int
  percentage_in_favour int
}

class ApplicationDetails {
  union_name string
  employer_name string
  recognition bool @description("Whether this is an application for statutory union recognition")
  success bool @description("Whether the application was successful")
  application_date string @description("An ISO8601 date string for the date the application was made")
  end_of_acceptance_period string @description("The date for the end of the acceptance period after any extensions")
  panel Panel @description("The details of the CAC panel")
  bargaining_unit BargainingUnit
  additional_support_check AdditionalSupportCheck? @alias("s") @description("If a membership check was insufficient to determine support, the details of any petition/survey/etc that was used as support check.")
}

// Creating a function to extract the resume from a string.
function ExtractApplicationDetails(application: string) -> ApplicationDetails {
  client Claude
  prompt #"
    {{ _.role("system") }}
    You are a UK trade union head of legal, specialising in contentious union recognition cases with the CAC.
    Be extremely thorough and make sure you don't miss anything in the application, as the stakes are high for your members.

    {{ _.role("user") }}
    Parse the following CAC application outcome and return the details as specified below.

    <application_outcome>
    {{ application }}
    </application_outcome>

    {{ ctx.output_format }}
  "#
}