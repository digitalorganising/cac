## What do I want this to do

### Outcomes:

1. I can see a timeline of CAC outcomes with key information visible
2. I can search CAC outcomes
3. I can filter by entities (union, employer, panel member) and other information (final outcome)
4. I can view aggregated information about statutory recognition

### To do:

- [x] Try some free text summary of applications
- [x] Ingest plain docs into local ~Elasticsearch~ Opensearch
- [x] Write prompts + tests for all document types
  - [x] Add rejection reason parsing to application decisions
  - [x] Extract dates for all decisions
  - [x] Get form-of-ballot details if decision was not required
- [x] Pipeline for docs with extracted data
  - [x] Build adapters for opensearch
  - [x] Rate-limited augmentation transformer
- [ ] Build interface for search & filter
- [ ] Dashboard or something?

