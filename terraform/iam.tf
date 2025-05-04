resource "aws_iam_instance_profile" "search" {
  name = "search-instance-profile"
  role = aws_iam_role.search_instance.name
}

data "aws_iam_policy_document" "search_instance_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs.amazonaws.com", "ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "search_instance" {
  name               = "search-instance-role"
  assume_role_policy = data.aws_iam_policy_document.search_instance_assume_role.json
}

resource "aws_iam_role_policy_attachment" "search_instance_policy" {
  role       = aws_iam_role.search_instance.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role" "search_service_execution_role" {
  name               = "search-service-execution-role"
  assume_role_policy = data.aws_iam_policy_document.search_service_execution_role.json
}

data "aws_iam_policy_document" "search_service_execution_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "search_service_execution_policy" {
  role       = aws_iam_role.search_service_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "search_service_secrets" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.opensearch_admin_password.arn]
  }
}

resource "aws_iam_role_policy" "search_service_secrets" {
  name   = "search-service-secrets"
  role   = aws_iam_role.search_service_execution_role.name
  policy = data.aws_iam_policy_document.search_service_secrets.json
}
