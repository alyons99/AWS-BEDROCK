#zips the lambda function as required by AWS to function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/lambda_function.py"
  output_path = "${path.module}/dist/lambda_function.zip"
}

#Setup for Lambda function
resource "aws_lambda_function" "bedrock_inference" {
  function_name    = var.project_name
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30


  environment {
    variables = {
      MODEL_ID = var.model_id
    }
  }

#passing variables through
  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy.lambda_inline
  ]

  tags = {
    Project = var.project_name
  }
}