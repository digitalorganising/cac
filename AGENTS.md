# AGENTS.md

Guide for AI agents working on this repository. **Primary focus: how data flows between services and where inter-service contracts live**, so schema changes are made consistently end-to-end.

## What this project does

UK CAC (Central Arbitration Committee) trade union recognition outcomes: scraped from GOV.UK, enriched with LLM extraction, merged into per-case outcomes, indexed in OpenSearch, and served by a Next.js webapp.

## Repository layout

| Area | Path | Role |
|------|------|------|
| Pipeline (Lambdas, transforms, types) | `pipeline/` | Scrape → augment → index |
| BAML schemas & LLM prompts | `pipeline/baml_src/` | Structured extraction contracts |
| OpenSearch index mappings (JSON) | `pipeline/index_mappings/` | Strict mappings for indexed docs |
| Infrastructure | `terraform/` | Lambdas, Step Functions, schedules |
| Webapp | `webapp/` | Search UI; reads `outcomes-indexed` |

## End-to-end data flow

```
GOV.UK (scrapy)
    → Scraper Lambda → outcomes-raw[-suffix]          (DecisionRaw)
    → Augmenter Lambda → outcomes-augmented[-suffix]  (DecisionAugmented)
    → [acceptance only] Company Disambiguator → disambiguated-companies
    → Indexer Lambda → outcomes-indexed[-suffix]      (display / filter / facet)
    → Next.js webapp (OUTCOMES_INDEX env)
```

The scraper also **reads** the webapp API (`API_BASE/outcomes`) to decide which outcomes to re-check (unterminated cases, last-updated watermark). That creates a **feedback loop**: indexed `display` shape must stay compatible with what `UpdatedOutcomesSpider` expects (`reference`, `cacUrl`, `lastUpdated`, `state`).

Orchestration: AWS Step Functions (`terraform/state-machine/pipeline.asl.json`). Scheduled runs pass `{"indexSuffix": "1012"}` so production uses suffixed indices (`outcomes-raw-1012`, etc.).

## Webapp and the document store

The webapp is a **Next.js** app (`webapp/`) hosted on **Vercel**. It does not call the pipeline Lambdas. All search and browse behaviour goes **directly to OpenSearch** (Bonsai-hosted cluster) — the “document server” in production.

### Connection and configuration

Server-side code uses `@opensearch-project/opensearch` (`webapp/src/lib/queries/client.ts`):

| Env var | Purpose |
|---------|---------|
| `OPENSEARCH_ENDPOINT` | Cluster URL (same Bonsai host as the pipeline) |
| `OPENSEARCH_CREDENTIALS_SECRET` | AWS Secrets Manager ARN; JSON `{username, password}` |
| `OUTCOMES_INDEX` | Index to query (e.g. `outcomes-indexed` or `outcomes-indexed-1012`) |
| `AWS_REGION` / `AWS_ROLE_ARN` | Vercel OIDC → IAM role for Secrets Manager access |

Terraform sets these on the Vercel project (`terraform/vercel.tf`). Queries run only in **server components** and route handlers (`import "server-only"`), with results cached via Next.js `"use cache: remote"` + `cacheLife("hours")`.

The webapp reads **one index only**: `OUTCOMES_INDEX`. It never touches `outcomes-raw`, `outcomes-augmented`, or `disambiguated-companies`. Those are pipeline-internal; the indexer’s job is to denormalise everything the UI needs into `outcomes-indexed`.

### What each stored document contains

Each outcome document in `outcomes-indexed` is a multi-view record built by `transform_for_index()`. The webapp uses different slices for different jobs:

| Slice | Indexed? | Webapp use |
|-------|----------|------------|
| `display` | No (`enabled: false`) | **Primary read model** — returned to React as `Outcome` |
| `filter.*` | Yes (flat dotted keys) | Query filters, sorting, dashboard metrics |
| `facet.*` | Yes (JSON-string values) | Sidebar facet counts and histograms |
| `full_text` | Yes | Free-text search (`match` on user `query` param) |
| `documents.*` | Copied into `full_text` only | Not returned to the UI; powers full-text search over decision bodies |

### The `display` object (`Outcome`)

TypeScript contract: `webapp/src/lib/types.ts` `Outcome`. This must match `transform_for_index()`’s `display` block. Fields the UI renders:

