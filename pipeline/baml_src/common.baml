class BargainingUnit {
  description string @description("Not including the address if given")
  size int? @description("Size determined after all checks.")
  claimed_membership int? @description("Union members in the bargaining unit initially claimed by the union. Be careful to count only members, not all workers.")
  membership int? @description("Union members in the bargaining unit as determined by the case manager")
  supporters int? @description("Maximum number of workers likely to favour union recognition who MUST be in the bargaining unit")
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
    NoMajoritySupportLikely
    PreviousApplicationExists
    AnotherUnionAlreadyRecognized
    SomeOtherReason @description("For exceptional cases where none of the usual reasons fit")
}