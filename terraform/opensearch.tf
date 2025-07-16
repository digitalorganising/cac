resource "aws_opensearch_domain" "cac_search" {
  domain_name    = "cac-cluster"
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

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
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

  depends_on = [
    aws_cognito_user_pool_domain.digitalorganising_users_domain,
    aws_iam_role_policy_attachment.opensearch_cognito_role_policy_attachment
  ]
}

data "aws_iam_policy_document" "opensearch_domain_access_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["es:*"]
    resources = ["${aws_opensearch_domain.cac_search.arn}/*"]
  }
}

resource "aws_opensearch_domain_policy" "opensearch_domain_policy" {
  domain_name     = aws_opensearch_domain.cac_search.domain_name
  access_policies = data.aws_iam_policy_document.opensearch_domain_access_policy.json
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
    index_patterns  = ["outcomes-raw*"]
    allowed_actions = ["write", "manage"]
  }
}

resource "opensearch_role" "augmented_writer" {
  role_name   = "augmented_writer"
  description = "Read from 'raw' and write to 'augmented' indices"

  index_permissions {
    index_patterns  = ["outcomes-raw*"]
    allowed_actions = ["read"]
  }

  index_permissions {
    index_patterns  = ["outcomes-augmented*"]
    allowed_actions = ["write", "manage"]
  }
}

resource "opensearch_role" "indexed_writer" {
  role_name   = "indexed_writer"
  description = "Read from 'augmented' and write to 'indexed' indices"

  index_permissions {
    index_patterns  = ["outcomes-augmented*"]
    allowed_actions = ["read"]
  }

  index_permissions {
    index_patterns  = ["outcomes-indexed*"]
    allowed_actions = ["write", "manage"]
  }
}

resource "opensearch_roles_mapping" "cac_webapp_vercel" {
  role_name   = opensearch_role.indexed_reader.role_name
  description = "Mapping Vercel role to OpenSearch role"
  backend_roles = [
    aws_iam_role.cac_webapp_vercel.arn
  ]
}

resource "opensearch_roles_mapping" "scraper" {
  role_name   = opensearch_role.ingest_writer.role_name
  description = "Mapping Scraper role to OpenSearch role"
  backend_roles = [
    module.scraper.role.arn
  ]
}

resource "opensearch_roles_mapping" "augmenter" {
  role_name   = opensearch_role.augmented_writer.role_name
  description = "Mapping Augmenter role to OpenSearch role"
  backend_roles = [
    module.augmenter.role.arn
  ]
}

resource "opensearch_roles_mapping" "indexer" {
  role_name   = opensearch_role.indexed_writer.role_name
  description = "Mapping Indexer role to OpenSearch role"
  backend_roles = [
    module.indexer.role.arn
  ]
}
