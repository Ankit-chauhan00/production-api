from app.security import OutputValidator

"""Command:- uv run python -m test.security.output_validator"""

validator = OutputValidator()

print("=" * 60)
print("OUTPUT VALIDATOR TESTS")
print("=" * 60)

test_cases = [
    # Safe response
    "LangChain is a framework for building LLM applications.",

    # Email leakage
    "You can contact me at john@gmail.com",

    # Phone leakage
    "Call me at 987-654-3210",

    # SSN leakage
    "The SSN is 123-45-6789",

    # Credit card leakage
    "Card: 4111-1111-1111-1111",

    # Harmful content
    "Here's how to hack a website.",

    # Password leakage
    "The password is admin123",

    # API key leakage
    "API_KEY=sk-123456789",

    # Mixed PII + harmful
    "Here's how to hack a server. Contact me at john@gmail.com",

    # Multiple PII
    (
        "Email: alice@test.com "
        "Phone: 555-123-4567 "
        "Card: 4444-3333-2222-1111"
    ),
]

for text in test_cases:
    print("\n" + "=" * 60)
    print("Original Output:")
    print(text)

    cleaned, warnings = validator.validate(text)

    print("\nValidated Output:")
    print(cleaned)

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"⚠️  {warning}")
    else:
        print("\nWarnings: None")

print("\n✅ Output validation tests completed.")