from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_aws import ChatBedrock
from os import getenv


def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


def web_search(query: str) -> str:
    """Search the web for the given query."""
    return (
        "Here are the headcounts for each of the FAANG companies in 2024:\n"
        "1. **Facebook (Meta)**: 67,317 employees.\n"
        "2. **Apple**: 164,000 employees.\n"
        "3. **Amazon**: 1,551,000 employees.\n"
        "4. **Netflix**: 14,000 employees.\n"
        "5. **Google**: 181,269 employees."
    )

# Initialize Bedrock Claude
model_id = getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
region = getenv("AWS_REGION", "us-west-2")

model = ChatBedrock(
    model_id=model_id,
    region_name=region,
    model_kwargs={
        "temperature": 0.7,
        "max_tokens": 1024,
    }
)

# Create specialised agents for math
math_agent = create_react_agent(
    model=model,
    tools=[add, subtract, multiply],
    name="Math Agent",
    prompt="You are a math expert. Always use one tool at a time."
)

# Create specialised agents for web search
web_search_agent = create_react_agent(
    model=model,
    tools=[web_search],
    name="Web Search Agent",
    prompt="You are a web search expert. Always use one tool at a time. Do not do any math."
)

# Supervisor prompt
supervisor_prompt = (
    "You are a team supervisor managing a research expert and a math expert.\n"
    "For current events, use research_expert.\n"
    "For math problems, use math_expert."
)

# Create the supervisor workflow
supervisor = create_supervisor(
    [web_search_agent, math_agent],
    model=model,
    output_mode="last_message",
    prompt=supervisor_prompt,
)

# Compile the graph
app = supervisor.compile()