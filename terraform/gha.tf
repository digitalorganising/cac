resource "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = [
    "sts.amazonaws.com"
  ]
}

resource "aws_iam_role" "github_actions" {
  name               = "github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_actions_trust_policy.json
}

data "aws_iam_policy_document" "github_actions_trust_policy" {
  statement {
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github_actions.arn]
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:digitalorganising/cac:*"]
    }
  }
}

data "aws_iam_policy_document" "s3_package_write" {
  statement {
    effect  = "Allow"
    actions = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket"]
    resources = [
      aws_s3_bucket.pipeline_app.arn,
      "${aws_s3_bucket.pipeline_app.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "s3_package_policy" {
  name        = "s3-package-policy"
  description = "Allow writes to the pipeline-app bucket"
  policy      = data.aws_iam_policy_document.s3_package_write.json
}

resource "aws_iam_role_policy_attachment" "s3_package_policy_attachment" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.s3_package_policy.arn
}
