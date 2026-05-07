#allow lambda to assume role
data "aws_iam_policy_document" "lambda_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}


data "aws_iam_policy_document" "lambda_permissions" {
  #allow lambda to invoke bedrock
  statement {
    sid     = "AllowBedrockInvokeOnly"
    actions = ["bedrock:InvokeModel"]
    resources = [
      "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.model_id}"
    ]
  }

  #allow the creation of CW Logs
  statement {
    sid = "AllowCloudWatchLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.project_name}:*"
    ]
  }
}

#execution role w/ trust
resource "aws_iam_role" "lambda_exec" {
  name               = "${var.project_name}-exec-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json

  tags = {
    Project = var.project_name
  }
}

#policy attached to execution role
resource "aws_iam_role_policy" "lambda_inline" {
  name   = "${var.project_name}-inline-policy"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.lambda_permissions.json
}