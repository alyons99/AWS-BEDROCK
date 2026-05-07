output "function_name" {
  value = aws_lambda_function.bedrock_inference.function_name
}

output "function_arn" {
  value = aws_lambda_function.bedrock_inference.arn
}

output "execution_role_arn" {
  value = aws_iam_role.lambda_exec.arn
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.lambda_logs.name
}