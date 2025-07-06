resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.name}"
  retention_in_days = 5

  tags = {
    Name = "${var.name}-log-group"
  }
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "${var.name}-logging"
  description = "Allow Lambda to write logs to CloudWatch"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect    = "Allow"
    actions   = ["logs:CreateLogGroup"]
    resources = ["arn:aws:logs:region:${data.aws_caller_identity.current.account_id}:*"]
  }
  statement {
    effect  = "Allow"
    actions = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [
      "${aws_cloudwatch_log_group.lambda.arn}:*"
    ]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_logging" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}
