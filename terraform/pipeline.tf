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

resource "aws_ecr_repository" "pipeline" {
  name = "cac-pipeline"
}

resource "aws_ecr_lifecycle_policy" "pipeline" {
  repository = aws_ecr_repository.pipeline.name
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the last 2 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 2
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_lambda_function" "scraper" {
  function_name = "pipeline-scraper"
  role          = aws_iam_role.pipeline_role["scraper"].arn
  timeout       = 60 * 5

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.pipeline.repository_url}:latest"
  image_config {
    command = ["lambda_functions.scrape_all_outcomes_handler"]
  }
}
