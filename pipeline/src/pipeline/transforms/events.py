from transitions import MachineError
from collections import OrderedDict
from dateutil.parser import parse as date_parse

from ..types.documents import DocumentType
from .events_machine import EventsBuilder, InvalidEventError
from .events_from_decision import events_from_decision, Decision
from .known_bad_data import fix_extracted_data


def doc_ordering(fallback_date):
    def _doc_order(kv_tuple):
        doc_type, doc = kv_tuple
        # It's pragmatic to have our own tiebreakers
        tiebreaker = {
            DocumentType.application_received: 1,
            DocumentType.application_withdrawn: 2,
            DocumentType.recognition_decision: 3,
            DocumentType.method_agreed: 4,
        }.get(doc_type, 0)
        return (
            (
                date_parse(doc.decision_date)
                if doc and doc.decision_date
                else fallback_date
            ),
            tiebreaker,
        )

    return _doc_order


def events_from_outcome(outcome):
    fallback_date = date_parse(outcome.last_updated.isoformat()[:10])
    fixed_outcome = fix_extracted_data(outcome)
    data = fixed_outcome.extracted_data
    sorted_docs = OrderedDict(sorted(data.items(), key=doc_ordering(fallback_date)))
    document_urls = outcome.document_urls

    # Escape hatch below: this only happens where there is a previous application receipt
    # but now the application has been withdrawn.
    if (
        "application_received" in document_urls
        and "application_withdrawn" in document_urls
        and document_urls["application_received"] is None
    ):
        document_urls["application_received"] = document_urls["application_withdrawn"]

    events = EventsBuilder()
    for doc_type, doc in sorted_docs.items():
        try:
            decision = Decision[doc_type](
                doc, document_urls.get(doc_type), fallback_date
            )
            for event in events_from_decision(decision):
                events.add_event(event)

        except (MachineError, ValueError, TypeError) as e:
            raise InvalidEventError(
                {
                    "root_cause": e,
                    "outcome_reference": fixed_outcome.id,
                    "current_events": events.dump_events(),
                }
            )
    return events
