# Dumps the assembled prompt for each of the four CBT stages using a fixd fake session so the output can be reproduced. 
# Chroma and Ollama NOT mocked; meant to be executed live against real knowledgebase and embedding model to reflect 
# authentic prompt assembly. 

### ENSURE OLLAMA RUNNING and CHroma Collection populated: E.g., python scripts/dump_stage_prompts.py > docs/706b-stage-prompt-dumps.txt
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.retriever import assemble_prompt, VALID_STAGES
import uuid

FIXED_USER_MESSAGE = "I've been feeling stressed about an upcoming deadline"

CONTEXT_WINDOW = 131072  # confirmed via generation_llm.metadata.context_window

OUTPUT_PATH = Path(__file__).parent.parent / "docs" / "706b-stage-prompt-dumps.txt"


def main():
    session_id = f"stage-dump-{uuid.uuid4()}"

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for stage in VALID_STAGES:
            prompt = assemble_prompt(session_id, FIXED_USER_MESSAGE, "low", stage)
            char_count = len(prompt)
            approx_tokens = char_count // 4
            pct_of_budget = (approx_tokens / CONTEXT_WINDOW) * 100

            f.write(f"\n{'=' * 80}\n")
            f.write(f"STAGE: {stage}\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(prompt)
            f.write(
                f"\n\n[char count: {char_count} | approx tokens (chars/4): {approx_tokens} "
                f"| ~{pct_of_budget:.2f}% of {CONTEXT_WINDOW}-token context window]\n"
            )

    print(f"Wrote dump to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()