# import os
# from app.config import get_settings

# settings = get_settings()

# print("Settings:")
# print(settings.langsmith_project)
# print(settings.langsmith_tracing_v2)

# print("\nEnvironment:")
# print("LANGSMITH_TRACING =", os.getenv("LANGSMITH_TRACING"))
# print("LANGSMITH_TRACING_V2 =", os.getenv("LANGSMITH_TRACING_V2"))
# print("LANGSMITH_PROJECT =", os.getenv("LANGSMITH_PROJECT"))

from dotenv import load_dotenv

load_dotenv()

from langsmith import Client, traceable

client = Client()

print("Client:", client)

@traceable
def hello(name):
    return f"Hello {name}"

print(hello("Ankit"))

# Force any buffered traces to upload
client.flush()