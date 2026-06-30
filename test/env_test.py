import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("Environment Variables")
print("=" * 50)

print(f"GOOGLE_API_KEY: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"LANGSMITH_API_KEY: {bool(os.getenv('LANGSMITH_API_KEY'))}")
print(f"DATABASE_URL: {bool(os.getenv('DATABASE_URL'))}")