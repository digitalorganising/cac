locals {
  mappings_dir = "${path.root}/../pipeline/index_mappings"
}

resource "opensearch_index" "outcomes_raw" {
  name     = "outcomes-raw"
  mappings = file("${local.mappings_dir}/outcomes_raw.json")
}

resource "opensearch_index" "outcomes_augmented" {
  name     = "outcomes-augmented"
  mappings = file("${local.mappings_dir}/outcomes_augmented.json")
}

resource "opensearch_index" "outcomes_indexed" {
  name     = "outcomes-indexed"
  mappings = file("${local.mappings_dir}/outcomes_indexed.json")
}
