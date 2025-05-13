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

  cognito_identity_providers {
    client_id     = aws_cognito_managed_user_pool_client.opensearch_managed_client.id
    provider_name = aws_cognito_user_pool.digitalorganising_users.endpoint
  }
}

resource "aws_cognito_managed_user_pool_client" "opensearch_managed_client" {
  name_prefix  = "AmazonOpenSearchService-cac-search-"
  user_pool_id = aws_cognito_user_pool.digitalorganising_users.id
}

data "aws_iam_policy_document" "cognito_user_authenticated_role_trust_policy" {
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
}

resource "aws_iam_role" "cognito_user_authenticated_role" {
  name               = "cognito_authenticated_role"
  assume_role_policy = data.aws_iam_policy_document.cognito_user_authenticated_role_trust_policy.json
}

resource "aws_cognito_identity_pool_roles_attachment" "cognito_user_authenticated_role_attachment" {
  identity_pool_id = aws_cognito_identity_pool.opensearch_identity_pool.id
  roles = {
    authenticated = aws_iam_role.cognito_user_authenticated_role.arn
  }
}