- **Identity:** `title`, `reference`, `cacUrl`, `lastUpdated`
- **Status:** `state` (`{value, label}`), derived from the event state machine
- **Parties:** `parties.unions`, `parties.employer` (parsed from title)
- **Company:** optional `company` (`identified` with `number` + `sics`, or `unidentified` with `subtype`)
- **Bargaining unit:** optional `bargainingUnit` (size, membership, description, locations, petitionSignatures)
- **Ballot:** optional `ballot` (turnout, eligible, inFavor/against/spoiled breakdowns)
- **Timeline:** `events[]` — `{type: {value, label}, date, description?, sourceDocumentUrl?}`
- **Derived dates:** `keyDates` (applicationReceived, outcomeConcluded, methodAgreed)
- **Derived durations:** `durations.overall` / `durations.acceptance` (seconds + `eq` | `gte` relation)

`OutcomeCard` (`webapp/src/components/outcome-card/`) is the main consumer. With `?debug=1`, it shows the raw `display` JSON.

### How the webapp queries OpenSearch

All query builders live in `webapp/src/lib/queries/`.

**Search results** — `getOutcomes()` (`outcomes.ts`):

- `_source: ["display"]` — only the UI payload is fetched
- `bool.should`: `match` on `full_text` if `query` param set, else `match_all`
- `bool.filter`: from `getFilters()` in `common.ts` — each URL search param maps to a `filter.<field>` path (e.g. `state` → `filter.state`, `parties.unions` → `filter.parties.unions`)
- Sort keys map to `filter.*` fields (`filter.lastUpdated`, `filter.keyDates.applicationReceived`, etc.)

**Facets** — `getFacets()` (`facets.ts`):

- `size: 0` search with aggregations on `facet.parties.unions`, `facet.state`, `facet.events.type`, `facet.bargainingUnit.size`
- Facet bucket keys are JSON strings (from pipeline `flatten_facets()`); `getFacetProps()` parses them back to `{value, label?}`

**Dashboard** — `dashboard.ts`:

- Mostly aggregation-only requests on `facet.*` and `filter.*`
- One exception: bargaining-unit vs turnout scatter plot fetches partial `_source` (`display.bargainingUnit.size`, `display.ballot.turnoutPercent`, etc.) from up to 1000 ballot-held outcomes

**URL ↔ filter mapping** — `webapp/src/lib/search-params.ts` defines every accepted query param; `util.ts` `appSearchParamsToOutcomesOptions()` bridges params to `GetOutcomesOptions`. Adding a new user-facing filter requires a search param, a `getFilters()` clause, a `filter.*` field in the indexed mapping, and a value in `transform_for_index()`.

### Public API (`/api/outcomes`)

`webapp/src/app/api/outcomes/route.ts` exposes the same `getOutcomes()` logic as JSON:

```json
{
  "totalResults": 1234,
  "nextPage": "https://…/api/outcomes?page=2&…",
  "previousPage": null,
  "outcomes": [ /* Outcome[] from display */ ]
}
```

This API is consumed by:

1. **The search UI** (could call it client-side; currently uses server-side `getOutcomes` directly on pages)
2. **The scraper Lambda** (`API_BASE` → `https://<vercel-domain>/api/outcomes`) for incremental re-scraping

Fields the scraper depends on from each `outcome` in that response: `reference`, `cacUrl`, `lastUpdated`, and `state.value`. Breaking or renaming these breaks incremental scraping.

### Pages

| Route | Data source |
|-------|-------------|
| `/` (search) | `getOutcomes` + `getFacets` via parallel routes (`@faceting`) |
| `/dashboard` | `dashboard.ts` aggregation helpers |
| `/docs/*` | Static MDX; no OpenSearch |

## OpenSearch indices

All pipeline indices use `"dynamic": "strict"`. **Adding a field without updating the mapping will fail writes.**

| Index | Written by | Pydantic / schema source | Mapping source |
|-------|-----------|--------------------------|----------------|
| `outcomes-raw[-suffix]` | Scraper | `DecisionRaw` | `decision_raw_mapping` in `pipeline/src/pipeline/types/decisions.py` |
| `outcomes-augmented[-suffix]` | Augmenter | `DecisionAugmented` (discriminated union) | `decision_augmented_mapping` in same file |
| `disambiguated-companies` | Company disambiguator | `StoredResult` | `pipeline/index_mappings/disambiguated_companies.json` |
| `application-withdrawals` | Manual / test data only | Same as augmented | Same as `decision_augmented_mapping` |
| `outcomes-indexed[-suffix]` | Indexer | Built by `transform_for_index()` | `pipeline/index_mappings/outcomes_indexed.json` |

