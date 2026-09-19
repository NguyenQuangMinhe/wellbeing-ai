from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

from app import config

# generation model - Gemma4 E4B (used by generator.py)
generation_llm = Ollama(
    model=config.OLLAMA_GEMMA_MODEL,
    base_url=config.OLLAMA_BASE_URL,
    request_timeout=config.OLLAMA_REQUEST_TIMEOUT,
    keep_alive=config.OLLAMA_KEEP_ALIVE,
)

# embedding model - nomic-embed-text (used by retriever.py)
embedding_model = OllamaEmbedding(
    model_name=config.OLLAMA_EMBED_MODEL,
    base_url=config.OLLAMA_BASE_URL,
    keep_alive=config.OLLAMA_KEEP_ALIVE,
)

# classification model - Llama Guard 3 (used by output_check.py, intent_classifier.py based on future testing)
llama_guard = Ollama(
    model=config.OLLAMA_LLAMAGUARD_MODEL,
    base_url=config.OLLAMA_BASE_URL,
    request_timeout=config.OLLAMA_REQUEST_TIMEOUT,
    keep_alive=config.OLLAMA_KEEP_ALIVE
)

# note: only use .complete() or .chat(), never .stream_complete() or .stream_chat() becuase the output guardrail 
# required checking the whole response. If streaming is enabled, the response will be incomplete and the guardrail will not work as intended.