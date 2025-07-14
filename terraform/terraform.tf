locals {
  region  = "eu-west-1"
  profile = "sso-profile"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    vercel = {
      source  = "vercel/vercel"
      version = "~> 3.2.0"
    }
    opensearch = {
      source  = "opensearch-project/opensearch"
      version = "~> 2.3.1"
    }
  }

  backend "s3" {
    bucket       = "digitalorganising-cac-terraform-state-delta"
    key          = "terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
    profile      = "sso-profile"
    assume_role = {
      role_arn = "arn:aws:iam::510900713680:role/digitalorganising-cac-admin"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = local.region
  profile = local.profile
}

provider "vercel" {
  team = "digital-organising"
}

provider "opensearch" {
  url                 = local.opensearch_endpoint
  aws_assume_role_arn = aws_iam_role.opensearch_master_user.arn
  aws_profile         = local.profile
  aws_region          = local.region
}
