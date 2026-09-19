import csv
import re
from pathlib import Path

KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"

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
    """Maps section_id -> stage, from coverage_map.csv."""
    lookup = {}
    with open(coverage_map_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lookup[row["section_id"]] = row["stage"]
    return lookup


def build_chunks() -> list[dict]:
    """Chunks all knowledge base files and attaches stage metadata."""
    stage_lookup = load_stage_lookup(KNOWLEDGE_BASE_DIR / "coverage_map.csv")

    all_chunks = []
    for filename in DOCUMENT_METADATA:
        chunks = chunk_markdown_file(KNOWLEDGE_BASE_DIR / filename)
        for chunk in chunks:
            chunk["stage"] = stage_lookup.get(chunk["section_id"], "cross-cutting")
            all_chunks.append(chunk)

    return all_chunks


if __name__ == "__main__":
    chunks = build_chunks()
    print(f"Total chunks: {len(chunks)}\n")
    for c in chunks:
        print(f"{c['section_id']} [{c['stage']}] — {c['title']}")
        print(f"  refs: {c['source_refs']}")