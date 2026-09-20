import csv
import re
from pathlib import Path

import chromadb

from app.llm.ollama_clients import embedding_model

KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"
CHROMA_DIR = Path(__file__).parent.parent.parent / "data" / "chroma"

DOCUMENT_METADATA = {
    "01_cbt_principles.md": {"document_id": "KB-01"},
    "02_cbt_stages.md": {"document_id": "KB-02"},
    "03_scope_and_safety.md": {"document_id": "KB-03"},
}

SECTION_PATTERN = re.compile(
    r"^## (?P<section_id>KB-[\d.]+) \| (?P<title>.+)$",
    re.MULTILINE,
)


def chunk_markdown_file(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    doc_meta = DOCUMENT_METADATA[filepath.name]

    matches = list(SECTION_PATTERN.finditer(text))
    chunks = []

    for i, match in enumerate(matches):
        section_id = match.group("section_id")
        title = match.group("title")
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        body = re.sub(r"\n+-{3,}\s*$", "", body).strip()

        source_refs = ""
        citation_match = re.search(r"\[([^\[\]]+)\]\s*$", body)
        if citation_match:
            source_refs = citation_match.group(1)
            body = body[: citation_match.start()].strip()

        chunks.append({
            "section_id": section_id,
            "document_id": doc_meta["document_id"],
            "title": title,
            "text": body,
            "source_refs": source_refs,
        })

    return chunks


def load_stage_lookup(coverage_map_path: Path) -> dict[str, str]:
    lookup = {}
    with open(coverage_map_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lookup[row["section_id"]] = row["stage"]
    return lookup


def build_chunks() -> list[dict]:
    stage_lookup = load_stage_lookup(KNOWLEDGE_BASE_DIR / "coverage_map.csv")

    all_chunks = []
    for filename in DOCUMENT_METADATA:
        chunks = chunk_markdown_file(KNOWLEDGE_BASE_DIR / filename)
        for chunk in chunks:
            chunk["stage"] = stage_lookup.get(chunk["section_id"], "cross-cutting")
            all_chunks.append(chunk)

    return all_chunks


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(name="cbt_knowledge_base")


def ingest() -> int:
    """
    Chunks the knowledge base, embeds each chunk via nomic-embed-text,
    and upserts into the local ChromaDB collection. Uses section_id as
    the document ID, so re-running this is idempotent - a chunk with an
    existing ID is overwritten in place, not duplicated.
    """
    chunks = build_chunks()
    collection = get_collection()

    ids, documents, embeddings, metadatas = [], [], [], []
    for chunk in chunks:
        ids.append(chunk["section_id"])
        documents.append(chunk["text"])
        embeddings.append(embedding_model.get_text_embedding(chunk["text"]))
        metadatas.append({
            "document_id": chunk["document_id"],
            "title": chunk["title"],
            "stage": chunk["stage"],
            "source_refs": chunk["source_refs"],
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def query(text: str, n_results: int = 3):
    collection = get_collection()
    query_embedding = embedding_model.get_text_embedding(text)
    return collection.query(query_embeddings=[query_embedding], n_results=n_results)


if __name__ == "__main__":
    count = ingest()
    print(f"Ingested {count} chunks into ChromaDB at {CHROMA_DIR}\n")
    print(f"Collection count: {get_collection().count()}\n")

    test_queries = [
        "How should the AI respond when someone wants to end the conversation?",
        "What should happen if the AI detects a crisis?",
        "How does the AI help someone identify unhelpful thinking patterns?",
    ]

    for test_query in test_queries:
        print(f"Test query: {test_query!r}\n")
        results = query(test_query)
        for i, (doc_id, doc_text, meta) in enumerate(
            zip(results["ids"][0], results["documents"][0], results["metadatas"][0])
        ):
            print(f"  {i+1}. {doc_id} [{meta['stage']}] — {meta['title']}")
        print()