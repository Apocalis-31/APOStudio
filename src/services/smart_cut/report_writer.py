from pathlib import Path

from services.smart_cut.models.episode_plan import (
    EpisodePlan
)


class ReportWriter:

    def write(
        self,
        project,
        plans: list[EpisodePlan]
    ):

        report = (
            project.project_path
            / "smart_cut_report.txt"
        )

        with open(
            report,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            )

            file.write(
                "SmartCut Report\n"
            )

            file.write(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )

            for plan in plans:

                file.write(
                    f"Episode {plan.index}\n"
                )

                file.write(
                    f"Début : {plan.start:.1f}s\n"
                )

                file.write(
                    f"Fin : {plan.end:.1f}s\n"
                )

                file.write(
                    f"Durée : {plan.duration:.1f}s\n"
                )

                file.write(
                    f"Cible : {plan.target:.1f}s\n"
                )

                if plan.candidate:

                    file.write(
                        f"Gap : {plan.candidate.timestamp:.1f}s\n"
                    )

                    file.write(
                        f"Silence : {plan.candidate.silence_duration:.1f}s\n"
                    )

                    file.write(
                        f"Score : {plan.candidate.score:.2f}\n"
                    )

                    file.write(
                        f"Raison : {plan.candidate.reason}\n"
                    )

                    file.write("\n")

                    file.write("Avant :\n")

                    file.write(
                        f"{plan.candidate.before_text}\n\n"
                    )

                    file.write("Après :\n")

                    file.write(
                        f"{plan.candidate.after_text}\n"
                    )

                    file.write("\n")

                    difference = (
                        plan.end
                        - plan.target
                    )

                    file.write(
                        f"Ecart : {difference:+.1f}s\n"
                    )
                else:

                    file.write(
                        "Gap : Fin de vidéo\n"
                    )

                file.write("\n")