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
  assume_role_policy = data.aws_iam_policy_document.search_service_assume_execution_role.json
}

data "aws_iam_policy_document" "search_service_assume_execution_role" {
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

resource "aws_iam_role" "search_service_role" {
  name               = "search-service-role"
  assume_role_policy = data.aws_iam_policy_document.search_service_assume_role.json
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "search_service_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:ecs:${local.region}:${data.aws_caller_identity.current.account_id}:*"]
    }
  }
}

resource "aws_iam_policy" "cert_fetcher_dns_policy" {
  name        = "cert-fetcher-dns-policy"
  description = "Policy for the cert-fetcher container to access Route53"
  policy      = data.aws_iam_policy_document.cert_fetcher_dns_policy.json
}

# See https://certbot-dns-route53.readthedocs.io/en/stable/#sample-aws-policy-json
data "aws_iam_policy_document" "cert_fetcher_dns_policy" {
  statement {
    actions = [
      "route53:ListHostedZones",
      "route53:GetChange"
    ]
    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    actions = ["route53:ChangeResourceRecordSets"]
    resources = [
      "arn:aws:route53:::hostedzone/${aws_route53_zone.digitalorganising.zone_id}"
    ]
    effect = "Allow"
  }
}

resource "aws_iam_role_policy_attachment" "cert_fetcher_dns_policy_attachment" {
  role       = aws_iam_role.search_service_role.name
  policy_arn = aws_iam_policy.cert_fetcher_dns_policy.arn
}
