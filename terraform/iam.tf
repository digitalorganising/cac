resource "aws_iam_role" "opensearch_master_user" {
  name               = "opensearch-master-user"
  assume_role_policy = data.aws_iam_policy_document.opensearch_master_user_assume_role_policy.json
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "opensearch_master_user_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = [data.aws_caller_identity.current.arn]
    }
  }
}

data "aws_iam_policy_document" "opensearch_domain_access_policy" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["es:ESHttp*"]
    resources = ["${aws_opensearch_domain.cac_search.arn}/*"]
  }
}

resource "aws_opensearch_domain_policy" "opensearch_domain_policy" {
  domain_name     = aws_opensearch_domain.cac_search.domain_name
  access_policies = data.aws_iam_policy_document.opensearch_domain_access_policy.json
}
