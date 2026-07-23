import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def create_patch_zip(version: str, changed_files: list[str], dist_dir: Path) -> Path:

    output_dir = ROOT / "installer" / "output"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / f"APOStudio_Patch_v{version}.zip"

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in changed_files:
            src = dist_dir / f
            if src.exists():
                zf.write(src, f)
                print(f"  + {f} ({src.stat().st_size:,} bytes)")

    print(f"Patch zip: {output} ({output.stat().st_size:,} bytes)")
    return output


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python patch_packager.py <version> <file1> <file2> ...")
        sys.exit(1)

    version = sys.argv[1]
    changed_files = sys.argv[2:]

    if not changed_files:
        print("No changed files.")
        sys.exit(0)

    create_patch_zip(version, changed_files, ROOT / "dist" / "Apo Studio CPU")
