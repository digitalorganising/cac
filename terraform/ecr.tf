resource "aws_ecrpublic_repository" "opensearch" {
  repository_name = "opensearch"
  provider        = aws.us_east_1
}

resource "aws_ecrpublic_repository" "cert_fetcher" {
  repository_name = "cert-fetcher"
  provider        = aws.us_east_1
}

