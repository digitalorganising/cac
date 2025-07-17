resource "opensearch_role" "main" {
  role_name = var.service_name

  cluster_permissions = var.write_prefixes != [] ? ["cluster_composite_ops", "indices:data/read/scroll/clear"] : ["cluster_composite_ops_ro", "indices:data/read/scroll/clear"]

  dynamic "index_permissions" {
    for_each = var.write_prefixes != [] ? [var.write_prefixes] : []
    content {
      index_patterns  = [for prefix in index_permissions.value : "${prefix}*"]
      allowed_actions = ["write", "manage"]
    }
  }

  dynamic "index_permissions" {
    for_each = var.read_prefixes != [] ? [var.read_prefixes] : []
    content {
      index_patterns  = [for prefix in index_permissions.value : "${prefix}*"]
      allowed_actions = ["read", "indices:data/read/scroll/clear"]
    }
  }
}

resource "opensearch_roles_mapping" "main" {
  role_name     = opensearch_role.main.role_name
  backend_roles = [var.backend_role]
}

variable "service_name" {
  type = string
}

variable "write_prefixes" {
  default = []
  type    = list(string)
}

variable "read_prefixes" {
  default = []
  type    = list(string)
}

variable "backend_role" {
  type = string
}

terraform {
  required_providers {
    opensearch = {
      source = "opensearch-project/opensearch"
    }
  }
}
