from pathlib import Path
from models.project import Project
from models.prompt import Prompt
from services.path_service import PathService

class PromptBuilder:

    def __init__(self):

        self.knowledge_path = PathService.knowledge()

        self.prompt_path = PathService.prompts()

    def build(self, project: Project, provider: str):



        # ==========================
        # SYSTEM
        # ==========================

        print(f"🧠 PromptBuilder : {provider}")

        if provider == "ollama":
            system_prompt = self.read_prompt("youtube_prompt_ollama.md")

        elif provider == "glm":
            system_prompt = self.read_prompt("youtube_prompt_glm.md")

        else:
            system_prompt = self.read_prompt("youtube_prompt.md")

        # ==========================
        # USER
        # ==========================

        user_sections = []

        if provider == "ollama":

            user_sections.append(self.read("channel.md"))
            user_sections.append(self.read("intro_style.md"))
            user_sections.append(self.read("personality.md"))

        else:

            user_sections.append(self.read("channel.md"))
            user_sections.append(self.read("personality.md"))
            user_sections.append(self.read("intro_style.md"))
            user_sections.append(self.read("thumbnail_style.md"))
            user_sections.append(self.read("forbidden.md"))
            user_sections.append(self.read("youtube_hook.md"))

            examples = self.knowledge_path / "examples"

            for file in sorted(examples.glob("*.md")):
                user_sections.append(
                    self.read(file.relative_to(self.knowledge_path))
                )

        # Transcript
        transcript = project.project_path / "transcript.txt"

        with open(transcript, "r", encoding="utf-8") as f:

            user_sections.append("# Transcript\n")
            user_sections.append(f.read())

        user_prompt = "\n\n".join(user_sections)


        return Prompt(
            system=system_prompt,
            user=user_prompt
        )
    

    def read(self, filename):

        path = self.knowledge_path / filename

        with open(path, "r", encoding="utf-8") as f:

            return f.read()



    def read_prompt(self, filename):

        path = self.prompt_path / filename

        with open(path, "r", encoding="utf-8") as f:

            return f.read()
        

        # ==========================
        # SMART CUT
        # ==========================

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

        for i, candidate in enumerate(candidates, start=1):

            section = []

            section.append(f"--- Candidat {i} ---")

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