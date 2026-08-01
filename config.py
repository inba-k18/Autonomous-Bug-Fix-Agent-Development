import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Directory Paths
UPLOADS_DIR = BASE_DIR / "uploads"
TESTS_DIR = BASE_DIR / "tests"
REPORTS_DIR = BASE_DIR / "reports_output"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base" / "python_docs"
VECTOR_STORE_DIR = BASE_DIR / "chroma_db"

# Create directories if they do not exist
for directory in [UPLOADS_DIR, TESTS_DIR, REPORTS_DIR, KNOWLEDGE_BASE_DIR, VECTOR_STORE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys & LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "models/text-embedding-004")

# Analysis Thresholds
MAX_FUNCTION_LENGTH = 30
CYCLOMATIC_COMPLEXITY_THRESHOLD = 10
