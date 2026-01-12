export const eventTypes = [
  "application_received",
  "application_p35_valid",
  "application_p35_invalid",
  "application_withdrawn",
  "application_accepted",
  "application_rejected",
  "bargaining_unit_appropriate",
  "bargaining_unit_inappropriate",
  "ballot_requirement_decided",
  "ballot_not_required",
  "ballot_form_postal",
  "ballot_form_workplace",
  "ballot_form_combination",
  "ballot_held",
  "unfair_practice_upheld",
  "unfair_practice_not_upheld",
  "access_arrangement",
  "union_recognized",
  "union_not_recognized",
  "method_decision",
  "method_agreed",
  "case_closed",
] as const;

export type EventType = (typeof eventTypes)[number];

export type OutcomeEvent = {
  type: {
    value: EventType;
    label: string;
  };
  date: string;
  description?: string;
  sourceDocumentUrl?: string;
};

export const outcomeStates = [
  "withdrawn",
  "pending_application_decision",
  "application_rejected",
  "pending_recognition_decision",
  "balloting",
  "recognized",
  "not_recognized",
  "method_agreed",
  "closed",
] as const;

export type OutcomeState = {
  value: (typeof outcomeStates)[number];
  label: string;
};

type OutcomeParties = {
  unions: string[];
  employer: string;
};

type OutcomeBargainingUnit = {
  size?: number;
  membership?: number;
  description?: string;
  petitionSignatures?: number;
  locations?: string[];
};

export type BallotStats = {
  n: number;
  percentVotes: number;
  percentBU: number;
};

export type OutcomeBallot = {
  turnoutPercent: number;
  eligible: number;
  inFavor: BallotStats;
  against: BallotStats;
  spoiled: BallotStats;
};

export type OutcomeKeyDates = {
  applicationReceived: string;
  outcomeConcluded?: string;
  methodAgreed?: string;
};

export type OutcomeDuration = {
  value: number;
  relation: "eq" | "gte";
};

export type Outcome = {
  title: string;
  reference: string;
  cacUrl: string;
  lastUpdated: string;
  state: OutcomeState;
  parties: OutcomeParties;
  bargainingUnit?: OutcomeBargainingUnit;
  ballot?: OutcomeBallot;
  events: OutcomeEvent[];
  keyDates: OutcomeKeyDates;
  durations: {
    overall: OutcomeDuration;
    acceptance: OutcomeDuration;
  };
};
