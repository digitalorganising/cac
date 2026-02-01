import type { Context } from "hono";

export default function (context: Context) {
  return context.json({
    totalResults: 1,
    outcomes: [
      {
        reference: "TUR1/1441(2024)",
        cacUrl:
          "https://www.gov.uk/government/publications/cac-outcome-gmb-the-montefiore-hospital",
        lastUpdated: "2025-06-25T11:15:36+01:00",
      },
    ],
  });
}
