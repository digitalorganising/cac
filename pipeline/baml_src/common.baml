template_string BargainingUnitThinkingPrompt() #"
    There may be a small number of cases where the number of workers in the bargaining unit is not available to you in the decision document.
    For example, there may be preliminary issues which preclude looking at it.
    In these cases where you do not know the number of workers, n_workers_in_decision is false, and n_workers is 0.
    
    There may also be cases where you do not feel that n_workers was verified: in this case, use the best number you can.

    Before you answer, outline the following step by step with reference to the document.
    Make sure to distinguish between claimed numbers and numbers verified by the case manager.
   
    - The number of workers in the bargaining unit (verified) [n_workers], if they were stated [n_workers_in_decision]
    - The number of union members in the bargaining unit (verified) [n_verified_union_members]
    - The first (based on what we know) number of union members claimed (unverified, usually just from the membership list supplied) [n_stated_union_members]

    Next, check whether you've obeyed these rules:
    - If n_workers_in_decision is true, then n_workers cannot be zero (and vice versa)
"#

class BargainingUnit {
  description string @description("The defined bargaining unit exactly as written but excluding any address")
  size_considered bool @alias("n_workers_in_decision")
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
