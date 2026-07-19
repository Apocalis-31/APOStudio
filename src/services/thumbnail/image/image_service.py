class ImageService:

    def __init__(self, ui):

        self.ui = ui

    def generate(self, project, frame):

        self.ui.log("🎨 Génération de la miniature IA...")

        title = project.youtube["thumbnail"]["title"]

        prompt = project.youtube["thumbnail"]["prompt"]

        self.ui.log(title)
        
        self.ui.log(prompt)