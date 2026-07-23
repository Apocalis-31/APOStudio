from pathlib import Path
import sys
import re


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from app_info import (
    APP_NAME,
    COMPANY,
    AUTHOR,
    COPYRIGHT,
    VERSION,
)


def version_tuple(version: str) -> str:
    """
    Convertit 1.0.1 -> 1,0,1,0
    """
    parts = version.split(".")

    while len(parts) < 4:
        parts.append("0")

    return ",".join(parts[:4])


VERSION_TEMPLATE = r"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', '{company}'),
          StringStruct('FileDescription', '{app_name}'),
          StringStruct('FileVersion', '{version}'),
          StringStruct('InternalName', '{app_name}'),
          StringStruct('OriginalFilename', '{app_name}.exe'),
          StringStruct('ProductName', '{app_name}'),
          StringStruct('ProductVersion', '{version}'),
          StringStruct('LegalCopyright', '{copyright}')
        ]
      )
    ]),
    VarFileInfo([
      VarStruct('Translation', [1036, 1200])
    ])
  ]
)
"""



def update_installer_version(root: Path):
    windows_version = VERSION + ".0"
    replacements = {
        "MyAppName": APP_NAME,
        "MyAppVersion": windows_version,
        "MyAppPublisher": COMPANY,
    }

    for iss_name in ["Apo Studio.iss", "Apo Studio CPU.iss"]:
        iss_file = root / "installer" / iss_name

        if not iss_file.exists():
            continue

        text = iss_file.read_text(encoding="utf-8")

        for key, value in replacements.items():
            text = re.sub(
                rf'(#define\s+{key}\s+)".*"',
                rf'\1"{value}"',
                text,
            )

        iss_file.write_text(text, encoding="utf-8")



def main():


    content = VERSION_TEMPLATE.format(
        app_name=APP_NAME,
        company=COMPANY,
        author=AUTHOR,
        copyright=COPYRIGHT,
        version=VERSION,
        version_tuple=version_tuple(VERSION)
    )

    output = Path("version_info.txt")

    output.write_text(
        content,
        encoding="utf-8"
    )
    update_installer_version(ROOT)


if __name__ == "__main__":
    main()

