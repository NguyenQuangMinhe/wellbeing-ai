import datetime
import shutil
from pathlib import Path

from app.rag.ingest import CHROMA_DIR

"""
Copies the current on-disk Chroma directory (CHROMA_DIR, as defined in
ingest.py) to a timestamped folder under eval/snapshots/, taken
immediately before any corpus-expansion or re-ingestion work (1101b).

This is the fallback if an expanded knowledge base is later found to
degrade relevance scores: restoring means deleting the live Chroma
directory and copying this snapshot back in its place, no
re-ingestion required.
"""

def snapshot_chroma(chroma_dir=CHROMA_DIR, dest_root=Path(__file__).parent / "snapshots"):
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    dest = Path(dest_root) / f"chroma_pre_expansion_{stamp}"
    shutil.copytree(chroma_dir, dest)
    return dest

if __name__ == "__main__":
    dest = snapshot_chroma()
    print(f"Snapshot written to {dest}")