**Index suffix propagation:** `lambdas/__init__.py` `destination_index()` copies the suffix from `outcomes-*` source indices onto destination namespaces (`outcomes-augmented-1012`, `outcomes-indexed-1012`, etc.).

**Document IDs:**
- Per-decision: `{reference}:{document_type}` (e.g. `TUR1/0123/24:acceptance_decision`)
- Per-outcome (indexed): `reference` string (e.g. `TUR1/0123/24`)
- Disambiguated company: deterministic hash of request (`company_disambiguator/model.py` `request_to_doc_id`, keyed by `hash_version`)

## Step Functions: Lambda payloads and handoffs

### Scraper → Map

**Input:** `ScraperEvent` (`pipeline/src/lambdas/scraper.py`)

```json
{
  "indexSuffix": "1012",
  "limitItems": null,
  "forceLastUpdated": null,
  "redrive": { "complete": false, "augment": true, "ids": ["..."] }
}
```

**Output:** array of document refs — one per scraped decision:

```json
{ "_id": "TUR1/0123/24:acceptance_decision", "_index": "outcomes-raw-1012" }
```

Redrive mode may add `"passthrough": true` to skip re-augmentation (updates destination with empty doc, then runs `result_transform` on existing augmented doc).

### Map item → Augmenter

**Input:** `{"ref": <DocumentRef>}`

**Output:**

```json
{
  "ref": { "_id": "...", "_index": "outcomes-augmented-1012", "passthrough": false },
  "name": "...",
  "unions": ["..."],
  "application_date": "...",
  "bargaining_unit": "...",
  "locations": ["..."]
}
```

Extra top-level fields (`name`, `unions`, etc.) are only present for `acceptance_decision` documents — produced by `augmenter.transform_for_next_step`. The Step Function routes to Company Disambiguator when `_id` contains `acceptance_decision`.

### Augmenter → Company Disambiguator (acceptance only)

**Input:** fields from augmenter output (not the full `ref`):

```json
{
  "name": "Employer Ltd",
  "unions": ["Unite"],
  "application_date": "2024-01-15",
  "bargaining_unit": "...",
  "locations": ["..."],
  "force": false
}
```

Model: `DisambiguateCompanyLambdaEvent` (`company_disambiguator/model.py`).

