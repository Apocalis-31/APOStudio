from dataclasses import dataclass


@dataclass
class UpdateInfo:
    current_version: str
    latest_version: str
    has_update: bool

    release_name: str = ""
    download_url: str = ""
    release_notes: str = ""
    is_gpu: bool = False
    is_patch: bool = False
