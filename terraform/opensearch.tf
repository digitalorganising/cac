resource "aws_opensearch_domain" "cac_search" {
  domain_name    = "cac-search"
  engine_version = "OpenSearch_2.19"

  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = false
    anonymous_auth_enabled         = false
    master_user_options {
      master_user_arn = aws_iam_role.opensearch_master_user.arn
    }
  }

  # TODO: Replace with Identity Center trusted identity propagation once available in tf
  # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/idc-aos.html
  # https://github.com/hashicorp/terraform-provider-aws/issues/41026
  cognito_options {
    enabled          = true
    user_pool_id     = aws_cognito_user_pool.digitalorganising_users.id
    identity_pool_id = aws_cognito_identity_pool.opensearch_identity_pool.id
    role_arn         = aws_iam_role.opensearch_cognito_role.arn
  }

  ip_address_type = "dualstack"
}

resource "opensearch_role" "indexed_reader" {
  role_name   = "indexed_reader"
  description = "Read any documents in indices ending with 'indexed'"

  index_permissions {
    index_patterns  = ["*indexed"]
    allowed_actions = ["read"]
  }
}

resource "opensearch_role" "ingest_writer" {
  role_name   = "ingest_writer"
  description = "Write to 'raw' indices"

  index_permissions {
    index_patterns  = ["*raw"]
    allowed_actions = ["write"]
  }
}

resource "opensearch_role" "augmented_writer" {
  role_name   = "ingest_writer"
  description = "Read from 'raw' and write to 'augmented' indices"

  index_permissions {
    index_patterns  = ["*raw"]
    allowed_actions = ["read"]
  }

  index_permissions {
    index_patterns  = ["*augmented"]
    allowed_actions = ["write"]
  }
}

resource "opensearch_role" "merged_writer" {
  role_name   = "merged_writer"
  description = "Read from 'augmented' and write to 'merged' indices"

  index_permissions {
    index_patterns  = ["*augmented"]
    allowed_actions = ["read"]
  }

  index_permissions {
    index_patterns  = ["*merged"]
    allowed_actions = ["write"]
  }
}

resource "opensearch_role" "indexed_writer" {
  role_name   = "indexed_writer"
  description = "Read from 'merged' and write to 'indexed' indices"

  index_permissions {
    index_patterns  = ["*merged"]
    allowed_actions = ["read"]
  }

  index_permissions {
    index_patterns  = ["*indexed"]
    allowed_actions = ["write"]
  }
}

resource "opensearch_roles_mapping" "cac_webapp_vercel" {
  role_name   = opensearch_role.indexed_reader.role_name
  description = "Mapping Vercel role to OpenSearch role"
  backend_roles = [
    aws_iam_role.cac_webapp_vercel.arn
  ]
}

locals {
  pipeline_role_mappings = {
    scraper   = opensearch_role.ingest_writer.role_name
    augmenter = opensearch_role.augmented_writer.role_name
    indexer   = opensearch_role.indexed_writer.role_name
    merger    = opensearch_role.merged_writer.role_name
  }
}

resource "opensearch_roles_mapping" "pipeline_role_mappings" {
  for_each    = local.pipeline_role_mappings
  role_name   = each.value
  description = "Mapping ${each.key} pipeline role to OpenSearch role"
  backend_roles = [
    aws_iam_role.pipeline_role[each.key].arn
  ]
}
