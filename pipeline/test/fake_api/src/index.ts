import { serve } from "@hono/node-server";
import { Hono } from "hono";
import outcomes from "./outcomes.js";
import { chatCompletions } from "./llm.js";
import { searchCompanies, getCompanyProfile } from "./companies_house.js";

const app = new Hono();

app.get("/cac/api/outcomes", outcomes);
app.post("/llm/chat/completions", chatCompletions);
app.get("/ch/search/companies", searchCompanies);
app.get("/ch/company/:company_number", getCompanyProfile);

serve(
  {
    fetch: app.fetch,
    port: 3001,
  },
  (info) => {
    console.log(`Server is running on http://localhost:${info.port}`);
  }
);
