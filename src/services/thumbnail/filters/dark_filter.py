import cv2


class DarkFilter:

    def __init__(self, threshold=20):

        self.threshold = threshold

    def keep(self, image_path):

        image = cv2.imread(str(image_path))

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        brightness = gray.mean()

        return brightness >= self.threshold