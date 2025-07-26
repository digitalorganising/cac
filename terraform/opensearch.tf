resource "bonsai_cluster" "cac_search" {
  name = "Digitalorganising search"

  plan = {
    slug = "sandbox"
  }

  space = {
    path = "omc/bonsai/${local.region}/common"
  }

  release = {
    slug = "opensearch-2.6.0-mt"
  }
}
