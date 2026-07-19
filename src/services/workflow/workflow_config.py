import json

from services.path_service import PathService
from services.workflow.workflow import Workflow


DEFAULT_WORKFLOW = {
    "enabled": [
        "transcription",
        "youtube",
        "thumbnail",
        "vision"
    ]
}


class WorkflowConfig:

    def __init__(self):

        self.path = (
            PathService.config()
            / "workflow.json"
        )

        if not self.path.exists():
            self.create_default_workflow()


    def create_default_workflow(self):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                DEFAULT_WORKFLOW,
                f,
                indent=4,
                ensure_ascii=False
            )


    def load(self):

        workflow = Workflow()

        with open(
            self.path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        workflow.enabled = data.get("enabled", [])

        return workflow


    def save(self, workflow: Workflow):

        data = {
            "enabled": workflow.enabled
        }

        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )