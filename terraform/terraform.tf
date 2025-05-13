locals {
  region = "eu-west-1"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.97.0"
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
  profile = "sso-profile"
}
