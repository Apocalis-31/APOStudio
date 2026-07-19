from services.workflow.workflow import Workflow
from services.workflow.workflow_config import WorkflowConfig


class WorkflowManager:

    def __init__(
        self,
        forced_modules=None
    ):

        if forced_modules is None:

            self.workflow = WorkflowConfig().load()

        else:

            self.workflow = Workflow()

            self.workflow.enabled = forced_modules

    def enabled(self, module: str):

        return self.workflow.is_enabled(module)