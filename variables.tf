variable "aws_region" {
  default = "us-east-1"
}

#claude haiku is cheap so good for an MVP
variable "model_id" {
  default = "anthropic.claude-3-haiku-20240307-v1:0"
}

variable "project_name" {
  default = "bedrock-inference"
}

variable "log_retention_days" {
  default = 30
}