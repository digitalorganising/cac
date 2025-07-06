resource "aws_lambda_function" "main" {
  function_name = var.name
  timeout       = var.timeout
  memory_size   = var.memory_size

  package_type = "Image"
  image_uri    = var.image_uri
  image_config {
    command = var.image_command
  }

  environment {
    variables = var.environment
  }

  role = aws_iam_role.lambda.arn
}

resource "aws_iam_role" "lambda" {
  name               = "${var.name}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_role_trust_policy.json
}

data "aws_iam_policy_document" "lambda_role_trust_policy" {
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
