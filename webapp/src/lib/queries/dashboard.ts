import "server-only";
import { getClient, outcomesIndex } from "./common";

export type CategoryCounts = {
  successful: number;
  unsuccessful: number;
  pending: number;
  withdrawn: number;
};

export type ApplicationsPerUnionData = {
  union: string;
  successful: number;
  unsuccessful: number;
  pending: number;
  withdrawn: number;
}[];

export type BargainingUnitSizeData = {
  sizeRange: string;
  successful: number;
  unsuccessful: number;
  pending: number;
  withdrawn: number;
}[];

export type TimeToAcceptanceData = {
  timeRange: string;
  count: number;
}[];

export type TimeToConclusionData = {
  timeRange: string;
  successful: number;
  unsuccessful: number;
}[];

// TODO: Replace with real OpenSearch aggregation query
export async function getCategoryCounts(): Promise<CategoryCounts> {
  // Placeholder: Return mock data for now
  // In the future, this will query OpenSearch with aggregations on the state field
  return {
    successful: 1247,
    unsuccessful: 892,
    pending: 156,
    withdrawn: 203,
  };
}

// TODO: Replace with real OpenSearch aggregation query
export async function getApplicationsPerUnion(): Promise<ApplicationsPerUnionData> {
  // Placeholder: Return mock data for now
  // In the future, this will query OpenSearch with terms aggregation on parties.unions
  // and nested aggregations for state distribution
  return [
    { union: "UNITE", successful: 45, unsuccessful: 32, pending: 5, withdrawn: 8 },
    { union: "GMB", successful: 38, unsuccessful: 28, pending: 4, withdrawn: 6 },
    { union: "UNISON", successful: 52, unsuccessful: 41, pending: 7, withdrawn: 12 },
    { union: "CWU", successful: 29, unsuccessful: 19, pending: 3, withdrawn: 4 },
    { union: "PCS", successful: 34, unsuccessful: 25, pending: 6, withdrawn: 7 },
    { union: "RMT", successful: 21, unsuccessful: 15, pending: 2, withdrawn: 3 },
    { union: "UCU", successful: 18, unsuccessful: 12, pending: 1, withdrawn: 2 },
  ];
}

// TODO: Replace with real OpenSearch aggregation query
export async function getBargainingUnitSizes(): Promise<BargainingUnitSizeData> {
  // Placeholder: Return mock data for now
  // In the future, this will query OpenSearch with range aggregation on bargainingUnit.size
  // and nested aggregations for state distribution
  return [
    { sizeRange: "0-50", successful: 12, unsuccessful: 8, pending: 2, withdrawn: 3 },
    { sizeRange: "51-100", successful: 28, unsuccessful: 19, pending: 4, withdrawn: 5 },
    { sizeRange: "101-200", successful: 45, unsuccessful: 32, pending: 6, withdrawn: 8 },
    { sizeRange: "201-500", successful: 62, unsuccessful: 44, pending: 8, withdrawn: 12 },
    { sizeRange: "501-1000", successful: 48, unsuccessful: 35, pending: 5, withdrawn: 7 },
    { sizeRange: "1001-2000", successful: 35, unsuccessful: 25, pending: 4, withdrawn: 6 },
    { sizeRange: "2001-5000", successful: 22, unsuccessful: 16, pending: 2, withdrawn: 3 },
    { sizeRange: "5000+", successful: 15, unsuccessful: 11, pending: 1, withdrawn: 2 },
  ];
}

// TODO: Replace with real OpenSearch aggregation query
export async function getTimeToAcceptance(): Promise<TimeToAcceptanceData> {
  // Placeholder: Return mock data for now
  // In the future, this will query OpenSearch and calculate time difference between
  // applicationReceived and application_accepted event dates, then aggregate into week ranges
  return [
    { timeRange: "0-4", count: 45 },
    { timeRange: "5-8", count: 68 },
    { timeRange: "9-12", count: 52 },
    { timeRange: "13-16", count: 38 },
    { timeRange: "17-20", count: 29 },
    { timeRange: "21-24", count: 22 },
    { timeRange: "25-28", count: 15 },
    { timeRange: "29-32", count: 12 },
    { timeRange: "33-36", count: 8 },
    { timeRange: "37+", count: 6 },
  ];
}

// TODO: Replace with real OpenSearch aggregation query
export async function getTimeToConclusion(): Promise<TimeToConclusionData> {
  // Placeholder: Return mock data for now
  // In the future, this will query OpenSearch and calculate time difference between
  // applicationReceived and outcomeConcluded dates, then aggregate into week ranges
  // split by successful (recognized) vs unsuccessful (not_recognized/application_rejected)
  return [
    { timeRange: "0-4", successful: 12, unsuccessful: 8 },
    { timeRange: "5-8", successful: 28, unsuccessful: 19 },
    { timeRange: "9-12", successful: 35, unsuccessful: 24 },
    { timeRange: "13-16", successful: 42, unsuccessful: 29 },
    { timeRange: "17-20", successful: 38, unsuccessful: 26 },
    { timeRange: "21-24", successful: 32, unsuccessful: 22 },
    { timeRange: "25-28", successful: 25, unsuccessful: 17 },
    { timeRange: "29-32", successful: 18, unsuccessful: 12 },
    { timeRange: "33-36", successful: 12, unsuccessful: 8 },
    { timeRange: "37+", successful: 8, unsuccessful: 5 },
  ];
}

