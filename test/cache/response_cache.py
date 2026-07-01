import time

from app.cache import ResponseCache   # Change this import


cache = ResponseCache(ttl_seconds=2)

print("=" * 60)
print("RESPONSE CACHE TESTS")
print("=" * 60)

# -------------------------------------------------
# Test 1 : Initial Cache Miss
# -------------------------------------------------
query = "What is Python?"

print("\nTEST 1: Initial Cache Miss")
print("-" * 40)

result = cache.get(query)

print("Query :", query)
print("Result:", result)

assert result is None

# -------------------------------------------------
# Test 2 : Store Response
# -------------------------------------------------

print("\nTEST 2: Store Response")
print("-" * 40)

response = "Python is a high-level programming language."

cache.set(query, response)

print("Stored response successfully.")

# -------------------------------------------------
# Test 3 : Cache Hit
# -------------------------------------------------

print("\nTEST 3: Cache Hit")
print("-" * 40)

result = cache.get(query)

print("Query :", query)
print("Result:", result)

assert result == response

# -------------------------------------------------
# Test 4 : Query Normalization
# -------------------------------------------------

print("\nTEST 4: Query Normalization")
print("-" * 40)

queries = [
    "what is python?",
    " WHAT IS PYTHON? ",
    "What Is Python?",
]

for q in queries:
    result = cache.get(q)
    print(f"{q!r} -> {result}")

    assert result == response

# -------------------------------------------------
# Test 5 : TTL Expiration
# -------------------------------------------------

print("\nTEST 5: TTL Expiration")
print("-" * 40)

print("Waiting 3 seconds...")

time.sleep(3)

result = cache.get(query)

print("Result after expiration:", result)

assert result is None

# -------------------------------------------------
# Test 6 : Cache Statistics
# -------------------------------------------------

print("\nTEST 6: Cache Statistics")
print("-" * 40)

print(cache.stats)

print("\nAll tests passed!")