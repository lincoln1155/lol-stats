import os

# Define environment variables before app modules are imported
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres" # Using dummy url because postgres driver might complain about sqlite+aiosqlite
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["GEMINI_API_KEY"] = "fake-api-key"
os.environ["RIOT_API_KEY"] = "fake-riot-key"
