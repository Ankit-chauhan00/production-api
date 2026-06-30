from app.config import Settings


"""Use uv run python test/config_test.py"""

print("=" * 50)
print("Configuration")
print("=" * 50)

settings = Settings()

for key, value in settings.model_dump().items():
    print(f"{key}: {value}")

print("\n✅ Config loaded successfully")