variable "name" {
  type        = string
  description = "The name of the secret"
}

variable "description" {
  type        = string
  description = "The description of the secret"
}

variable "accessor_roles" {
  type        = list(string)
  description = "The roles that can access the secret"
}

resource "aws_secretsmanager_secret" "this" {
  name        = var.name
  description = var.description
}

data "aws_iam_policy_document" "this" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [aws_secretsmanager_secret.this.arn]
  }
}

resource "aws_iam_policy" "this" {
  name   = "${var.name}-secret-access"
  policy = data.aws_iam_policy_document.this.json
}

resource "aws_iam_role_policy_attachment" "this" {
  for_each   = toset(var.accessor_roles)
  role       = each.value
  policy_arn = aws_iam_policy.this.arn
}

output "arn" {
  value = aws_secretsmanager_secret.this.arn
}


