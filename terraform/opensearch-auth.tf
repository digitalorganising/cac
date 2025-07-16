resource "aws_cognito_user_pool" "digitalorganising_users" {
  name = "digitalorganising-users"

  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
}

resource "aws_cognito_user_pool_domain" "digitalorganising_users_domain" {
  domain       = "digitalorganising-users"
  user_pool_id = aws_cognito_user_pool.digitalorganising_users.id
}

resource "aws_cognito_identity_pool" "opensearch_identity_pool" {
  identity_pool_name               = "opensearch-identity-pool"
  allow_unauthenticated_identities = false

  lifecycle {
    ignore_changes = [
      cognito_identity_providers
    ]
  }
}

resource "aws_cognito_managed_user_pool_client" "opensearch_managed_client" {
  name_prefix  = "AmazonOpenSearchService-${aws_opensearch_domain.cac_search.domain_name}"
  user_pool_id = aws_cognito_user_pool.digitalorganising_users.id

  depends_on = [aws_opensearch_domain.cac_search]
}

resource "aws_cognito_identity_pool_roles_attachment" "opensearch" {
  identity_pool_id = aws_cognito_identity_pool.opensearch_identity_pool.id
  roles = {
    "authenticated" = aws_iam_role.opensearch_master_user.arn
  }
}

data "aws_caller_identity" "current" {}

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
