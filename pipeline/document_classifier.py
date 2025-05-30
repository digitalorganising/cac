from enum import StrEnum, auto


class DocumentType(StrEnum):
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


document_titles = {
    "Para 35 Decision": DocumentType.acceptance_decision,
    "Declaration Decision": DocumentType.derecognition_decision,
    "Unfair Practice Decision": DocumentType.access_decision_or_dispute,
    "Method Agreed": DocumentType.method_agreed,
    "Decision under s.264 of the Act": DocumentType.bargaining_unit_decision,
    "Acceptance Decision": DocumentType.acceptance_decision,
    "Application Withdrawn": DocumentType.application_withdrawn,
    "Paragraph 26 Decision": DocumentType.access_decision_or_dispute,
    "Method Decision": DocumentType.bargaining_decision,
    "Form of Ballot": DocumentType.form_of_ballot_decision,
    "Whether to Ballot": DocumentType.whether_to_ballot_decision,
    "Bargaining Unit Decision": DocumentType.bargaining_unit_decision,
    "Application Progress": DocumentType.application_received,
    "Access Arrangements for Ballot Decision": DocumentType.access_decision_or_dispute,
    "Validity Decision": DocumentType.validity_decision,
    "Whether to Ballot Decision": DocumentType.whether_to_ballot_decision,
    "Case Closure": DocumentType.case_closure,
    "Nullification Decision": DocumentType.nullification_decision,
    "Recognition Decision": DocumentType.recognition_decision,
    "Paragraph 35 Decision": DocumentType.acceptance_decision,
    "Application withdrawn": DocumentType.application_withdrawn,
    "Form of Ballot Decision": DocumentType.form_of_ballot_decision,
    "Whether to Ballot decision": DocumentType.whether_to_ballot_decision,
    "Access Decision": DocumentType.access_decision_or_dispute,
    "Ballot Decision": DocumentType.whether_to_ballot_decision,
}


def get_document_type(title):
    if title in document_titles:
        return document_titles[title]
    else:
        raise ValueError(f"Unexpected document title '{title}'")


# These documents contain text which is the same in all cases - we don't need to analyze
def should_get_content(document_type):
    match document_type:
        case DocumentType.application_withdrawn:
            return False
        case _:
            return True


def should_skip(document_type):
    match document_type:
        # There is only one of these and it shouldn't be there
        case DocumentType.derecognition_decision:
            return True
        case _:
            return False
