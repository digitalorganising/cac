locals {
  mappings_dir = "${path.root}/../pipeline/index_mappings"
}

resource "opensearch_index" "outcomes" {
  name = "cac-outcomes"
  mappings = file("${local.mappings_dir}/outcomes.json")
}
