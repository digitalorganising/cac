class BargainingUnit {
  description string @description("Not including the address if given, but otherwise quote exactly as written including all details, qualifiers and exclusions")
  size int? @description("Size determined after all checks.")
  claimed_membership int? @alias("claimed_union_membership") @description("Union members in the bargaining unit initially claimed by the union. Be careful to count only members, not all workers.")
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
    NoMajoritySupportLikely @description("majority of employees in the bargaining unit NOT likely to favour recognition")
    PreviousApplicationExists
    AnotherUnionAlreadyRecognized
    SomeOtherReason @description("When the reason given by the CAC is not one of those above")
}
