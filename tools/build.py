from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent

PYINSTALLER_SPEC = "APO Studio.spec"

INNO_SETUP = (
    r"D:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

INSTALLER_SCRIPT = (
    ROOT / "installer" / "Apo Studio.iss"
)

def run_step(title: str, command: list[str]) -> None:

    start = time.perf_counter()

    result = subprocess.run(command, cwd=ROOT)

    if result.returncode != 0:
        sys.exit(result.returncode)

    elapsed = time.perf_counter() - start


def main():

    run_step(
        "Generate version information",
        [
            sys.executable,
            "tools/generate_version_info.py",
        ],
    )

    run_step(
        "Build executable",
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            PYINSTALLER_SPEC,
        ],
    )

    run_step(
        "Build installer",
        [
            INNO_SETUP,
            str(INSTALLER_SCRIPT),
        ],
    )



if __name__ == "__main__":
    main()