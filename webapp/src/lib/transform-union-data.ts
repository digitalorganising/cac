import unionSizesData from "@/data/union-sizes.json";
import { ApplicationsPerUnionData } from "./queries/dashboard";

// Sort data by total applications (descending) and truncate to top N
export function sortAndTruncateApplicationsPerUnion(
  data: ApplicationsPerUnionData,
  limit: number = 15,
): ApplicationsPerUnionData {
  // Calculate total applications for each union
  const withTotal = data.map((entry) => ({
    ...entry,
    total:
      entry.successful + entry.unsuccessful + entry.pending + entry.withdrawn,
  }));

  // Sort by total in descending order
  const sorted = withTotal.sort((a, b) => b.total - a.total);

  // Truncate to top N and remove the total field
  return sorted.slice(0, limit).map(({ total, ...entry }) => entry);
}

// Transform ApplicationsPerUnionData to show applications per 1000 members
// Consolidates unions by matching names/alternativeNames and normalizes by membership
export function transformApplicationsPerUnionToPer1000Members(
  data: ApplicationsPerUnionData,
): ApplicationsPerUnionData {
  // Create a map to find union membership by name (case-insensitive)
  const unionMembershipMap = new Map<string, number>();
  const unionNameMap = new Map<string, string>(); // Maps normalized name to display name

  for (const unionData of unionSizesData.data) {
    const normalizedName = unionData.name.toLowerCase();
    unionMembershipMap.set(normalizedName, unionData.membership);
    unionNameMap.set(normalizedName, unionData.name);

    // Also add alternative names
    for (const altName of unionData.alternativeNames) {
      const normalizedAltName = altName.toLowerCase();
      unionMembershipMap.set(normalizedAltName, unionData.membership);
      unionNameMap.set(normalizedAltName, unionData.name);
    }
  }

  // Map to consolidate unions: key is the canonical union name from union-sizes.json
  const consolidated = new Map<
    string,
    {
      successful: number;
      unsuccessful: number;
      pending: number;
      withdrawn: number;
    }
  >();

  // Process each union in the data
  for (const entry of data) {
    const normalizedUnionName = entry.union.toLowerCase();
    const membership = unionMembershipMap.get(normalizedUnionName);

    // Skip unions without membership data
    if (membership === undefined) {
      continue;
    }

    // Get the canonical name for this union
    const canonicalName = unionNameMap.get(normalizedUnionName) || entry.union;

    // Initialize or add to consolidated data
    const existing = consolidated.get(canonicalName);
    if (existing) {
      existing.successful += entry.successful;
      existing.unsuccessful += entry.unsuccessful;
      existing.pending += entry.pending;
      existing.withdrawn += entry.withdrawn;
    } else {
      consolidated.set(canonicalName, {
        successful: entry.successful,
        unsuccessful: entry.unsuccessful,
        pending: entry.pending,
        withdrawn: entry.withdrawn,
      });
    }
  }

  // Convert to array and normalize by membership (per 1000 members)
  const result: ApplicationsPerUnionData = [];
  for (const [unionName, counts] of consolidated.entries()) {
    const membership = unionMembershipMap.get(unionName.toLowerCase());
    if (membership === undefined || membership === 0) {
      continue; // Skip if no membership data
    }

    result.push({
      union: unionName,
      successful: (counts.successful / membership) * 1000,
      unsuccessful: (counts.unsuccessful / membership) * 1000,
      pending: (counts.pending / membership) * 1000,
      withdrawn: (counts.withdrawn / membership) * 1000,
    });
  }

  // Sort by total applications (descending) and truncate to top 15
  return sortAndTruncateApplicationsPerUnion(result, 15);
}
