resource "aws_secretsmanager_secret" "google_api_key" {
  name        = "cac-pipeline-google-api-key"
  description = "Secret for the CAC pipeline google api key"
}

data "aws_iam_policy_document" "augmenter_secrets_access" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [aws_secretsmanager_secret.google_api_key.arn]
  }
}

resource "aws_iam_policy" "augmenter_secrets_access" {
  name        = "augmenter-secrets-access"
  description = "Allow augmenter lambda to access secrets manager"
  policy      = data.aws_iam_policy_document.augmenter_secrets_access.json
}

resource "aws_iam_role_policy_attachment" "augmenter_secrets_access" {
  role       = module.augmenter.role.name
  policy_arn = aws_iam_policy.augmenter_secrets_access.arn
}
