class BargainingUnit {
  description string @description("The defined bargaining unit exactly as written but excluding any address")
  size int? @description("Size determined after all checks, but before any new hires added.")
  claimed_membership int @alias("claimed_union_membership") @description("Number of union members in the bargaining unit stated by the union, before verification.")
  membership int? @description("Union members in the bargaining unit as determined by the case manager, might differ from the above")
  supporters int? @description("Number of workers likely to favour union recognition")
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
