resource "bonsai_cluster" "cac_search" {
  name = "Digitalorganising search"

  plan = {
    slug = "staging"
  }

  space = {
    path = "omc/bonsai/${local.region}/common"
  }

  release = {
    slug = "opensearch-2.19.4"
  }
}
