from services.workflow import workflow
from services.workflow.workflow import Workflow
from services.workflow.workflow_config import WorkflowConfig
import customtkinter as ctk

class WorkflowWindow(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        # Associer la fenêtre à APO Studio
        self.transient(master)

        # Fenêtre modale
        self.grab_set()

        # Premier plan
        self.lift()
        self.focus_force()

        self.title("Workflow - APO Studio")
        self.geometry("700x620")
        self.resizable(False, False)

        # ==========================
        # Variables
        # ==========================

        workflow = WorkflowConfig().load()

        self.youtube = ctk.BooleanVar(
                value=workflow.is_enabled("youtube")
            )

        self.thumbnail = ctk.BooleanVar(
                value=workflow.is_enabled("thumbnail")
            )
        
        self.vision = ctk.BooleanVar(
                value=workflow.is_enabled("vision")
        )

        self._all_modules = [
            ("youtube", self.youtube),
            ("thumbnail", self.thumbnail),
            ("vision", self.vision),
        ]

        # ==========================
        # Titre
        # ==========================

        title = ctk.CTkLabel(
            self,
            text="🔀 Workflow",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(25, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Configurez votre pipeline de création",
            font=("Segoe UI", 14)
        )
        subtitle.pack()

        ctk.CTkLabel(
            self,
            text="Workflow actuel : Personnalisé",
            font=("Segoe UI", 12),
            text_color="gray"
        ).pack(pady=(5, 20))

        # ==========================
        # Modules
        # ==========================

        self.add_module(
            "🤖 Génération YouTube",
            "Produit le youtube.json ainsi que l'intro.",
            self.youtube
        )

        self.add_module(
            "🎨 Miniature",
            "Extraction des images, sélection et génération.",
            self.thumbnail
        )

        self.add_module(
            "🧠 Sélection IA (GLM Vision)",
            "Analyse automatiquement les captures et sélectionne les meilleures. (Expérimental)",
            self.vision
        )

        # ==========================
        # Etat
        # ==========================

        self.status = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 12),
            text_color="gray"
        )

        self.status.pack(
            pady=(15, 20)
        )

        self._update_counter()

        # ==========================
        # Bouton
        # ==========================

        ctk.CTkButton(
            self,
            text="💾 Enregistrer",
            width=180,
            command=self.save
        ).pack(pady=(5, 25))

    # =====================================================

    def add_module(
        self,
        title,
        description,
        variable
    ):

        frame = ctk.CTkFrame(
            self,
            corner_radius=10
        )

        frame.pack(
            fill="x",
            padx=25,
            pady=6
        )

        left = ctk.CTkFrame(
            frame,
            fg_color="transparent"
        )

        left.pack(
            side="left",
            padx=15,
            pady=8,
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            left,
            text=title,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=description,
            font=("Segoe UI", 12),
            text_color="#AAAAAA"
        ).pack(anchor="w", pady=(3, 0))

        cb = ctk.CTkCheckBox(
            frame,
            text="Activer",
            variable=variable,
            command=self._update_counter
        ).pack(
            side="right",
            padx=18
        )

    def _update_counter(self):
        total = len(self._all_modules) + 1
        active = 1
        for _, var in self._all_modules:
            if var.get():
                active += 1
        self.status.configure(
            text=f"Modules actifs : {active} / {total}"
        )

    # =====================================================

    def save(self):

        workflow = Workflow()

        workflow.enabled = ["transcription"]

        if self.youtube.get():
            workflow.enabled.append("youtube")

        if self.thumbnail.get():
            workflow.enabled.append("thumbnail")

        if self.vision.get():
            workflow.enabled.append("vision")  

        WorkflowConfig().save(workflow)

        self.destroy()