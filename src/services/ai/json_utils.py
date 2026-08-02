import json
import re


def parse_json_response(text, context="réponse IA"):

    if not isinstance(text, str):

        return text

    cleaned = text.strip()

    # Retire les blocs de code markdown (```json ... ```)
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:

        return json.loads(cleaned)

    except json.JSONDecodeError:

        pass

    # L'IA ajoute parfois du texte après le JSON -> lit le premier
    # objet / tableau valide et ignore ce qui suit
    decoder = json.JSONDecoder()

    for start in (
        cleaned.find("{"),
        cleaned.find("[")
    ):

        if start == -1:

            continue

        try:

            value, _ = decoder.raw_decode(cleaned[start:])

            return value

        except json.JSONDecodeError:

            continue

    raise ValueError(
        f"Impossible de lire la {context} : {text[:200]}"
    )
