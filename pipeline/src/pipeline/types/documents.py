from enum import StrEnum, auto


class DocumentType(StrEnum):
    para_35_decision = auto()
    acceptance_decision = auto()
    bargaining_unit_decision = auto()
    bargaining_decision = auto()
    form_of_ballot_decision = auto()
    whether_to_ballot_decision = auto()
    validity_decision = auto()
    case_closure = auto()
    recognition_decision = auto()
    application_received = auto()

    # These are a rather annoying case in that
    # it is impossible to consistently distinguish
    # the following 2 cases without reading the decision:
    #
    # - A decision in advance of the access period as to the access agreement
    # - A dispute during the access period regarding unfair practice
    access_decision_or_dispute = auto()

    # Only one of these ever, will index but
    # no point trying to extract data
    nullification_decision = auto()

    # Types with boilerplate document content
    method_agreed = auto()
    application_withdrawn = auto()

    # Types to ignore, shouldn't be there
    derecognition_decision = auto()
