from ..types.documents import DocumentType


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
