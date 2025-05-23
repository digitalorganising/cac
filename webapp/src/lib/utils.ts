import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function addQueryParam(
  base: Record<string, string | string[] | undefined>,
  key: string,
  value: string | string[],
) {
  if (Array.isArray(base[key]) && Array.isArray(value)) {
    return { ...base, [key]: [...new Set([...base[key], ...value])] };
  }

  if (Array.isArray(base[key]) && typeof value === "string") {
    return { ...base, [key]: [...new Set([...base[key], value])] };
  }

  if (typeof base[key] === "string" && Array.isArray(value)) {
    return { ...base, [key]: [...new Set([base[key], ...value])] };
  }

  if (
    typeof base[key] === "string" &&
    typeof value === "string" &&
    base[key] !== value
  ) {
    return { ...base, [key]: [base[key], value] };
  }

  return { ...base, [key]: value };
}

export function deleteQueryParam(
  base: Record<string, string | string[] | undefined>,
  key: string,
  value: string | string[],
) {
  if (Array.isArray(base[key]) && Array.isArray(value)) {
    return { ...base, [key]: base[key].filter((v) => !value.includes(v)) };
  }

  if (Array.isArray(base[key]) && typeof value === "string") {
    return { ...base, [key]: base[key].filter((v) => v !== value) };
  }

  if (
    typeof base[key] === "string" &&
    Array.isArray(value) &&
    value.includes(base[key])
  ) {
    return { ...base, [key]: undefined };
  }

  if (
    typeof base[key] === "string" &&
    typeof value === "string" &&
    base[key] === value
  ) {
    return { ...base, [key]: undefined };
  }

  return base;
}
