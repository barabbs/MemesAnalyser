from . import var
import math, cv2


class Meme(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

        self.template_ID = None
        self.part_match = None
        self.match = None

        self.resized = list()
        self.image = None
        self._set_image()

    def _set_image(self):
        try:
            decoded = cv2.imdecode(self.np_array, cv2.IMREAD_COLOR)
            self.image = cv2.cvtColor(decoded, cv2.COLOR_BGR2HSV)
        except cv2.error:
            pass
        else:
            self._set_resized()

    def _set_resized(self):
        height, width = self.image.shape[0:2]
        for i in [var.PRIMARY_SEARCH_LEVEL, var.SECONDARY_SEARCH_LEVEL]:
            while True:
                size = 2 ** i
                if size > width:
                    i-=1
                    continue
                self.resized.append((cv2.resize(self.image, (size, math.ceil(height * size / width)), interpolation=cv2.INTER_AREA), i))
                break
