from app.security import PIIDetector
"""uv run python -m test.inputsanitizer_test"""

detector = PIIDetector()

print("=" * 60)
print("PII DETECTOR TESTS")
print("=" * 60)

test_cases = [
    "Hello, how are you?",

    "My email is john.doe@gmail.com",

    "Call me at 987-654-3210",

    "My SSN is 123-45-6789",

    "My card number is 4111-1111-1111-1111",

    "Email: alice@test.com Phone: 555-123-4567",

    "Contact me at bob@example.com or call 1234567890",

    "Email: admin@company.com SSN: 123-45-6789 Card: 4444 3333 2222 1111",
]

for text in test_cases:
    print("\n" + "-" * 60)
    print(f"Original : {text}")

    detected = detector.detect(text)

    if detected:
        print("Detected:")
        for pii_type, values in detected.items():
            print(f"  {pii_type}: {values}")
    else:
        print("Detected: None")

    masked = detector.mask(text)
    print(f"Masked   : {masked}")

print("\n✅ All PII detection tests completed.")