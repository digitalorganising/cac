from enum import StrEnum, auto


class DocumentType(StrEnum):
    acceptance_decision = auto()
    derecognition_decision = auto()
    access_decision = auto()
    bargaining_unit_decision = auto()
    bargaining_decision = auto()
    form_of_ballot_decision = auto()
    whether_to_ballot_decision = auto()
    validity_decision = auto()
    case_closure = auto()
    nullification_decision = auto()
    recognition_decision = auto()
    application_received = auto()


document_titles = {
    "Para 35 Decision": DocumentType.acceptance_decision,
    "Declaration Decision": DocumentType.derecognition_decision,
    "Unfair Practice Decision": DocumentType.access_decision,
    "Method Agreed": None,
    "Decision under s.264 of the Act": DocumentType.bargaining_unit_decision,
    "Acceptance Decision": DocumentType.acceptance_decision,
    "Application Withdrawn": None,
    "Paragraph 26 Decision": DocumentType.access_decision,
    "Method Decision": DocumentType.bargaining_decision,
    "Form of Ballot": DocumentType.form_of_ballot_decision,
    "Whether to Ballot": DocumentType.whether_to_ballot_decision,
    "Bargaining Unit Decision": DocumentType.bargaining_unit_decision,
    "Application Progress": DocumentType.application_received,
    "Access Arrangements for Ballot Decision": DocumentType.access_decision,
    "Validity Decision": DocumentType.validity_decision,
    "Whether to Ballot Decision": DocumentType.whether_to_ballot_decision,
    "Case Closure": DocumentType.case_closure,
    "Nullification Decision": DocumentType.nullification_decision,
    "Recognition Decision": DocumentType.recognition_decision,
    "Paragraph 35 Decision": DocumentType.acceptance_decision,
    "Application withdrawn": None,
    "Form of Ballot Decision": DocumentType.form_of_ballot_decision,
    "Whether to Ballot decision": DocumentType.whether_to_ballot_decision,
    "Access Decision": DocumentType.access_decision,
    "Ballot Decision": DocumentType.whether_to_ballot_decision,
}


def get_document_type(title):
    if title in document_titles:
        return document_titles[title]
    else:
        raise ValueError(f"Unexpected document title '{title}'")
