from . import var
import datetime
import subprocess as sprc


def get_time():
    """
    Returns a formatted string of current time

    :return:
    """
    return datetime.datetime.now().strftime(var.TIME_STAMP)


def result_calc(res):
    """
    Calculates the match value by applying the weighted sum of all comparison method results

    :param res: the result returned by secondary_search method of Template class
    :type res: list
    :return:
    """
    value = 0.0
    for i in range(var.METHODS_NUMBER):
        value += res[i][0] * var.MATCH_TEMPLATE_METHODS[i][2]
    return value


def copy_file(src, dest):
    """
    Copies the source file to the destination file

    :param src: path to the source file
    :param dest: path to the destination file
    :return:
    """
    sprc.call(["cp", src, dest])


def get_int(flt):
    """
    Returns the first decimal digits for database data saving

    :param flt: The float to convert
    :type flt: float
    :return:
    """
    return int(flt * (10 ** var.DIGITS))
