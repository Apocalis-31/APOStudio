from queue import Queue


class UiBridge:

    def __init__(self):
        self.queue = Queue()

    def log(self, message):
        self.queue.put(("log", message))

    def progress(self, value):
        self.queue.put(("progress", value))

    def finish(self):
        self.queue.put(("finish", None))

    def error(self, message):
        self.queue.put(("error", message))

    def current_video(self, name):

        self.queue.put(
            ("current_video", name)
        )

    def current_video(self, name):
        self.queue.put(
            ("current_video", name)
        )

    def queue_update(self, current, waiting):


        self.queue.put(
            (
                "queue_update",
                {
                    "current": current,
                    "waiting": waiting
                }
            )
        )

    def step(self, step):

        self.queue.put(
            (
                "step",
                step
            )
        )
        
    # ==================================================
    # Session
    # ==================================================

    def session_started(self):


        self.queue.put(
            (
                "session_started",
                None
            )
        )

    def session_finished(self):

        self.queue.put(
            (
                "session_finished",
                None
            )
        )

    def video_added(self):

        self.queue.put(
            ("video_added", None)
        )


    def video_finished(self, duration):

        self.queue.put(
            (
                "video_finished",
                duration
            )
        )

    def queue_update_buttons(self, has_pending):

        self.queue.put(
            (
                "queue_update_buttons",
                has_pending
            )
        )