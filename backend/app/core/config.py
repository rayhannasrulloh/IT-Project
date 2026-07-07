from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/conversational_analyst",
        description="Async database connection URL"
    )
    DATABASE_SYNC_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/conversational_analyst",
        description="Sync database connection URL for migrations and seeding"
    )
    GROQ_API_KEY: str = Field(..., description="API Key for Groq service")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, description="API Key for OpenRouter service")
    LLM_PROVIDER: str = Field(default="groq", description="LLM provider: 'groq' or 'openrouter'")
    OPENROUTER_MODEL: str = Field(default="tencent/hy3:free", description="OpenRouter model name")
    SUPABASE_URL: str = Field(..., description="Supabase API endpoint URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase anonymous client key")
    SUPABASE_JWT_SECRET: str = Field(..., description="JWT Secret to verify Supabase Auth tokens locally")
    ENVIRONMENT: str = Field(default="development", description="Current environment (development, production, testing)")
    
    SQL_GENERATION_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Groq model to generate SQL")
    EXPLANATION_MODEL: str = Field(default="llama-3-8b-8192", description="Groq model to generate explanations")
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://conversational-data-analyst.vercel.app"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

import os

# Resolve env_file path dynamically to work both on host and inside Docker container
_env_path = "c:\\Code\\IT-project\\backend\\.env"
if not os.path.exists(_env_path):
    _env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    if not os.path.exists(_env_path):
        _env_path = ".env"

settings = Settings(_env_file=_env_path)
