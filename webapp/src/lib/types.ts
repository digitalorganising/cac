export type EventTypeValue =
  | "application_received"
  | "application_withdrawn"
  | "application_accepted"
  | "application_rejected"
  | "bargaining_unit_decided"
  | "ballot_requirement_decided"
  | "ballot_form_decided"
  | "ballot_held"
  | "access_disputed"
  | "union_recognized"
  | "union_not_recognized"
  | "method_decision"
  | "method_agreed"
  | "case_closed";

type EventType = {
  value: EventTypeValue;
  label: string;
};

export type OutcomeEvent = {
  type: EventType;
  date: string;
  description?: string;
};

type OutcomeStatus = {
  value: string;
  label: string;
};

export type Outcome = {
  title: string;
  reference: string;
  cacUrl: string;
  lastUpdated: string;
  status: OutcomeStatus;
  parties: {
    union: string;
    employer: string;
  };
  events: OutcomeEvent[];
};
