data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "opensearch_domain_access_policy" {
  statement {
    effect = "Allow"
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

resource "aws_iam_role" "opensearch_master_user" {
  name               = "opensearch-master-user"
  assume_role_policy = data.aws_iam_policy_document.opensearch_master_user_trust_policy.json
}

data "aws_iam_policy_document" "opensearch_master_user_trust_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Federated"
      identifiers = ["cognito-identity.amazonaws.com"]
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringEquals"
      variable = "cognito-identity.amazonaws.com:aud"
      values   = [aws_cognito_identity_pool.opensearch_identity_pool.id]
    }
    condition {
      test     = "ForAnyValue:StringLike"
      variable = "cognito-identity.amazonaws.com:amr"
      values   = ["authenticated"]
    }
  }

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
}

resource "aws_iam_role" "opensearch_cognito_role" {
  name               = "opensearch-cognito-role"
  assume_role_policy = data.aws_iam_policy_document.opensearch_cognito_role_trust_policy.json
}


data "aws_iam_policy_document" "opensearch_cognito_role_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["opensearchservice.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "opensearch_cognito_role_policy_attachment" {
  role       = aws_iam_role.opensearch_cognito_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonOpenSearchServiceCognitoAccess"
}

data "aws_iam_policy_document" "opensearch_cognito_additional_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ec2:DescribeVpcs",
      "cognito-identity:ListIdentityPools",
      "cognito-idp:ListUserPools"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "iam:GetRole",
      "iam:PassRole"
    ]
    resources = [aws_iam_role.opensearch_cognito_role.arn]
  }
}

resource "aws_iam_policy" "opensearch_cognito_additional_policy" {
  name        = "opensearch-cognito-additional-policy"
  description = "Additional policy for OpenSearch Cognito role"
  policy      = data.aws_iam_policy_document.opensearch_cognito_additional_policy.json
}

resource "aws_iam_role_policy_attachment" "opensearch_cognito_additional_policy_attachment" {
  role       = aws_iam_role.opensearch_cognito_role.name
  policy_arn = aws_iam_policy.opensearch_cognito_additional_policy.arn
}
