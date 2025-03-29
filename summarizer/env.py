import os


DATABASE_URL = os.getenv("DATABASE_URL", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL environment variable is not set.")
