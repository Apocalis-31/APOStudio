import customtkinter as ctk

from ui.windows.settings_window import SettingsWindow
from ui.windows.workflow_window import WorkflowWindow
from ui.windows.tools_window import ToolsWindow
from ui.windows.help_window import HelpWindow
from ui.windows.ai_style_window import AIStyleWindow


class TopBar(ctk.CTkFrame):

    def __init__(self, master, home):

        super().__init__(
            master,
            fg_color="transparent"
        )

        self.home = home

        self.projects_button = ctk.CTkButton(
            self,
            text="📁",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#3A3A3A",
            font=("Segoe UI Emoji", 18),
            command=self.home.open_projects_folder
        )

        self.workflow_button = ctk.CTkButton(
            self,
            text="🔀",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#3A3A3A",
            font=("Segoe UI Emoji", 18),
            command=self.open_workflow
        )

        self.tools_button = ctk.CTkButton(
            self,
            text="🛠",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#3A3A3A",
            font=("Segoe UI Emoji", 18),
            command=self.open_tools
        )

        self.settings_button = ctk.CTkButton(
            self,
            text="⚙️",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#3A3A3A",
            font=("Segoe UI Emoji", 18),
            command=self.open_settings
        )

        self.help_button = ctk.CTkButton(
            self,
            text="❓",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#3A3A3A",
            font=("Segoe UI Emoji", 18),
            command=self.open_help
        )

        self.ai_style_button = ctk.CTkButton(
            self,
            text="🎭",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#3A3A3A",
            font=("Segoe UI Emoji", 18),
            command=self.open_ai_style
        )

        self.projects_button.pack(side="left", padx=8)
        self.workflow_button.pack(side="left", padx=8)
        self.ai_style_button.pack(side="left", padx=8)
        self.tools_button.pack(side="left", padx=8)
        self.settings_button.pack(side="left", padx=8)
        self.help_button.pack(side="left", padx=8)

    # ==================================================

    def open_settings(self):
        SettingsWindow(self.home)

    def open_workflow(self):
        WorkflowWindow(self.home)

    def open_tools(self):
        ToolsWindow(self.home, self.home)

    def open_help(self):
        HelpWindow(self.home)

    def open_ai_style(self):
        AIStyleWindow(self.home)
