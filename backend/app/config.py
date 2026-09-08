import os 
from dotenv import load_dotenv

#read the env file
load_dotenv()

#get values from env with fallback defaults
API_PORT = int(os.getenv("API_PORT", 8000))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_GEMMA_MODEL = os.getenv("OLLAMA_GEMMA_MODEL", "gemma4:e4b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_LLAMAGUARD_MODEL = os.getenv("OLLAMA_LLAMAGUARD_MODEL", "llama-guard3:1b")
OLLAMA_REQUEST_TIMEOUT = int(os.getenv("OLLAMA_REQUEST_TIMEOUT", 60))
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "10m")