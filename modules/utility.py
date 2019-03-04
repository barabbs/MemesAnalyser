from . import var
import datetime
import subprocess as sprc
import time


def wait_for_child_processes(processes):
    for p in processes:
        print(f"joining {p.name}")
        # p.join()
        # print(f"{p.name} closed")
        while True:
            if p.is_alive():
                time.sleep(1)
            else:
                print(f"{p.name} closed")
                break


def get_time():
    return datetime.datetime.now().strftime(var.TIME_STAMP)


def result_calc(res):
    value = 0.0
    for i in range(var.METHODS_NUMBER):
        value += res[i][0] * var.MATCH_TEMPLATE_METHODS[i][2]
    return value


def copy_file(src, dest):
    sprc.call(["cp", src, dest])


def get_int(flt):
    return int(flt * (10 ** var.DIGITS))