**Output:** `DocumentRef` to `disambiguated-companies` index (the augmenter's `ref` is preserved separately in the state machine).

### Augmenter / Disambiguator → Indexer

**Input:** `{"ref": <DocumentRef>}` pointing at an augmented decision index.

Indexer merges **all decisions sharing the same outcome `reference`** from `outcomes-augmented[-suffix]` plus `application-withdrawals`, attaches company from `disambiguated-companies`, validates as `Outcome`, then writes to `outcomes-indexed[-suffix]`.

## Schema layers (update all relevant layers)

Contracts are duplicated across several representations. When changing a field, trace it through every layer it touches.

### 1. BAML (`pipeline/baml_src/*.baml`)

Source of truth for **LLM-extracted decision fields**. Defines classes like `AcceptanceDecision`, `RecognitionDecision`, enums (`FormOfBallot`, `RejectionReason`), shared `BargainingUnit`.

After editing BAML, regenerate the Python client (project uses `baml-py`):

```bash
cd pipeline && uv run baml-cli generate
```

Generated types land in `baml_client/types` (imported as `baml_client.types` in Python).

### 2. Python Pydantic models

| Model | File | Purpose |
|-------|------|---------|
| `DocumentType` | `pipeline/src/pipeline/types/documents.py` | Enum of decision kinds; keys in `Outcome.documents` / `extracted_data` |
| `DecisionRaw` | `pipeline/src/pipeline/types/decisions.py` | Scraped document before LLM |
| `DecisionAugmented*` | same | Per-type augmented docs; `extracted_data` typed from BAML |
| `Outcome` | `pipeline/src/pipeline/types/outcome.py` | Merged per-case view before indexing |
| `DisambiguateCompanyRequest` / `DisambiguatedCompany` | `company_disambiguator/model.py` | Company resolution |
| `Event` / `EventType` / `OutcomeState` | `pipeline/src/pipeline/transforms/model.py` | Event timeline & state machine |

`DecisionAugmented` is a **discriminated union on `document_type`**. New document types need: enum value, BAML extractor, augmented subclass, mapping fragment, `augmentation.get_extracted_data` case, `events_from_decision` handlers, and usually updates to `document_classifier.py` title map.

### 3. OpenSearch mappings

**Inline Python dicts** (raw & augmented): `decision_raw_mapping`, `decision_augmented_mapping`, and per-type `*_mapping` dicts in `decisions.py`. Augmented `extracted_data` merges all per-type property dicts into one object (fields from different types coexist in the mapping).

**JSON files** (indexed & disambiguated): `pipeline/index_mappings/`. The indexed mapping defines:
- `documents.*` — raw text per decision type (`full_text` for search)
- `display` — `enabled: false`; full UI payload (camelCase)
- `filter.*` — flat fields for queries/sorts (dot-separated keys, camelCase leaf names)
- `facet.*` — JSON-stringified facet values for aggregations

`transform_for_index()` in `pipeline/src/pipeline/transforms/__init__.py` is the **single builder** for indexed documents. It defines the contract between pipeline and webapp.

### 4. TypeScript (`webapp/src/lib/types.ts`)

`Outcome`, `OutcomeEvent`, `EventType`, `OutcomeState`, etc. must mirror `display` from `transform_for_index()`.

**Naming:** Pipeline internals use `snake_case`; indexed `display` / `filter` / API JSON use `camelCase`. Company fields: pipeline `DisambiguatedCompany` uses `company_name`, `company_number`, `industrial_classifications`; indexed `display.company` uses `name`, `number`, `sics`.

### 5. Webapp queries (`webapp/src/lib/queries/`)

See **Webapp and the document store** above for the full picture. In short:

- `common.ts` — filters target `filter.<field>` paths; must match `outcomes_indexed.json` `filter` properties
- `outcomes.ts` — `_source: ["display"]`; returns `hit._source.display` as `Outcome`
- `facets.ts` / `dashboard.ts` — aggregations on `facet.*` and `filter.*` fields

Changing a filterable or facetable field requires updates to **mapping**, **`transform_for_index` `filter`/`facet`**, and **query code**.

## Event & state machine contract

Decisions → events: `events_from_decision.py` (plum dispatch per `DocumentType`).

Events → state: `events_machine.py` transitions on `EventType` / `OutcomeState`.

`EventType` values in Python (`transforms/model.py`) must match `eventTypes` in `webapp/src/lib/types.ts` (string values, not labels).

Invalid event sequences raise `InvalidEventError`; indexer skips the outcome (`transform_if_possible` returns `None`).

## Document type reference

`DocumentType` (`documents.py`) drives scraping classification, augmentation routing, merge keys, and indexed `documents` map keys.

Notable cases:
- `derecognition_decision` — scraped but skipped; augmenter passes through raw
- `access_decision_or_dispute` — multiple GOV.UK titles map here
- `method_agreed` / `application_withdrawn` — boilerplate content; date extraction only
- `nullification_decision` — indexed, no extraction

Classifier title → type map: `pipeline/src/pipeline/transforms/document_classifier.py`.

## Company disambiguation contract

Request fields (from acceptance decision + parsed outcome title):

| Field | Source |
|-------|--------|
| `name` | Employer from `get_parties(outcome_title)` |
| `unions` | Unions from same |
| `application_date` | `extracted_data.decision_date` on acceptance |
| `bargaining_unit` | `extracted_data.bargaining_unit.description` |
| `locations` | `extracted_data.bargaining_unit.locations` |

Indexer looks up company by `request_to_doc_id()` — **must match** the disambiguator's stored `id`. Bump `hash_version` in `model.py` to invalidate all cached disambiguations when lookup logic changes.

## Checklist: changing a schema field

Use this when adding, renaming, or retyping data that crosses service boundaries.

1. **Identify the field's stage** — raw scrape, LLM extraction, merge (`Outcome`), index transform (`display`/`filter`/`facet`), or webapp-only.
2. **BAML** — if extracted by LLM, edit `.baml`, run `uv run baml-cli generate` (from `pipeline/`), update evals in `pipeline/test/evals/llm_extractors/`.
3. **Pydantic** — update `DecisionAugmented*` subclass and/or `Outcome`; update `decision_augmented_mapping` (or `decision_raw_mapping`).
4. **Extraction routing** — `augmentation.py` `get_extracted_data` match arms.
5. **Events** — if the field affects timeline/state, update `events_from_decision.py` and possibly `events_machine.py`.
6. **Index transform** — `transform_for_index()` and helpers (`get_bargaining_unit`, `get_ballot_result`, etc.).
7. **OpenSearch mapping** — `outcomes_indexed.json` (and JSON mapping files if disambiguation-related).
8. **TypeScript** — `webapp/src/lib/types.ts` and any components assuming the shape.
9. **Queries** — `common.ts` filters, `facets.ts`, `dashboard.ts` if searchable/filterable/facet-able.
10. **Step Functions** — only if lambda I/O shape changes (rare; augmenter → disambiguator is the main handoff).
11. **Tests** — unit/integration: `pipeline/test/unit_integration/`; e2e lambdas: `pipeline/test/e2e/`; LLM evals for BAML changes.
12. **Re-index** — strict mappings and merged outcomes mean production data may need a pipeline re-run or redrive after schema changes.

## Strict mapping gotchas

- `ensure_index_mapping()` creates or **put_mapping** updates indices; it cannot remove fields.
- Indexed `display` is not indexed (`enabled: false`) but is the webapp's read model — shape matters more than mapping there.
- `filter` and `facet` field paths use dots as literal key names (e.g. `filter.parties.unions`), not nested objects.
- `facet` values are JSON strings via `flatten_facets()` for aggregation stability.

## Local development & testing

**Python:** run all pipeline commands via [uv](https://docs.astral.sh/uv/) from `pipeline/` (matches CI in `.github/workflows/pipeline.yml`). Install deps first with `uv sync --locked --all-extras --dev`.

```bash
# Pipeline unit tests (from pipeline/)
uv run pytest test/unit_integration/

# Pipeline e2e tests — run from repo root; rebuild and restart containers every time
docker compose build
docker compose up -d
cd pipeline && uv run pytest test/e2e/

# Webapp (from webapp/)
npm run dev

# Webapp typecheck (matches Vercel/CI — run after query/dashboard changes)
npm run build
```

**Webapp TypeScript:** After editing `webapp/src/lib/queries/` (especially `dashboard.ts`), run `npm run build` from `webapp/` — do not rely on filtered `tsc` output (`| rg …`) or `|| echo OK`, which can miss errors. The `@opensearch-project/opensearch` SDK types for aggregation buckets (`StringTermsBucket`, `HistogramBucket`, etc.) do not include nested sub-aggregations. When parsing nested aggs, extend the bucket type explicitly (see `StringTermsBucketWithStates` in `dashboard.ts`), matching the sub-agg name in your query (`states`, `byDecision`, etc.). Use `stringTermsBuckets()` to normalise `buckets`, which the SDK types as an array or keyed record.

E2E tests invoke the four pipeline Lambdas over HTTP (scraper 9000, augmenter 9001, indexer 9002, company_disambiguator 9003) plus OpenSearch (9200) and a fake GOV.UK/Companies House API (`pipeline/test/e2e/__init__.py`, `docker-compose.yml`). **`docker compose build` and `docker compose up -d` are required before each e2e run** — do not assume containers from a previous session are still valid.

Set `MOCK_LLM=1` on augmenter to use `mock_augmentation.py` instead of live Gemini calls (the compose file sets `MOCK_LLM=true` on augmenter and company_disambiguator already).

## Key files quick reference

| Concern | File |
|---------|------|
| Lambda shared I/O (`DocumentRef`, `map_doc`) | `pipeline/src/lambdas/__init__.py` |
| Step Function definition | `terraform/state-machine/pipeline.asl.json` |
| Merge decisions → outcome | `pipeline/src/pipeline/decisions_to_outcomes.py` |
| Build indexed document | `pipeline/src/pipeline/transforms/__init__.py` `transform_for_index` |
| Scraper item shape | `pipeline/src/pipeline/spider/cac_outcome_spider.py` |
| Webapp search API | `webapp/src/app/api/outcomes/route.ts` |
| Webapp OpenSearch reads | `webapp/src/lib/queries/outcomes.ts` |
| Production index name | `OUTCOMES_INDEX` env on Vercel (typically `outcomes-indexed-1012`) |

## Conventions

- **Python commands** — use `uv run …` from `pipeline/` (e.g. `uv run pytest`, `uv run baml-cli generate`), not bare `python`/`pytest`.
- **References** normalized via `normalize_reference()` (zero-pad TUR1 number segment).
- **Parties** parsed from outcome title: `"Union A, Union B & Employer Ltd"` → `{unions, employer}`.
- **Dates** in extracted data are strings as they appear in documents; event machine parses them with `dateutil`.
- Do not commit secrets; OpenSearch and API keys come from AWS Secrets Manager in Lambdas.
- Only create git commits when explicitly asked.
