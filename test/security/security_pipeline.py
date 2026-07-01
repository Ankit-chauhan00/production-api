from app.security import SecurityPipeline

pipeline = SecurityPipeline()

# you can enter your inputs
test_inputs = []

print("=" * 70)
print("INPUT SECURITY TESTS")
print("=" * 70)

for text in test_inputs:
    print(f"\nInput: {text}")

    allowed, cleaned, notes = pipeline.check_input(text)

    print(f"Allowed : {allowed}")
    print(f"Cleaned : {cleaned}")
    print(f"Notes   : {notes}")
