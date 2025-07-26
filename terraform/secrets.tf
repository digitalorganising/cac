module "google_api_key" {
  source         = "./modules/secret"
  name           = "google-api-key"
  description    = "Secret for the CAC pipeline google api key"
  accessor_roles = [module.augmenter.role.name]
}

module "opensearch_credentials" {
  source      = "./modules/secret"
  name        = "opensearch-credentials"
  description = "Secret for the CAC pipeline opensearch credentials"
  accessor_roles = [
    module.augmenter.role.name,
    module.indexer.role.name,
    module.scraper.role.name,
    aws_iam_role.cac_webapp_vercel.name
  ]
}
