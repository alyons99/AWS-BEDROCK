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
<img src="https://github.com/alyons99/AWS-EVENT-DRIVEN-SECURITY-PIPELINE/blob/eeb30cc5c701479f94d37c10bc5c874207d9caf1/docs/AWS-EVENT-DRIVEN-SECURE-PIPELINE.png" alt="Alt text" width="450" height="300">
See architecture.md in docs/ for more information

## Cost

## Production Considerations
