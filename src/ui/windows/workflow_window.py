from services.workflow import workflow
from services.workflow.workflow import Workflow
from services.workflow.workflow_config import WorkflowConfig
import customtkinter as ctk

class WorkflowWindow(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("Workflow")
        self.geometry("700x620")
        self.resizable(False, False)
        self.grab_set()


        # ==========================
        # Variables
        # ==========================

        workflow = WorkflowConfig().load()

        self.transcription = ctk.BooleanVar(
                value=workflow.is_enabled("transcription")
            )

        self.youtube = ctk.BooleanVar(
                value=workflow.is_enabled("youtube")
            )

        self.thumbnail = ctk.BooleanVar(
                value=workflow.is_enabled("thumbnail")
            )
        
        self.vision = ctk.BooleanVar(
                value=workflow.is_enabled("vision")
)

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
            "🎙️ Transcription",
            "Analyse la vidéo et génère le transcript.",
            self.transcription
        )

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
            text="Modules actifs : 3 / 3",
            font=("Segoe UI", 12),
            text_color="gray"
        )

        self.status.pack(
            pady=(15, 20)
        )

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

        ctk.CTkCheckBox(
            frame,
            text="Activer",
            variable=variable
        ).pack(
            side="right",
            padx=18
        )

    # =====================================================

    def save(self):

        workflow = Workflow()

        workflow.enabled = []

        if self.transcription.get():
            workflow.enabled.append("transcription")

        if self.youtube.get():
            workflow.enabled.append("youtube")

        if self.thumbnail.get():
            workflow.enabled.append("thumbnail")

        if self.vision.get():
            workflow.enabled.append("vision")  

        print(workflow.enabled)          

        WorkflowConfig().save(workflow)

        self.destroy()