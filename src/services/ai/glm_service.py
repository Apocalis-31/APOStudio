import base64
import json
import time

from openai import (
    OpenAI,
    RateLimitError,
    APITimeoutError
)

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
                timeout=180.0
            )

            self.debug(f"📝 Modèle texte  : {self.text_model}")
            self.debug(f"🖼️ Modèle vision : {self.vision_model}")

        def debug(self, message):

            print(message)

            if self.ui:
                self.ui.log(message)

        def log(self, message):

            if self.ui:
                self.ui.log(message)
            else:
                print(message)


        def _log_request(
            self,
            model,
            prompt_size,
            image_count=0,
            base64_size=0
        ):

            self.debug("══════════════════════════════")
            self.debug(f"🤖 Modèle       : {model}")
            self.debug(f"📝 Prompt       : {prompt_size:,} caractères")

            if image_count:

                self.debug(f"📸 Images       : {image_count}")
                self.debug(f"📦 Base64 total : {base64_size / 1024:.1f} Ko")

            self.debug("══════════════════════════════")


        def _log_success(
            self,
            elapsed,
            response
        ):

            self.debug(f"✅ Réponse reçue en {elapsed:.2f}s")

            if response:

                self.debug(
                    f"📥 Taille réponse : {len(response):,} caractères"
                )


        def _log_error(
            self,
            elapsed,
            error
        ):

            self.debug(
                f"❌ {type(error).__name__} après {elapsed:.2f}s"
            )

            self.debug(str(error))


        def _execute_request(
            self,
            model,
            messages,
            response_format=None
        ):
            """
            Envoie une requête à GLM avec retry automatique.

            Retourne toujours le texte brut de la réponse.
            """

            for attempt in range(self.MAX_RETRY):

                start = time.perf_counter()

                self.debug(
                    f"🚀 Tentative {attempt + 1}/{self.MAX_RETRY}"
                )

                try:

                    kwargs = {
                        "model": model,
                        "messages": messages,
                        "extra_body": {
                            "thinking": {
                                "type": "disabled"
                            }
                        }
                    }

                    if response_format is not None:
                        kwargs["response_format"] = response_format

                    response = self.client.chat.completions.create(
                        **kwargs
                    )

                    elapsed = time.perf_counter() - start

                    text = response.choices[0].message.content

                    self._log_success(
                        elapsed,
                        text
                    )

                    return text

                except RateLimitError as e:

                    elapsed = time.perf_counter() - start

                    self._log_error(
                        elapsed,
                        e
                    )

                    wait = (attempt + 1) * 10

                    if attempt < self.MAX_RETRY - 1:

                        self.debug(
                            f"🔄 Nouvelle tentative dans {wait} secondes..."
                        )

                        time.sleep(wait)

                        continue

                    raise Exception(
                        "GLM indisponible après plusieurs tentatives."
                    )

                except APITimeoutError as e:

                    elapsed = time.perf_counter() - start

                    self._log_error(
                        elapsed,
                        e
                    )

                    raise Exception(
                        "GLM n'a pas répondu avant le timeout."
                    )

                except Exception as e:

                    elapsed = time.perf_counter() - start

                    self._log_error(
                        elapsed,
                        e
                    )

                    raise


        def ask(self, prompt: str):

            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            self._log_request(
                model=self.text_model,
                prompt_size=len(prompt)
            )

            return self._execute_request(
                model=self.text_model,
                messages=messages
            )

        def ask_json(
            self,
            system_prompt,
            user_prompt
        ):

            total = len(system_prompt) + len(user_prompt)

            self._log_request(
                model=self.text_model,
                prompt_size=total
            )

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]

            text = self._execute_request(
                model=self.text_model,
                messages=messages,
                response_format={
                    "type": "json_object"
                }
            )

            print("===== RÉPONSE BRUTE =====")
            print(repr(text))
            print("=========================")

            return json.loads(text)


        def ask(
            self,
            prompt: str
        ):

            self._log_request(
                model=self.text_model,
                prompt_size=len(prompt)
            )

            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            return self._execute_request(
                model=self.text_model,
                messages=messages
            )


        def ask_vision(
            self,
            prompt,
            images
        ):

            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            total_size = 0

            for image in images[:5]:

                total_size += len(image["base64"])

                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image['base64']}"
                    }
                })

            self._log_request(
                model=self.vision_model,
                prompt_size=len(prompt),
                image_count=min(len(images), 5),
                base64_size=total_size
            )

            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]

            text = self._execute_request(
                model=self.vision_model,
                messages=messages,
                response_format={
                    "type": "json_object"
                }
            )


            print("===== RÉPONSE BRUTE =====")
            print(repr(text))
            print("=========================")

            return json.loads(text)


        def _build_vision_content(
            self,
            prompt,
            images
        ):

            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            total_size = 0

            for image in images[:5]:

                total_size += len(image["base64"])

                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image['base64']}"
                    }
                })

            return content, total_size


        