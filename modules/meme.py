from . import var
import math, cv2


class Meme(object):
    """
    Class representing the memes retrieved online by the Downloaders
    """
    def __init__(self, **kwargs):
        """
        Initialises a new meme object with the keyword arguments passed by the Downloader

        :param kargs: dict of the arguments of the meme
        """
        self.__dict__.update(kwargs)

        self.template_ID = None
        self.part_match = None
        self.match = None

        self.resized = list()
        self.image = None
        self._set_image()

    def _set_image(self):
        """
        Converts the bytes array downloaded by the Downloader in a readable image and resizes the image

        :return:
        """
        try:
            decoded = cv2.imdecode(self.np_array, cv2.IMREAD_COLOR)
            self.image = cv2.cvtColor(decoded, cv2.COLOR_BGR2HSV)
        except cv2.error:
            pass
        else:
            self._set_resized()

    def _set_resized(self):
        """
        Resizes the image into the two formats used for the primary and secondary search.
        Starts trying with the default width of the primary and secondary search and
        if they are too big for the given images goes down one step.

        :return:
        """
        height, width = self.image.shape[0:2]
        for i in [var.PRIMARY_SEARCH_LEVEL, var.SECONDARY_SEARCH_LEVEL]:
            while True:
                size = 2 ** i
                if size > width:
                    i -= 1
                    continue
                self.resized.append((cv2.resize(self.image, (size, math.ceil(height * size / width)), interpolation=cv2.INTER_AREA), i))
                break
