import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { SingleKeyObject } from "type-fest";

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
