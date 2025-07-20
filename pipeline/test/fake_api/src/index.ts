import { serve } from "@hono/node-server";
import { Hono } from "hono";

const app = new Hono();

app.get("/api/outcomes", (c) => {
  return c.json({
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
});

serve(
  {
    fetch: app.fetch,
    port: 3001,
  },
  (info) => {
    console.log(`Server is running on http://localhost:${info.port}`);
  }
);
