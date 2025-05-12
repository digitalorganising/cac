resource "aws_s3_bucket" "terraform_state" {
  bucket = "digitalorganising-cac-terraform-state-delta"
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket_public_access_block" "terraform_state_bucket_public_access_block" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_role" "admin_role" {
  name = "digitalorganising-cac-admin"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          AWS = data.aws_caller_identity.current.account_id
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "terraform_role_policy_attachment" {
  role       = aws_iam_role.admin_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

output "admin_role_arn" {
  value = aws_iam_role.admin_role.arn
}

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region  = "eu-west-1"
  profile = "do-cac-admin"
}



