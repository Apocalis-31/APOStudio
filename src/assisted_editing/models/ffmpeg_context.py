from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class FFmpegContext:
    """
    Contexte de construction
    d'une commande FFmpeg.
    """

    # ==================================================
    # Sections de la commande
    # ==================================================

    inputs: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    maps: list[str] = field(default_factory=list)
    codecs: list[str] = field(default_factory=list)
    output: list[str] = field(default_factory=list)

    # ==================================================
    # Index des entrées
    # ==================================================

    master_index: int = -1
    intro_index: int = -1
    logo_index: int = -1
    outro_index: int = -1
    music_index: int = -1

    # ==================================================
    # Interne
    # ==================================================

    _next_input_index: int = 0

    # ==================================================

    def add_input(
        self,
        path: Path,
    ) -> int:
        """
        Ajoute une entrée FFmpeg
        et retourne son index.
        """

        index = self._next_input_index

        self.inputs.extend([

            "-i",
            str(path),

        ])

        self._next_input_index += 1

        return index