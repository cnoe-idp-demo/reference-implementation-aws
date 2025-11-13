from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from strands import Agent
from utils import get_secret, get_secret_field
import os

app = FastAPI(title="Strands Agent Server", version="1.0.0")

# Example: Initialize Strands agent with secrets from AWS Secrets Manager
# Option 1: Get entire secret as dict
# api_config = get_secret("my-app/api-config")
# api_key = api_config.get("api_key")

# Option 2: Get specific field from secret
# api_key = get_secret_field("my-app/api-config", "api_key")

strands_agent = Agent()

# Get the API key from AWS Secrets Manager
secrets_path = os.getenv("TENANT_SECRETS_PATH")
openai_api_key = get_secret_field(secrets_path, "OPENAI_API_KEY")
weather_api_key = get_secret_field(secrets_path, "WEATHER_API_KEY")
print(f"OpenAI API Key: {openai_api_key}")
print(f"Weather API Key: {weather_api_key}")


class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(
                status_code=400, 
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )

        result = strands_agent(user_message)
        response = {
            "message": result.message,
            "timestamp": datetime.utcnow().isoformat()
        }

        return InvocationResponse(output=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@app.get("/ping")
async def ping():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)