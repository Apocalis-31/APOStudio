import base64
import json
import time
from openai import APITimeoutError

from openai import OpenAI, RateLimitError

from services.config_service import ConfigService

class GLMService:

    MAX_RETRY = 5
    

    def __init__(self, ui=None):


        self.ui = ui

        config = ConfigService()

        self.text_model = config.get("glm.model")

        self.vision_model = config.get("glm.vision_model")

        self.client = OpenAI(
            api_key=config.get("glm.api_key"),
            base_url=config.get("glm.base_url"),
            timeout=60.0
        )


    def ask(self, prompt: str):

        try:

            response = self.client.chat.completions.create(
                model = self.text_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:

            return f"ERREUR GLM : {e}"        
    
            
    def ask_json(
        self,
        system_prompt,
        user_prompt
    ):
        
        self.debug("🤖 Connexion à GLM...")

        for attempt in range(self.MAX_RETRY):

            try:

                response = self.client.chat.completions.create(

                    model=self.text_model,

                    response_format={
                        "type": "json_object"
                    },

                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )

                self.debug("✅ Réponse GLM reçue")

                text = response.choices[0].message.content

                return json.loads(text)

            except RateLimitError:

                wait = (attempt + 1) * 10

                if attempt < self.MAX_RETRY - 1:

                    self.debug(f"⚠️ GLM surchargé (tentative {attempt + 1}/{self.MAX_RETRY})")

                    time.sleep(wait)

                    continue

                raise Exception(
                    "GLM indisponible après plusieurs tentatives."
                )
            except APITimeoutError:

                if self.ui:

                    self.ui.log("⏱️ GLM ne répond pas.")

                    self.ui.log(
                        "⚠️ Le serveur a dépassé le délai de 60 secondes."
                    )

                    self.ui.log(
                        "🔄 Réessayez dans quelques minutes."
                    )

                raise Exception(
                    "GLM n'a pas répondu après 60 secondes."
                )

    def ask_vision(
        self,
        prompt,
        images
    ):
        self.debug("➡️ Entrée dans ask_vision()")

        content = [
            {
                "type": "text",
                "text": prompt
            }
        ]

        for image in images[:5]:

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image['base64']}"
                }
            })


        for attempt in range(self.MAX_RETRY):

            try:

                self.debug("🚀 Création de la requête OpenAI")


                response = self.client.chat.completions.create(

                    model=self.vision_model,

                    response_format={
                        "type": "json_object"
                    },

                    messages=[
                        {
                            "role": "user",
                            "content": content
                        }
                    ]
                )

                if self.ui:
                    self.ui.log("📥 Réponse Vision reçue")

                text = response.choices[0].message.content

                return json.loads(text)

            except RateLimitError as e:

                wait = (attempt + 1) * 10

                if attempt < self.MAX_RETRY - 1:

                    if self.ui:

                        self.ui.log(
                            f"⏳ GLM est actuellement surchargé."
                        )

                        self.ui.log(
                            f"🔄 Nouvelle tentative dans {wait} secondes..."
                        )

                    time.sleep(wait)

                    continue

                raise Exception(
                    "GLM Vision indisponible après 5 tentatives."
                )
            
            except APITimeoutError:

                if self.ui:

                    self.ui.log("⏱️ GLM ne répond pas.")

                    self.ui.log(
                        "⚠️ Le serveur a dépassé le délai de 60 secondes."
                    )

                    self.ui.log(
                        "🔄 Réessayez dans quelques minutes."
                    )

                raise Exception(
                    "GLM n'a pas répondu après 60 secondes."
                )
            
            except Exception as e:

                if self.ui:
                    self.ui.log(f"❌ Erreur GLM Vision : {e}")

                raise

    def debug(self, message):

        print(message)

        if self.ui:
            self.ui.log(message)

    def log(self, message):

        if self.ui:
            self.ui.log(message)
        else:
            print(message)