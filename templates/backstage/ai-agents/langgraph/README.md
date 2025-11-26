# Strands Agent with AWS Secrets Manager

## AWS Secrets Manager Utility

The `utils.py` module provides a simple interface to fetch secrets from AWS Secrets Manager.

### Quick Start

```python
from utils import get_secret, get_secret_field, SecretsManager

# Method 1: Get entire secret (returns dict if JSON, string otherwise)
config = get_secret("my-app/config")
api_key = config["api_key"]
database_url = config["database_url"]

# Method 2: Get specific field from JSON secret
api_key = get_secret_field("my-app/config", "api_key")
db_password = get_secret_field("my-app/config", "db_password", default="")

# Method 3: Use SecretsManager class for multiple operations
secrets = SecretsManager(region_name="us-west-2")
llm_config = secrets.get_secret("my-app/llm-credentials")
db_config = secrets.get_secret("my-app/database")
```

### Usage Examples

#### Connecting to 3rd Party LLMs

```python
from utils import get_secret_field

# Get OpenAI API key
openai_key = get_secret_field("my-app/llm-config", "openai_api_key")

# Get Anthropic API key
anthropic_key = get_secret_field("my-app/llm-config", "anthropic_api_key")

# Use with your LLM client
import openai
openai.api_key = openai_key
```

#### Connecting to Databases

```python
from utils import get_secret

# Get database credentials
db_config = get_secret("my-app/database")

# Use with your database client
import psycopg2
conn = psycopg2.connect(
    host=db_config["host"],
    database=db_config["database"],
    user=db_config["username"],
    password=db_config["password"]
)
```

#### Connecting to External APIs

```python
from utils import get_secret_field
import httpx

# Get API credentials
api_key = get_secret_field("my-app/external-api", "api_key")
api_url = get_secret_field("my-app/external-api", "base_url")

# Make authenticated requests
async with httpx.AsyncClient() as client:
    response = await client.get(
        f"{api_url}/endpoint",
        headers={"Authorization": f"Bearer {api_key}"}
    )
```

### Secret Format in AWS Secrets Manager

Store your secrets as JSON for easy field access:

```json
{
  "api_key": "your-api-key-here",
  "database_url": "postgresql://user:pass@host:5432/db",
  "openai_api_key": "sk-...",
  "anthropic_api_key": "sk-ant-..."
}
```

### Error Handling

```python
from utils import get_secret

try:
    config = get_secret("my-app/config")
except Exception as e:
    print(f"Failed to retrieve secret: {e}")
    # Handle error appropriately
```

### IAM Permissions Required

Ensure your application has the following IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:region:account-id:secret:my-app/*"
    }
  ]
}
```
