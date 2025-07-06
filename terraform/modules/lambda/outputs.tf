output "function" {
  value = aws_lambda_function.main
}

output "role" {
  value = aws_iam_role.lambda
}
