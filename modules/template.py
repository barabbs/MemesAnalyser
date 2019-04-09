from . import var
import numpy as np
import os, cv2, math


def matchTemplate_decorator(n):
    """
    Decorates the comparison method for the usage in Template class

    :param n: Number of the comparison method to return
    :type n: int
    :return:
    """
    if var.MATCH_TEMPLATE_METHODS[n][1] == 0:
        def func_wrapper(img, templ, scale):
            result = cv2.minMaxLoc(cv2.matchTemplate(img, templ, var.MATCH_TEMPLATE_METHODS[n][0]))
            return result[1], result[3], scale
    else:
        def func_wrapper(img, templ, scale):
            result = cv2.minMaxLoc(cv2.matchTemplate(img, templ, var.MATCH_TEMPLATE_METHODS[n][0]))
            return 1 - result[0], result[2], scale
    return func_wrapper


class Template(object):
    """
    Class representing a meme template
    """

    def __init__(self, *args):
        """
        Initialises a new template object with the arguments gotten from database

        :param args: list of arguments of the template
        """
        self.ID = args[0]
        self.name = args[1]
        self.level_correction = args[2]
        self.threshold = args[6]
        self.template = None
        self.resized = dict()
        self.matchers = [matchTemplate_decorator(i) for i in range(var.METHODS_NUMBER)]
        self._load_frames()

    def _load_frames(self):
        """
        Loads the template image, converts it to HSV values and resizes it to differend levels and different scales for each level

        :return:
        """
        self.template = cv2.imread(os.path.join(var.TEMPLATES_DIR, str(self.ID) + var.IMG_EXT))
        self.template = cv2.cvtColor(self.template, cv2.COLOR_BGR2HSV)

        height, width = self.template.shape[0:2]

        for level in range(var.MAX_LEVEL, var.MIN_LEVEL - 1, -1):
            self.resized[level] = dict()
            size = 2 ** (level - self.level_correction)
            level_shape = np.array((size, int(size * height / width)))
            max_shape = ((1 - var.MARGIN_PERC) * level_shape).astype(int)

            for scale in range(var.MIN_SCALE, var.MAX_SCALE + 1):
                scale_shape = (level_shape * scale) // var.SCALE_STEPS
                try:
                    if not math.log2(scale).is_integer():
                        raise KeyError
                    self.resized[level][scale] = self.resized[level + 1][scale / 2]
                except KeyError:
                    self.resized[level][scale] = cv2.resize(self.template, (scale_shape[0], max(1, scale_shape[1])), interpolation=cv2.INTER_AREA)

                if (scale_shape > max_shape).any():
                    corner = (scale_shape - max_shape) // 2
                    self.resized[level][scale] = self.resized[level][scale][corner[1]:corner[1] + max_shape[1], corner[0]:corner[0] + max_shape[0]]

    def primary_search(self, meme):
        """
        Primary research for the meme, with the first comparison method
        Returns a list with match value for that function, the position and the scale of the maximum match

        :param meme: The meme to analyse
        :return:
        """
        return self.search(meme, 0)

    def secondary_search(self, meme):
        """
        Secondary research for the meme, with all 3 comparison method
        Returns a list of lists with match value for that function, position and scale of the maximum match for all 3 methods of comparison

        :param meme: The meme to analyse
        :return:
        """
        return [self.search(meme, 1, i) for i in range(var.METHODS_NUMBER)]

    def search(self, meme, ind, method_n=0):
        """
        Searches the template inside the given meme with the provided function
        Returns a list of lists with match value for that function, position and scale of the maximum match for all 3 methods of comparison

        :param meme: The meme to analyse
        :param ind: A number representing primary or secondary search
        :type ind: int
        :param method_n: Number of the function to use
        :type method_n: int
        :return:
        """

        maximum = [0, (0, 0), 0]
        level = meme.resized[ind][1]
        for i in range(var.MIN_SCALE, var.MAX_SCALE + 1):
            img = meme.resized[ind][0]
            templ = self.resized[level][i]
            if img.shape[0] >= templ.shape[0] and img.shape[1] >= templ.shape[1]:
                result = self.matchers[method_n](img, templ, i)
                maximum = max(maximum, result, key=lambda x: x[0])
        return maximum
