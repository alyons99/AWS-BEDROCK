# Architecture
 
## Overview
 
This project implements a fully serverless LLM inference endpoint on AWS,
integrating Amazon Bedrock for foundation model access with a least-privilege
IAM execution role and a structured CloudWatch audit trail. The architecture
is aligned with NIST 800-53 security controls, with particular focus on the
AC (Access Control) and AU (Audit and Accountability) control families.
 
No servers run continuously. No infrastructure exists between invocations.
Every component is idle and costs nothing until a request arrives.
 
## Pipeline Tiers
 
### Tier 1 Invocation
 
A caller invokes the Lambda function directly using AWS SigV4-signed API
calls via the AWS CLI or SDK. The event payload contains a single field:
 
- **`prompt`** — the text input to be sent to the foundation model
In this implementation the caller is a local terminal using `aws lambda
invoke`. In a production deployment the function would sit behind API
Gateway with an authorizer. No changes to the function code or IAM policy
are required to make that transition — the handler is agnostic to how it
is invoked.
 
### Tier 2 Input Validation
 
The Lambda handler performs synchronous validation before any AWS API call
is made or any log entry is written:
 
- `prompt` must be present and must be a string type
- `prompt` must not exceed 4,000 characters
Requests that fail either check are rejected immediately with a `400`
response. This bounds token costs and prevents malformed input from
reaching Bedrock. No audit log entry is written for rejected requests —
they never enter the pipeline.
 
### Tier 3 Audit Logging (Request)
 
Immediately after validation and before the Bedrock call, the handler
writes a structured JSON log entry to CloudWatch:
 
```json
{
  "event": "inference_request",
  "request_id": "<lambda-request-id>",
  "timestamp": "<iso8601-utc>",
  "model_id": "<model-arn-fragment>",
  "prompt_length": 42,
  "prompt_preview": "<first-100-chars>"
}
```
 
Logging before the external call is deliberate. If Bedrock is unavailable
or returns an error, a record of the inbound request still exists. The
`request_id` is Lambda's own invocation ID — it is the correlation key
that links this entry to the response entry written in Tier 5.
 
Full prompt text is intentionally not logged. Only the first 100 characters
are retained as `prompt_preview`. This is a data minimization control
aligned to NIST SI-12 — callers may embed PII or sensitive content in
prompts, and the log store may have broader read access than the
application itself.
 
### Tier 4 Bedrock Inference
 
The handler calls `bedrock:InvokeModel` against the configured foundation
model (Claude 3 Haiku by default). The request body follows the Anthropic
Messages API schema required by Bedrock:
 
- `anthropic_version` required versioning field for the Bedrock runtime
- `max_tokens: 512` caps response length, bounding latency and cost
- `messages` single-turn user message containing the validated prompt
The Lambda execution role is authorized to call `bedrock:InvokeModel`
against exactly one model ARN. No other Bedrock actions are permitted.
No other model ARNs are accessible. This is enforced at the IAM layer,
not the application layer — the function could not invoke a different
model even if the code were modified to attempt it.
 
### Tier 5 Audit Logging (Response)
 
After a successful Bedrock response, the handler writes a second structured
log entry to CloudWatch:
 
```json
{
  "event": "inference_response",
  "request_id": "<same-lambda-request-id>",
  "timestamp": "<iso8601-utc>",
  "model_id": "<model-arn-fragment>",
  "response_length": 198,
  "input_tokens": 12,
  "output_tokens": 44
}
```
 
The shared `request_id` between Tier 3 and Tier 5 entries satisfies NIST
AU-3's requirement for a correlation identifier linking related audit events.
Token counts serve two purposes: cost attribution (Bedrock charges per token)
and anomaly detection (unusually high output token counts may indicate
prompt injection producing verbose responses).
 
Response text is not logged, consistent with the data minimization approach
established in Tier 3.
 
### Tier 6 Error Handling
 
Three error conditions are caught explicitly and each produces a structured
`inference_error` log entry before returning to the caller:
 
**AccessDeniedException** `NIST AC-3, AC-6`
Indicates the execution role lacks permission to invoke the model — either
the IAM policy is misconfigured or Bedrock model access has not been enabled
in the account. Returns `403` to the caller.
 
**ThrottlingException**
Indicates Bedrock has rate-limited the request. Returns `429` to the caller,
signaling that a retry with backoff is appropriate.
 
**Exception (catch-all)**
Captures any unexpected failure. Logs the exception class name and message.
Returns `500` to the caller with the `request_id` for log correlation.
 
Every error path logs before returning. No invocation fails silently. Failed
invocations are fully visible in CloudWatch alongside successful ones.
 
---
 
## Production Considerations
 
This implementation is optimized for learning and demonstration purposes.
A production or FedRAMP-authorized deployment would incorporate the
following changes:
 
| Component | Demo Configuration | Production Configuration |
|---|---|---|
| Caller authentication | Any principal with `lambda:InvokeFunction` | API Gateway with IAM SigV4, Cognito, or Lambda authorizer |
| Network boundary | Lambda in AWS-managed environment, public internet to Bedrock | Lambda in VPC with Bedrock VPC endpoint |
| Log encryption | CloudWatch default encryption | KMS customer-managed key on log group |
| Log retention | 30 days | 90+ days per NIST AU-11 |
| Input validation | Length cap and type check | Maximum length enforcement, injection pattern detection, structured error responses with correlation IDs |
| Terraform state | Local `terraform.tfstate` | Remote backend (S3 + DynamoDB lock) with restricted bucket access |
| Prompt logging | 100-character preview | Decision based on data classification with full logging if prompts are confirmed non-sensitive, enabling Logs Insights queries |
| Model access | Single model ARN | Same least-privilege IAM scoping is already production-appropriate |
 
---