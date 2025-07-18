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
  opensearch_endpoint = "https://${aws_opensearch_domain.cac_search.endpoint_v2}"
}

module "scraper" {
  source        = "./modules/lambda"
  name          = "pipeline-scraper"
  image_uri     = "${aws_ecr_repository.pipeline.repository_url}:latest"
  image_command = ["lambdas.scraper.handler"]
  timeout       = 60 * 15
  memory_size   = 3008
  environment = {
    OPENSEARCH_ENDPOINT = local.opensearch_endpoint
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
    OPENSEARCH_ENDPOINT   = local.opensearch_endpoint
    GOOGLE_API_KEY_SECRET = aws_secretsmanager_secret.google_api_key.arn
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
    OPENSEARCH_ENDPOINT = local.opensearch_endpoint
  }
}

module "pipeline_step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "5.0.1"

  name = "cac-pipeline"
  type = "STANDARD"

  definition = templatefile("${path.module}/state-machine/pipeline.asl.json", {
    batch_size           = 10
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
