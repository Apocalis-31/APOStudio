from enum import Enum


class ResourceType(Enum):
    """Type de ressource utilisable par le module de montage assisté."""

    INTRODUCTION = "introduction"
    ENDING = "ending"
    OVERLAY = "overlay"
    MUSIC = "music"