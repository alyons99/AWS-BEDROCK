| Control | Family | Implementation |
|---------|--------|----------------|
| AC-3  | Access Enforcement      | The Lambda role cannot call any action not explicitly listed in the policy |
| AC-6  | Least Privilege     | Actions scoped to a single ARN |
| CM-2  | Baseline Configuration | All infrastructure is declared in Terraform |
| CM-7  | Least Functionality | SG Lockdown removes 0.0.0.0/0 ingress rules |
| SI-12  | Information Management and Retention | Only first 100 characters of prompts is retained, limiting exposure |
| AU-2  | Audit Events        | Structured JSON logs, CloudWatch metric filters |
| AU-3  | Content of Audit Records | Each log entry includes: event type, timestamp, request ID, model ID, prompt length, and token counts |
| AU-9  | Audit Protection    | S3 versioning, blocked public access on audit bucket |
| AU-11 | Audit Record Retention | Log group is created by Terraform with an explicit 30-day retention policy |