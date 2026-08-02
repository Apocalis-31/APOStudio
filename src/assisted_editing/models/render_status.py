from enum import Enum


class RenderStatus(str, Enum):

    PENDING = "pending"

    RENDERING = "rendering"

    COMPLETED = "completed"

    FAILED = "failed"