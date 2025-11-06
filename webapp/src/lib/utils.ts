import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { SingleKeyObject } from "type-fest";
import { StateCategory } from "@/components/timeline/types";
import { OutcomeState } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function arr<T>(value: T | T[]): T[] {
  return Array.isArray(value) ? value : [value];
}

export function hasDeepProperty<V, O extends object>(
  prop: SingleKeyObject<V>,
  obj: O,
): boolean {
  const [searchKey, searchValue] = Object.entries(prop ?? {})[0];
  const searchObj = (obj: O): boolean => {
    if (typeof obj === "object" && Array.isArray(obj)) {
      return obj.some((item) => searchObj(item));
    }
    if (typeof obj === "object" && obj !== null) {
      return Object.entries(obj).some(([key, value]) => {
        if (typeof value === "object") {
          return searchObj(value);
        } else {
          return key === searchKey && value === searchValue;
        }
      });
    }
    return false;
  };
  return searchObj(obj);
}

export const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(value, max));
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
