
# One-off calibration script for TOPIC_CHANGE_SIMILARITY_THRESHOLD in app/classifier/stage_gate.py. Run locally against the real embedding
#model (requires Ollama + nomic-embed-text running).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.llm.ollama_clients import embedding_model


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


SAME_TOPIC_PAIRS = [
    (
        "My presentation is on Friday, and the audience questions worry me.",
        "I think I will go blank, and I feel nervous.",
    ),  # START-01 T2 -> T3
    (
        "I think I will go blank, and I feel nervous.",
        "I avoid practising the questions because I am scared of freezing.",
    ),  # START-01 T3 -> T4
    (
        "The group did not reply to my message, and I felt left out.",
        "I thought they did not want me on the team.",
    ),  # EXPLORE-01 T1 -> T2
    (
        "I still think their silence means they do not want me there.",
        "It fits because nobody replied, but I know they had exams. They may have been busy.",
    ),  # REFLECT-01 T1 -> T2
    (
        "Alex interrupted me in our project meeting. I am upset.",
        "I felt ignored when Alex spoke over my part of the project.",
    ),  # START-02 T1 -> T4 (same topic, corrected relationship)
]

DIFFERENT_TOPIC_PAIRS = [
    (
        "Thinking of Friday makes me nervous because I might go blank.",
        "I would rather talk about my friend cancelling dinner.",
    ),  # EXPLORE-02 T1 -> T2 (decline wording stripped out)
    (
        "My presentation is on Thursday. I know my slides, but questions from the audience make me nervous.",
        "My friend cancelled our visit. I'm disappointed because I was looking forward to seeing her.",
    ),  # MWB-806-S01 T1 vs MWB-806-S03 T1
    (
        "The worry is still here, I just want to say that.",
        "Maybe the cancellation means she does not care.",
    ),  # FINISH-02 T2 vs REFLECT-02 T1
]


def main():
    print("=== Same-topic pairs (want HIGH similarity) ===")
    same_scores = []
    for a, b in SAME_TOPIC_PAIRS:
        emb_a = embedding_model.get_text_embedding(a)
        emb_b = embedding_model.get_text_embedding(b)
        score = cosine_similarity(emb_a, emb_b)
        same_scores.append(score)
        print(f"{score:.4f}  |  {a[:50]!r} <-> {b[:50]!r}")

    print("\n=== Different-topic pairs (want LOW similarity) ===")
    diff_scores = []
    for a, b in DIFFERENT_TOPIC_PAIRS:
        emb_a = embedding_model.get_text_embedding(a)
        emb_b = embedding_model.get_text_embedding(b)
        score = cosine_similarity(emb_a, emb_b)
        diff_scores.append(score)
        print(f"{score:.4f}  |  {a[:50]!r} <-> {b[:50]!r}")

    print("\n=== Summary ===")
    print(f"Same-topic:      min={min(same_scores):.4f}  max={max(same_scores):.4f}")
    print(f"Different-topic: min={min(diff_scores):.4f}  max={max(diff_scores):.4f}")

    if min(same_scores) > max(diff_scores):
        suggested = (min(same_scores) + max(diff_scores)) / 2
        print(f"\nClean separation. Suggested threshold: {suggested:.4f}")
    else:
        print(
            "\nNo clean separation - same-topic and different-topic scores overlap. "
            "A single previous-message similarity check may not be reliable enough; "
            "consider comparing against more than one prior turn, or review whether "
            "nomic-embed-text distinguishes these topics well enough at all."
        )


if __name__ == "__main__":
    main()