from datetime import datetime, timedelta

class SessionStatistics:

    def __init__(self):

        self.total_videos = 0
        self.finished_videos = 0
        self.total_processing_time = 0

    # =====================================

    def add_video(self):

        self.total_videos += 1

    # =====================================

    def finish_video(self):

        self.finished_videos += 1

    # =====================================

    @property
    def waiting_videos(self):

        return max(
            self.total_videos - self.finished_videos,
            0
        )
    
    # =====================================

    def add_processing_time(self, seconds):

        self.total_processing_time += seconds


    # =====================================


    @property
    def average_processing_time(self):

        if self.finished_videos == 0:
            return 0

        return self.total_processing_time / self.finished_videos
    
    # =====================================


    @property
    def remaining_processing_time(self):

        return (
            self.waiting_videos
            * self.average_processing_time
        )

    # =====================================


    @property
    def estimated_end_time(self):

        remaining = self.remaining_processing_time

        if remaining <= 0:
            return None

        return datetime.now() + timedelta(
            seconds=remaining
        )
        
