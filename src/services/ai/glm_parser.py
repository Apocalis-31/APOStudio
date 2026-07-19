import re


class GLMParser:

    @staticmethod
    def parse_index(value):

        if isinstance(value, int):
            return value

        if isinstance(value, str):

            value = value.strip().lower()

            # Cas : "3"
            if value.isdigit():
                return int(value)

            # Cas : image-3 / image3 / image 3
            match = re.search(r"\d+", value)

            if match:
                return int(match.group())

        raise Exception(
            f"Indice GLM invalide : {value}"
        )