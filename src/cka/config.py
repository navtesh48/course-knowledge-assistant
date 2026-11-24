import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cka:cka@localhost:5432/cka")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
INBOX_DIR = os.getenv("INBOX_DIR", "./docs_inbox")
CHUNK_CHARS = int(os.getenv("CHUNK_CHARS", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "5"))
