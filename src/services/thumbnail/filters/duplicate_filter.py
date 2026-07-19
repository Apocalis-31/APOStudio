import cv2


class DuplicateFilter:

    def __init__(self, threshold=3):

        self.threshold = threshold

    def keep(self, previous_image, current_image):

        image1 = cv2.imread(str(previous_image))
        image2 = cv2.imread(str(current_image))

        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        # Réduction importante
        gray1 = cv2.resize(gray1, (64, 36))
        gray2 = cv2.resize(gray2, (64, 36))

        # Suppression du bruit
        gray1 = cv2.GaussianBlur(gray1, (5, 5), 0)
        gray2 = cv2.GaussianBlur(gray2, (5, 5), 0)

        difference = cv2.absdiff(gray1, gray2)

        score = difference.mean()

        return score > self.threshold