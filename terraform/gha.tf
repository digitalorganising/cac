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

data "aws_iam_policy_document" "ecr_push" {
  statement {
    effect = "Allow"
    actions = [
      "ecr:CompleteLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:InitiateLayerUpload",
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer"
    ]
    resources = [aws_ecr_repository.pipeline.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "ecr_push" {
  name        = "ecr-push"
  description = "Allow pushes to the pipeline ECR repository"
  policy      = data.aws_iam_policy_document.ecr_push.json
}

resource "aws_iam_role_policy_attachment" "ecr_push" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.ecr_push.arn
}

data "aws_iam_policy_document" "lambda_update" {
  statement {
    effect = "Allow"
    actions = [
      "lambda:UpdateFunctionCode"
    ]
    resources = [
      module.scraper.function.arn,
      module.augmenter.function.arn,
      module.indexer.function.arn,
      module.company_disambiguator.function.arn
    ]
  }
}

resource "aws_iam_policy" "lambda_update" {
  name        = "lambda-update"
  description = "Allow updates to the pipeline Lambda functions"
  policy      = data.aws_iam_policy_document.lambda_update.json
}

resource "aws_iam_role_policy_attachment" "lambda_update" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.lambda_update.arn
}
