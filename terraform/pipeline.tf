resource "aws_ecr_repository" "pipeline" {
  name = "cac-pipeline"
}

resource "aws_ecr_lifecycle_policy" "pipeline" {
  repository = aws_ecr_repository.pipeline.name
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the last 2 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 2
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

locals {
  opensearch_endpoint = "${bonsai_cluster.cac_search.access.scheme}://${bonsai_cluster.cac_search.access.host}:${bonsai_cluster.cac_search.access.port}"
  batch_size          = 20
}

module "scraper" {
  source        = "./modules/lambda"
  name          = "pipeline-scraper"
  image_uri     = "${aws_ecr_repository.pipeline.repository_url}:latest"
  image_command = ["lambdas.scraper.handler"]
  timeout       = 60 * 15
  memory_size   = 3008
  environment = {
    OPENSEARCH_ENDPOINT           = local.opensearch_endpoint
    OPENSEARCH_CREDENTIALS_SECRET = module.opensearch_credentials.arn
    API_BASE                      = "https://${vercel_project_domain.cac_digitalorganising.domain}/api"
    OPENSEARCH_BATCH_SIZE         = local.batch_size
  }
}

module "augmenter" {
  source        = "./modules/lambda"
  name          = "pipeline-augmenter"
  image_uri     = "${aws_ecr_repository.pipeline.repository_url}:latest"
  image_command = ["lambdas.augmenter.handler"]
  timeout       = 60 * 15
  memory_size   = 512
  environment = {
    OPENSEARCH_ENDPOINT           = local.opensearch_endpoint
    OPENSEARCH_CREDENTIALS_SECRET = module.opensearch_credentials.arn
    GOOGLE_API_KEY_SECRET         = module.google_api_key.arn
  }
}


module "indexer" {
  source        = "./modules/lambda"
  name          = "pipeline-indexer"
  image_uri     = "${aws_ecr_repository.pipeline.repository_url}:latest"
  image_command = ["lambdas.indexer.handler"]
  timeout       = 60 * 15
  memory_size   = 512
  environment = {
    OPENSEARCH_ENDPOINT           = local.opensearch_endpoint
    OPENSEARCH_CREDENTIALS_SECRET = module.opensearch_credentials.arn
  }
}

module "company_disambiguator" {
  source        = "./modules/lambda"
  name          = "pipeline-company-disambiguator"
  image_uri     = "${aws_ecr_repository.pipeline.repository_url}:latest"
  image_command = ["lambdas.company_disambiguator.handler"]
  timeout       = 60 * 15
  memory_size   = 512
  environment = {
    CH_API_BASE                   = "https://api.company-information.service.gov.uk"
    COMPANIES_HOUSE_API_KEY_SECRET = module.companies_house_api_key.arn
    OPENSEARCH_ENDPOINT           = local.opensearch_endpoint
    OPENSEARCH_CREDENTIALS_SECRET = module.opensearch_credentials.arn
  }
}

module "pipeline_step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "5.0.1"

  name = "cac-pipeline"
  type = "STANDARD"

  definition = templatefile("${path.module}/state-machine/pipeline.asl.json", {
    batch_size           = local.batch_size
    scraper_lambda_arn   = module.scraper.function.arn
    augmenter_lambda_arn = module.augmenter.function.arn
    indexer_lambda_arn   = module.indexer.function.arn
  })

  service_integrations = {
    lambda = {
      lambda = [
        module.scraper.function.arn,
        module.augmenter.function.arn,
        module.indexer.function.arn
      ]
    }
  }

  cloudwatch_log_group_retention_in_days = 3
  logging_configuration = {
    include_execution_data = true
    level                  = "ALL"
  }
}
