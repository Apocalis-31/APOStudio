from pathlib import Path

from models.project import Project
from models.prompt import Prompt
from services.path_service import PathService


class PromptBuilder:

    USER_BLOCKS = [
        "creator.md",
        "intro.md",
        "thumbnail.md",
        "hook.md",
    ]

    def __init__(self):

        self.knowledge_path = PathService.knowledge()
        self.user_prompt_path = PathService.user_prompts()
        self.prompt_path = PathService.prompts()

    # =====================================================
    # YOUTUBE
    # =====================================================

    def build(
        self,
        project: Project,
        provider: str
    ):

        return Prompt(

            system=self.build_system(provider),

            user=self.build_user(project)

        )

    # =====================================================
    # SYSTEM
    # =====================================================

    def build_system(
        self,
        provider: str
    ):

        if provider == "ollama":

            return self.read_prompt(
                "youtube_prompt_ollama.md"
            )

        elif provider == "glm":

            return self.read_prompt(
                "youtube_prompt_glm.md"
            )

        return self.read_prompt(
            "youtube_prompt.md"
        )

    # =====================================================
    # USER
    # =====================================================

    def build_user(
        self,
        project: Project
    ):

        sections = []

        # -------------------------
        # Connaissances + Préférences
        # -------------------------

        for block in self.USER_BLOCKS:

            content = self.read_with_override(block)

            if content:

                sections.append(content)

        # -------------------------
        # Projet
        # -------------------------

        sections.append(
            self.build_project(project)
        )

        # -------------------------
        # Transcript
        # -------------------------

        sections.append(
            self.build_transcript(project)
        )

        return "\n\n".join(sections)

    # =====================================================
    # PROJECT
    # =====================================================

    def build_project(
        self,
        project: Project
    ):

        lines = [

            "# PROJECT",

            f"Name: {project.name}",

            f"Series: {project.series}",

            f"Episode: {project.episode if project.episode is not None else 'N/A'}",

            f"Video: {project.video_path.name}",

        ]

        return "\n".join(lines)

    # =====================================================
    # TRANSCRIPT
    # =====================================================

    def build_transcript(
        self,
        project: Project
    ):

        transcript = (
            project.project_path
            / "transcript.txt"
        )

        with open(
            transcript,
            "r",
            encoding="utf-8"
        ) as f:

            return (
                "# TRANSCRIPT\n\n"
                + f.read()
            )

    # =====================================================
    # SMART CUT
    # =====================================================

    def build_smart_cut(
        self,
        candidates,
        target
    ):

        system_prompt = self.read_prompt(
            "smart_cut_prompt.md"
        )

        user_sections = []

        user_sections.append(
            f"Objectif : {target:.1f} secondes"
        )

        user_sections.append(
            f"Nombre de candidats : {len(candidates)}"
        )

        for i, candidate in enumerate(
            candidates,
            start=1
        ):

            section = []

            section.append(
                f"--- Candidat {i} ---"
            )

            section.append(
                f"Timestamp : {candidate.timestamp:.1f}s"
            )

            section.append(
                f"Silence : {candidate.silence_duration:.1f}s"
            )

            section.append(
                f"Avant : {candidate.before_text}"
            )

            section.append(
                f"Après : {candidate.after_text}"
            )

            user_sections.append(
                "\n".join(section)
            )

        return Prompt(

            system=system_prompt,

            user="\n\n".join(user_sections)

        )

    # =====================================================
    # HELPERS
    # =====================================================

    def read_prompt(
        self,
        filename
    ):

        path = (
            self.prompt_path
            / filename
        )

        return path.read_text(
            encoding="utf-8"
        )

    def read_with_override(
        self,
        filename
    ):

        sections = []

        # -------------------------
        # Connaissances
        # -------------------------

        knowledge_file = (
            self.knowledge_path
            / filename
        )

        if knowledge_file.exists():

            content = knowledge_file.read_text(
                encoding="utf-8"
            ).strip()

            if content:

                sections.append(
                    content
                )

        # -------------------------
        # Préférences utilisateur
        # -------------------------

        user_file = (
            self.user_prompt_path
            / filename
        )

        if user_file.exists():

            content = user_file.read_text(
                encoding="utf-8"
            ).strip()

            if content:

                sections.append(
                    content
                )

        return "\n\n".join(
            sections
        )