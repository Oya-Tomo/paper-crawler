import os


COLLECTION_PERIOD = int(os.getenv("COLLECTION_PERIOD"))
if not COLLECTION_PERIOD:
    raise ValueError("COLLECTION_PERIOD environment variable is not set.")


SUMMARIZER_URL = os.getenv("SUMMARIZER_URL")
if not SUMMARIZER_URL:
    raise ValueError("SUMMARIZER_URL environment variable is not set.")
