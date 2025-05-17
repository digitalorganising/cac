output "opensearch_endpoint" {
  value = aws_opensearch_domain.cac_search.endpoint_v2
}

output "pipeline_role_arns" {
  value = {
    for role in local.pipeline_roles : role => aws_iam_role.pipeline_role[role].arn
  }
}
