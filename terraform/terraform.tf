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
    bonsai = {
      source  = "omc/bonsai"
      version = "~> 1.0"
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
