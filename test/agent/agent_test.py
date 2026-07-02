from app.agent import ProductionAgent
from app.config import get_settings

print("=" * 60)
print("PRODUCTION AGENT TESTS")
print("=" * 60)

agent = ProductionAgent()

# -------------------------------------------------
# Test 1 : Configuration
# -------------------------------------------------

print("\nTEST 1: Configuration")
print("-" * 40)

settings = get_settings()

print("Primary Model :", settings.primary_model)
print("Fallback Model:", settings.fallback_model)
print("Max Retries   :", settings.max_retries)
print("Environment   :", settings.app_env)

assert settings.primary_model != ""
assert settings.fallback_model != ""
assert settings.max_retries > 0

print("Configuration Passed")

# -------------------------------------------------
# Test 2 : Graph Creation
# -------------------------------------------------

print("\nTEST 2: Graph Creation")
print("-" * 40)

assert agent.graph is not None

print("Graph successfully created.")
print("Graph Creation Passed")

# -------------------------------------------------
# Test 3 : Normal Invocation
# -------------------------------------------------

print("\nTEST 3: Agent Invocation")
print("-" * 40)

query = "What is LangGraph?"

result = agent.invoke(query)

print("Query:")
print(query)

print("\nResponse:")
print(result["response"])

print("\nMetadata:")
print(f"Model Used : {result['model_used']}")
print(f"Error      : {result['error']}")

assert isinstance(result, dict)
assert "response" in result
assert "model_used" in result
assert "error" in result

print("Invocation Passed")

# -------------------------------------------------
# Test 4 : Multiple Requests
# -------------------------------------------------

print("\nTEST 4: Multiple Requests")
print("-" * 40)

queries = [
    "What is Python?",
    "Explain LangChain.",
    "What is RAG?",
]

for i, query in enumerate(queries, start=1):
    result = agent.invoke(query)

    print(f"\nRequest {i}")
    print("Query :", query)
    print("Model :", result["model_used"])
    print("Response :", result["response"][:100], "...")

    assert result["response"]

print("Multiple Request Test Passed")

print("\nAll tests passed!")