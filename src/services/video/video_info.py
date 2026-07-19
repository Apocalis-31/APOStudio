import av


class VideoInfo:

    def get_duration(self, video_path):

        container = av.open(str(video_path))

        duration = float(container.duration / av.time_base)

        container.close()

        return duration