terraform {
  required_providers {
    opensearch = {
      source = "opensearch-project/opensearch"
      version = "2.3.0"
    }
  }
}

provider "opensearch" {
  url = "http://127.0.0.1:9200"
}
