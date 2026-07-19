import customtkinter as ctk


class ProcessingStatus(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="transparent"
        )

        self.steps = {}

        title = ctk.CTkLabel(
            self,
            text="⚙ Traitement",
            font=("Segoe UI", 16, "bold")
        )

        title.pack(
            anchor="w",
            pady=(0, 12)
        )

        labels = [
            ("project", "Création du projet"),
            ("whisper", "Transcription Whisper"),
            ("youtube", "Génération YouTube"),
            ("thumbnail", "Génération miniature"),
            ("save", "Sauvegarde")
        ]

        for key, text in labels:

            label = ctk.CTkLabel(
                self,
                text=f"○ {text}",
                anchor="w",
                font=("Segoe UI", 13)
            )

            label.pack(
                anchor="w",
                pady=2
            )

            self.steps[key] = label

    def set_step(self, current_step):

        order = [
            "project",
            "whisper",
            "youtube",
            "thumbnail",
            "save"
        ]

        labels = {
            "project": "Création du projet",
            "whisper": "Transcription Whisper",
            "youtube": "Génération YouTube",
            "thumbnail": "Génération miniature",
            "save": "Sauvegarde"
        }

        current_index = order.index(current_step)

        for index, key in enumerate(order):

            if index < current_index:

                icon = "✔"

            elif index == current_index:

                icon = "⏳"

            else:

                icon = "○"

            self.steps[key].configure(
                text=f"{icon} {labels[key]}"
            )