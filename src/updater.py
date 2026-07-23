import os
import sys
import time
import zipfile
import subprocess


def wait_for_exit(exe_path, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with open(exe_path, "rb"):
                pass
            return True
        except PermissionError:
            time.sleep(0.5)
    return False


def main():
    if len(sys.argv) < 3:
        return 1

    zip_path = sys.argv[1]
    app_dir = sys.argv[2]
    exe_name = sys.argv[3] if len(sys.argv) > 3 else "APO Studio.exe"
    exe_path = os.path.join(app_dir, exe_name)

    time.sleep(1)

    if not wait_for_exit(exe_path):
        return 1

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(app_dir)

    subprocess.Popen([exe_path])

    return 0


if __name__ == "__main__":
    sys.exit(main())
