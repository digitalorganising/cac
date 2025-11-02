resource "vercel_project" "cac_webapp" {
  name          = "cac-webapp"
  build_command = ""

  oidc_token_config = {
    enabled     = true
    issuer_mode = "team"
  }
}

locals {
  vercel_envs = ["production", "preview", "development"]
}

resource "vercel_project_environment_variable" "cac_webapp_opensearch_endpoint" {
  project_id = vercel_project.cac_webapp.id
  key        = "OPENSEARCH_ENDPOINT"
  value      = local.opensearch_endpoint
  target     = local.vercel_envs
}

resource "vercel_project_environment_variable" "cac_webapp_opensearch_credentials_secret" {
  project_id = vercel_project.cac_webapp.id
  key        = "OPENSEARCH_CREDENTIALS_SECRET"
  value      = module.opensearch_credentials.arn
  target     = local.vercel_envs
}

resource "vercel_project_environment_variable" "cac_webapp_outcomes_index" {
  project_id = vercel_project.cac_webapp.id
  key        = "OUTCOMES_INDEX"
  value      = "outcomes-indexed"
  target     = local.vercel_envs

  lifecycle {
    ignore_changes = [value]
  }
}

resource "vercel_project_environment_variable" "cac_webapp_aws_region" {
  project_id = vercel_project.cac_webapp.id
  key        = "AWS_REGION"
  value      = local.region
  target     = local.vercel_envs
}

resource "vercel_project_environment_variable" "cac_webapp_aws_role_arn" {
  project_id = vercel_project.cac_webapp.id
  key        = "AWS_ROLE_ARN"
  value      = aws_iam_role.cac_webapp_vercel.arn
  target     = local.vercel_envs
}

resource "vercel_project_domain" "cac_digitalorganising" {
  project_id = vercel_project.cac_webapp.id
  domain     = aws_route53_record.digitalorganising_cac.name
}

resource "vercel_project_domain" "cac_digitalorganizing" {
  project_id = vercel_project.cac_webapp.id
  domain     = "cac.digitalorganiz.ing"

  redirect             = vercel_project_domain.cac_digitalorganising.domain
  redirect_status_code = 301
}

data "vercel_team_config" "digitalorganising" {
  id = vercel_project.cac_webapp.team_id
}

resource "aws_iam_openid_connect_provider" "vercel" {
  url = "https://oidc.vercel.com/${data.vercel_team_config.digitalorganising.slug}"
  client_id_list = [
    "https://vercel.com/${data.vercel_team_config.digitalorganising.slug}"
  ]
}

resource "aws_iam_role" "cac_webapp_vercel" {
  name               = "cac-webapp-vercel"
  assume_role_policy = data.aws_iam_policy_document.cac_webapp_vercel_role_trust.json
}

data "aws_iam_policy_document" "cac_webapp_vercel_role_trust" {
  statement {
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.vercel.arn]
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringLike"
      variable = "${aws_iam_openid_connect_provider.vercel.url}:sub"
      values   = ["owner:${data.vercel_team_config.digitalorganising.slug}:project:${vercel_project.cac_webapp.name}:environment:*"]
    }
    condition {
      test     = "StringEquals"
      variable = "${aws_iam_openid_connect_provider.vercel.url}:aud"
      values   = ["https://vercel.com/${data.vercel_team_config.digitalorganising.slug}"]
    }
  }

}
