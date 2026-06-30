
uv run python -c "
import sys
print(f'Python Version: {sys.version}')
print('Python is working!')
"


uv run python -c "
from dotenv import load_dotenv
import os

load_dotenv()

print('GOOGLE_API_KEY:', bool(os.getenv('GOOGLE_API_KEY')))
print('LANGSMITH_API_KEY:', bool(os.getenv('LANGSMITH_API_KEY')))
"


uv run python -c "
from app.config import get_settings

settings = get_settings()

print(f'Environment: {settings.app_env}')
print(f'Primary model: {settings.primary_model}')
print(f'Rate limit: {settings.rate_limit}')
print(f'Cache TTL: {settings.cache_ttl_seconds}')
print(f'Max retries: {settings.max_retries}')
print(f'Production: {settings.is_production}')
print('Config loaded successfully!')
"

uv run python -c "
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

response = llm.invoke('Say hello')

print(response.content)
"

uv run python -c "
from langsmith import Client

client = Client()

print('Connected to LangSmith!')
"


uv run python -c "
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))

print('Connected to PostgreSQL!')
conn.close()
"

