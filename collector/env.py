import os


SUMMARIZER_URL = os.getenv("SUMMARIZER_URL")
if not SUMMARIZER_URL:
    raise ValueError("SUMMARIZER_URL environment variable is not set.")
