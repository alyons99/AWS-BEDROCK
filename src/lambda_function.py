import json
import logging
import boto3
import os
from datetime import datetime, timezone

#for execution enviornment warm starts
logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
MODEL_ID = os.environ.get("MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

#lambda handler passes in the prompt and content
def lambda_handler(event, context):
    request_id = context.aws_request_id
    prompt = event.get("prompt", "")

    #basic input validation, prompt needs to be present and under 4k chars
    if not prompt or not isinstance(prompt, str):
        return {"statusCode": 400, "body": json.dumps({"error": "Missing or invalid 'prompt' field"})}

    if len(prompt) > 4000:
        return {"statusCode": 400, "body": json.dumps({"error": "Prompt exceeds maximum length of 4000 characters"})}

    #call logging w/ cw logs
    logger.info(json.dumps({
        "event": "inference_request",
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "prompt_length": len(prompt),
        "prompt_preview": prompt[:100]
    }))

    #bedrock call
    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}]
            })
        )

        result = json.loads(response["body"].read())
        output_text = result["content"][0]["text"]
        usage = result.get("usage", {})

        #response logging w/ cw logs
        logger.info(json.dumps({
            "event": "inference_response",
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_id": MODEL_ID,
            "response_length": len(output_text),
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens")
        }))

        return {
            "statusCode": 200,
            "body": json.dumps({
                "request_id": request_id,
                "response": output_text
            })
        }

    #error handling
    #access denied error returns error code
    except bedrock.exceptions.AccessDeniedException:
        logger.error(json.dumps({
            "event": "inference_error",
            "request_id": request_id,
            "error": "AccessDeniedException — check IAM role and Bedrock model access"
        }))
        return {"statusCode": 403, "body": json.dumps({"error": "Model access denied", "request_id": request_id})}

    #throttling error returns error code
    except bedrock.exceptions.ThrottlingException:
        logger.error(json.dumps({
            "event": "inference_error",
            "request_id": request_id,
            "error": "ThrottlingException"
        }))
        return {"statusCode": 429, "body": json.dumps({"error": "Rate limited by Bedrock", "request_id": request_id})}

    #All other errors are capture and logged with a catch all 500
    except Exception as e:
        logger.error(json.dumps({
            "event": "inference_error",
            "request_id": request_id,
            "error": type(e).__name__,
            "detail": str(e)
        }))
        return {"statusCode": 500, "body": json.dumps({"error": "Internal error", "request_id": request_id})}