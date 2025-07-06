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

module "scraper" {
  source        = "./modules/lambda"
  name          = "pipeline-scraper"
  image_uri     = "${aws_ecr_repository.pipeline.repository_url}:latest"
  image_command = ["lambdas.scraper.handler"]
  timeout       = 60 * 15
  memory_size   = 512
  environment = {
    OPENSEARCH_ENDPOINT = "https://${aws_opensearch_domain.cac_search.endpoint_v2}"
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
    OPENSEARCH_ENDPOINT = "https://${aws_opensearch_domain.cac_search.endpoint_v2}"
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
    OPENSEARCH_ENDPOINT = "https://${aws_opensearch_domain.cac_search.endpoint_v2}"
  }
}
