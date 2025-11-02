import { OutcomeState } from "../types";

export type StateCategory =
  | "successful"
  | "unsuccessful"
  | "pending"
  | "withdrawn";

export function getStateCategory(
  state: OutcomeState | string,
): StateCategory | null {
  const stateValue = typeof state === "string" ? state : state.value;

  switch (stateValue) {
    case "recognized":
    case "method_agreed":
      return "successful";
    case "application_rejected":
    case "not_recognized":
      return "unsuccessful";
    case "pending_application_decision":
    case "pending_recognition_decision":
    case "balloting":
      return "pending";
    case "withdrawn":
    case "closed":
      return "withdrawn";
    default:
      return null;
  }
}
