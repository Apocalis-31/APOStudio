import customtkinter as ctk


class SessionStatus(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="transparent"
        )

        # ==============================
        # Titre
        # ==============================

        self.title = ctk.CTkLabel(
            self,
            text="🗂️ Session",
            font=("Segoe UI", 16, "bold")
        )

        self.title.pack(
            anchor="w",
            pady=(0, 15)
        )

        # ==============================
        # Statistiques
        # ==============================

        self.elapsed_value = self.create_stat(
            "⏱ Temps",
            "00:00"
        )

        self.remaining_value = self.create_stat(
            "⏳ Restant",
            "Calcul..."
        )

        self.progress_value = self.create_stat(
            "🎬 Progression",
            "0 / 0"
        )

        self.queue_value = self.create_stat(
            "📚 En attente",
            "0"
        )

        self.end_value = self.create_stat(
            "🏁 Fin",
            "--:--"
        )


    # ===========================================
    # Création d'une ligne de statistique
    # ===========================================

    def create_stat(self, title, value):

        line = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        line.pack(
            fill="x",
            pady=4
        )

        label = ctk.CTkLabel(
            line,
            text=title,
            font=("Segoe UI", 13)
        )

        value_label = ctk.CTkLabel(
            line,
            text=value,
            font=("Segoe UI", 13, "bold")
        )

        label.pack(
            side="left"
        )

        value_label.pack(
            side="right"
        )

        return value_label
    
    def set_elapsed(self, seconds):

        minutes = int(seconds // 60)
        seconds = int(seconds % 60)

        text = f"{minutes:02}:{seconds:02}"


        self.elapsed_value.configure(
            text=text
        )

    def set_progress(self, current, total):

        self.progress_value.configure(
            text=f"{current} / {total}"
        )


    def set_queue(self, count):

        self.queue_value.configure(
            text=str(count)
        )

    def set_average(self, seconds):

        if seconds <= 0:

            self.remaining_value.configure(
                text="Calcul..."
            )

            return

        minutes = int(seconds // 60)

        self.remaining_value.configure(
            text=f"{minutes} min"
        )

    def set_remaining(self, seconds):

        if seconds <= 0:

            self.remaining_value.configure(
                text="Calcul..."
            )

            return

        minutes = int(seconds // 60)

        hours = minutes // 60
        minutes = minutes % 60

        if hours:

            text = f"{hours} h {minutes:02}"

        else:

            text = f"{minutes} min"

        self.remaining_value.configure(
            text=text
        )

    def set_end(self, end_time):

        if end_time is None:

            self.end_value.configure(
                text="--:--"
            )

            return

        self.end_value.configure(
            text=end_time.strftime("%H:%M")
        )