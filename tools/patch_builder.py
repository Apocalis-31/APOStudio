import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFESTS_DIR = ROOT / "manifests"


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def generate(dist_dir: Path, version: str) -> Path:
    files = {}
    for file in sorted(dist_dir.rglob("*")):
        if file.is_file():
            rel = str(file.relative_to(dist_dir)).replace("\\", "/")
            files[rel] = {
                "size": file.stat().st_size,
                "hash": file_hash(file),
            }

    MANIFESTS_DIR.mkdir(exist_ok=True)
    output = MANIFESTS_DIR / f"manifest_v{version}.json"
    output.write_text(json.dumps(files, indent=2), encoding="utf-8")
    return output


def diff(old_version: str, new_version: str) -> dict:
    old_file = MANIFESTS_DIR / f"manifest_v{old_version}.json"
    new_file = MANIFESTS_DIR / f"manifest_v{new_version}.json"

    if not old_file.exists():
        raise FileNotFoundError(f"Manifest {old_file} not found")
    if not new_file.exists():
        raise FileNotFoundError(f"Manifest {new_file} not found")

    old = json.loads(old_file.read_text(encoding="utf-8"))
    new = json.loads(new_file.read_text(encoding="utf-8"))

    added = [f for f in new if f not in old]
    modified = [f for f in new if f in old and new[f]["hash"] != old[f]["hash"]]
    removed = [f for f in old if f not in new]

    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "changed": added + modified,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        result = diff(sys.argv[1], sys.argv[2])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python patch_builder.py <old_version> <new_version>")
