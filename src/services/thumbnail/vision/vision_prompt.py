class VisionPrompt:

    def build(self, project):

        return {
            "system": self._system_prompt(),
            "user": self._user_prompt(project)
        }

    def _system_prompt(self):

        return """
Tu es un expert des miniatures YouTube Gaming.

Ton objectif est de choisir UNE seule image qui donnera le meilleur taux de clic.

Critères :

- sujet principal visible
- image nette
- bonne composition
- scène intéressante
- bonne lisibilité

À éviter :

- écran noir
- image floue
- menu
- HUD trop présent
- transition

Réponds uniquement en JSON.
"""

    def _user_prompt(self, project):

        return f"""
Jeu :

{project.series}

Choisis la meilleure image parmi celles fournies.

Les images sont présentées dans l'ordre.

La première image correspond à l'index 0.
La deuxième image correspond à l'index 1.
Et ainsi de suite.

Tu dois impérativement répondre avec un index existant.

Réponds uniquement avec cet objet JSON :

{{
    "best_index": 2,
    "score": 8.4,
    "reason": "...",
    "tags": [
        "facecam",
        "action",
        "bonne lumière"
    ]
}}

Exemple :

Image 0
Image 1
Image 2
Image 3

Si tu préfères l'image 2 :

{{
    "best_index": 2,
    "score": 9.1,
    "reason": "Le sujet principal est bien visible."
}}
"""