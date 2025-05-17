resource "vercel_project" "digitalorganising_webapp" {
  name      = "cac-webapp"
  framework = "nextjs"

  oidc_token_config = {
    enabled     = true
    issuer_mode = "team"
  }
}

resource "vercel_project_domain" "cac_digitalorganising" {
  project_id = vercel_project.digitalorganising_webapp.id
  domain     = aws_route53_record.digitalorganising_cac.name
}

resource "vercel_project_domain" "cac_digitalorganizing" {
  project_id = vercel_project.digitalorganising_webapp.id
  domain     = "cac.digitalorganiz.ing"

  redirect             = vercel_project_domain.cac_digitalorganising.domain
  redirect_status_code = 301
}

data "vercel_team_config" "digitalorganising" {
  id = vercel_project.digitalorganising_webapp.team_id
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
      test     = "StringEquals"
      variable = "${aws_iam_openid_connect_provider.vercel.url}:sub"
      values   = ["owner:${data.vercel_team_config.digitalorganising.slug}:project:${vercel_project.digitalorganising_webapp.name}:environment:production"]
    }
    condition {
      test     = "StringEquals"
      variable = "${aws_iam_openid_connect_provider.vercel.url}:aud"
      values   = ["https://vercel.com/${data.vercel_team_config.digitalorganising.slug}"]
    }
  }

}
