locals {
  pipeline_roles = ["scraper", "augmenter", "indexer", "merger"]
}

resource "aws_iam_role" "pipeline_role" {
  for_each           = toset(local.pipeline_roles)
  name               = "pipeline-${each.value}"
  assume_role_policy = data.aws_iam_policy_document.pipeline_role_trust_policy.json
}

data "aws_iam_policy_document" "pipeline_role_trust_policy" {
  statement {
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      ]
    }
    actions = ["sts:AssumeRole"]
  }
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}
