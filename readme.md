# Governed LLM Deployment on AWS Bedrock

## What This Builds
A single Lambda function that accepts a text prompt, calls Amazon Bedrock for LLM inference, and returns the response. Every invocation is logged to CloudWatch in structured JSON. All infrastructure is declared in Terraform and reproducible from a clean AWS account.

Goal is to safely integrate the capabilites of a LLM safely into a secure system. 

## Prerequisites
- AWS account with Bedrock model access enabled — go to the Bedrock console → Model access and request Claude 3 Haiku
- Terraform >= 1.5
- AWS CLI configured (aws configure) with credentials that have permission to create Lambda, IAM, and CloudWatch resources
- Recommended region: us-east-1

## Quick Start
1. Clone the repo
2. terraform init && terraform apply
3. Invoke the test function
4. Check CloudWatch Logs for results

## NIST 800-53 Control Mapping
See nist.md in docs/

## Architecture
<img src="https://github.com/alyons99/AWS-BEDROCK/blob/main/docs/AWS%20Bedrock%20Invocation%20Flow.png" alt="Alt text" width="350" height="350">
See architecture.md in docs/ for more information

## Cost
This project runs almost entirely within the AWS Free Tier for low-volume testing.
Estimated cost for development and testing (100–200 invocations): under $0.10 total. Claude 3 Haiku is the least expensive Bedrock model and is used here specifically for that reason. 
Run terraform destroy when not actively testing to ensure no idle resources accumulate cost.

## Production Considerations
This project is an MVP and would require changes to be ready for a production environment.

 1. he Lambda function currently has no caller authentication.
 2. There is no input validtation other than a null check for the prompt. Would likely want to check/sanatize inputs and maybe put guardrails on token usage.
 3. VPC Endpoint should be used as Bedrock is a public service.
 4. Logs should be encrypted in transit and at rest using customer managed keys (CMKs)
