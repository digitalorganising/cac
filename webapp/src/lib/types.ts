export type EventType =
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

export type OutcomeEvent = {
  type: {
    value: EventType;
    label: string;
  };
  date: string;
  description?: string;
  sourceDocumentUrl: string;
};

export type OutcomeState = {
  value:
    | "withdrawn"
    | "pending_application_decision"
    | "application_rejected"
    | "pending_recognition_decision"
    | "balloting"
    | "recognized"
    | "not_recognized"
    | "method_agreed"
    | "closed";
  label: string;
};

type OutcomeParties = {
  unions: string[];
  employer: string;
};

type OutcomeBargainingUnit = {
  size: number;
  membership?: number;
  description: string;
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
};

type QueryParam = string | string[] | undefined;

export type AppQueryParams = Record<
  | "query"
  | "page"
  | "sort"
  | "parties.unions"
  | "parties.employer"
  | "reference"
  | "state"
  | "bargainingUnit.size.from"
  | "bargainingUnit.size.to"
  | "events.type"
  | "events.date.from"
  | "events.date.to"
  | "debug",
  QueryParam
>;

export type SortKey =
  | "relevance"
  | "lastUpdated"
  | "applicationDate"
  | "concludedDate"
  | "bargainingUnitSize";
export type SortOrder = "asc" | "desc";

export type Filters = Pick<
  AppQueryParams,
  "parties.unions" | "parties.employer" | "reference" | "state" | "events.type"
>;
