resource "aws_ecrpublic_repository" "opensearch" {
  repository_name = "opensearch"
  provider        = aws.us_east_1
}
