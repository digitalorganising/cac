resource "bonsai_cluster" "cac_search" {
  name = "Digitalorganising search"

  plan = {
    slug = "staging-2024"
  }

  space = {
    path = "omc/bonsai/${local.region}/common"
  }

  release = {
    slug = "opensearch-2.6.0-mt"
  }
}
