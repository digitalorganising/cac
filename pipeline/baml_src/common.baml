template_string BargainingUnitThinkingPrompt() #"
    You have a particular interest in the bargaining unit and what is said about it.
    Before you answer, outline the following step by step with reference to the document.
    Make sure to distinguish between claimed numbers and numbers verified by the case manager.
   
    - The number of workers in the bargaining unit (verified) [n_workers]
    - The number of union members in the bargaining unit (verified) [n_verified_union_members]
    - The first (based on what we know) number of union members claimed (unverified, usually just from the membership list supplied) [n_stated_union_members]
"#

class BargainingUnit {
  description string @description("The defined bargaining unit exactly as written but excluding any address")
  size int @alias("n_workers") 
  claimed_membership int? @alias("n_stated_union_members")
  membership int? @alias("n_verified_union_members")
}

enum Party {
    Union
    Employer
}

enum FormOfBallot {
    Postal
    Workplace
    Combination
}

enum RejectionReason {
    UnionHasNoCertificateOfIndependence
    EmployerHasFewerThan21Workers
    LessThan10PercentMembership
    NoMajoritySupportLikely @description("majority of employees in the bargaining unit NOT likely to favour recognition")
    PreviousApplicationExists
    AnotherUnionAlreadyRecognized
    SomeOtherReason @description("When the reason given by the CAC is not one of those above")
}
