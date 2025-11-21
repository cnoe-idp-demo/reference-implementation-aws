from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from strands import Agent
import os
import base64
import logging
from strands.telemetry import StrandsTelemetry
from utils import get_secret, get_secret_field

app = FastAPI(title="Strands Agent Server", version="1.0.0")

# Get the API key from AWS Secrets Manager
openai_secret = os.getenv("OPENAI_API_SECRET")
if openai_secret:
    openai_api_key = get_secret(openai_secret)
    print(f"OpenAI API Key: {openai_api_key}")

# Get Agent details
agent_name = os.getenv("AGENT_NAME", "AIP POC Agent")
agent_env = os.getenv("AGENT_ENV", "Dev")
print(f"Agent Name: {agent_name}, Agent Environment: {agent_env}")

# Get Langfuse keys from secret manager
langfuse_secret = os.getenv("LANGFUSE_API_SECRET")
public_key = get_secret_field(langfuse_secret, "PUBLIC_KEY")
secret_key = get_secret_field(langfuse_secret, "SECRET_KEY")

# Get keys for your project from the project settings page: https://cloud.langfuse.com
os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
os.environ["LANGFUSE_SECRET_KEY"] = secret_key
os.environ["LANGFUSE_BASE_URL"] = "https://us.cloud.langfuse.com"
 
# Build Basic Auth header.
LANGFUSE_AUTH = base64.b64encode(
    f"{public_key}:{secret_key}".encode()
).decode()
 
# Configure OpenTelemetry endpoint & headers
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.environ.get("LANGFUSE_BASE_URL") + "/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"


# Configure the telemetry
# (Creates new tracer provider and sets it as global)
strands_telemetry = StrandsTelemetry().setup_otlp_exporter()

# Initialize Strands agent with OpenAI model
strands_agent = Agent()

class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

# System Prompt
system_prompt = """
You are a helpful and smart assistant to answer user queries related to technology and tools.
"""

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    try:
        session_id = request.input.get("session_id", "abc-001")
        user_id = request.input.get("user_id", "default_user")
        user_message = request.input.get("prompt", "")
        print(f"session_id: {session_id}, user_id: {user_id}, user_message: {user_message}")
        if not user_message:
            raise HTTPException(
                status_code=400, 
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )
        
        trace_attr = {
            "session.id": session_id,
            "user.id": user_id,
            "langfuse.tags": [
                "Agent-SDK-Example",
                "Strands-Project-Demo",
                "Observability-Tutorial"
            ]
        }

        print(f"trace_attr: {trace_attr}")

        result = strands_agent(
            user_message,
            system_prompt=system_prompt,
            trace_attributes={
                "session.id": "abc-1234", # Example session ID
                "user.id": "mmaroth@amazon.com", # Example user ID
                "langfuse.tags": [
                    "Agent-SDK-Example",
                    "Strands-Project-Demo",
                    "Observability-Tutorial"
                ]
            }
        )
        
        response = {
            "message": result.message,
            "timestamp": datetime.utcnow().isoformat()
        }

        return InvocationResponse(output=response)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@app.get("/ping")
async def ping():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)