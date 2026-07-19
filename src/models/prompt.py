from dataclasses import dataclass


@dataclass
class Prompt:

    system: str

    user: str