from assisted_editing.exceptions import RenderValidationError
from assisted_editing.models.render_job import RenderJob


class RenderValidator:
    """Vérifie qu'un RenderJob est valide avant son exécution."""

    def validate(
        self,
        render_job: RenderJob,
    ) -> None:

        if not render_job.master_video.exists():
            raise RenderValidationError(
                f"Le fichier master est introuvable : {render_job.master_video}"
            )

        output_directory = render_job.output_video.parent

        if not output_directory.exists():
            raise RenderValidationError(
                f"Le dossier de sortie est introuvable : {output_directory}"
            )

        if (
            render_job.introduction is not None
            and not render_job.introduction.path.exists()
        ):
            raise RenderValidationError(
                f"L'introduction est introuvable : {render_job.introduction.path}"
            )

        if (
            render_job.ending is not None
            and not render_job.ending.path.exists()
        ):
            raise RenderValidationError(
                f"L'ending est introuvable : {render_job.ending.path}"
            )

        for overlay in render_job.overlays:
            if not overlay.path.exists():
                raise RenderValidationError(
                    f"L'overlay est introuvable : {overlay.path}"
                )

        if render_job.fade_in < 0:
            raise RenderValidationError(
                "La durée du fade in ne peut pas être négative."
            )

        if render_job.fade_out < 0:
            raise RenderValidationError(
                "La durée du fade out ne peut pas être négative."
            )

        if (
            render_job.logo is not None
            and not render_job.logo.path.exists()
        ):
            raise RenderValidationError(
                f"Le logo est introuvable : {render_job.logo.path}"
            )