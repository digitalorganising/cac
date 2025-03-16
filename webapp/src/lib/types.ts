type EventType = {
  value: string;
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
