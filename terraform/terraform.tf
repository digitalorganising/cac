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
    bucket       = "digitalorganising-cac-terraform-state"
    key          = "terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
    profile      = "do-cac-admin"
    assume_role = {
      role_arn = "arn:aws:iam::627738371162:role/digitalorganising-cac-admin"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = local.region
  profile = "do-cac-admin"
}

provider "aws" {
  region  = "us-east-1"
  alias   = "us_east_1"
  profile = "do-cac-admin"
}
