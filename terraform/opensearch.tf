locals {
  endpoint = "search.cac.api.digitalorganis.ing"
}

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
    anonymous_auth_enabled         = true
    master_user_options {
      master_user_arn = aws_iam_role.opensearch_master_user.arn
    }
  }

  domain_endpoint_options {
    custom_endpoint                 = local.endpoint
    custom_endpoint_enabled         = true
    custom_endpoint_certificate_arn = aws_acm_certificate_validation.cac_search.certificate_arn
    enforce_https                   = true
    tls_security_policy             = "Policy-Min-TLS-1-2-PFS-2023-10"
  }

  ip_address_type = "dualstack"
}

resource "aws_acm_certificate" "cac_search" {
  domain_name       = local.endpoint
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "cac_search" {
  certificate_arn         = aws_acm_certificate.cac_search.arn
  validation_record_fqdns = [for record in aws_route53_record.cac_search_validation : record.fqdn]
}

resource "aws_opensearch_saml_options" "cac_search" {
  domain_name = aws_opensearch_domain.cac_search.domain_name

  saml_options {
    enabled = true
  }
}
