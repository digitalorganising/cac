import { CompanySubtype, OutcomeCompany } from "@/lib/types";

export const COMPANY_SUBTYPE_LABELS: Record<CompanySubtype, string> = {
  LocalAuthority: "Local authority",
  GovernmentDepartment: "Government department",
  ArmsLengthBody: "Arms-length body",
  University: "University",
  IndependentSchool: "Independent school",
  Charity: "Charity",
  Other: "Other",
  Unknown: "Unknown",
};

export const getSubtypeLabel = (subtype: CompanySubtype): string =>
  COMPANY_SUBTYPE_LABELS[subtype];

export const getEntityTypeLabel = (company: OutcomeCompany): string => {
  if (company.type === "identified") {
    return "Company";
  }
  return company.subtype ? getSubtypeLabel(company.subtype) : "Unknown";
};

export const getCompanyTypeFilterValue = (company: OutcomeCompany): string => {
  if (company.type === "identified") {
    return "identified";
  }
  return company.subtype ?? "Unknown";
};

export const getCompanyTypeLabel = (value: string): string =>
  value === "identified"
    ? "Company"
    : COMPANY_SUBTYPE_LABELS[value as CompanySubtype];

export const companiesHouseUrl = (companyNumber: string): string =>
  `https://find-and-update.company-information.service.gov.uk/company/${companyNumber}`;
