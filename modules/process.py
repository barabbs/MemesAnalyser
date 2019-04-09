from . import var
from . import utility as utl
import multiprocessing as mprc
import queue, traceback, os, time


class Process(mprc.Process):
    """
    Base class for the child processes
    """

    def __init__(self, name, pipes, terminal, **kwargs):
        """
        Creates a new child process object

        :param name: The name of the process
        :type name: str
        :param pipes: A dict of the connection pipes
        :type pipes: dict
        :param terminal: The terminal object of the current run
        :param kwargs:Additional kwargs passed to the class
        """
        super(Process, self).__init__()
        self.name = name
        self.pipes = pipes
        self.terminal = terminal
        self.exit_event = mprc.Event()

        self.daemon = True

    def _new_subprocess(self, sub_class, name, kwargs=None):
        """
        Puts a new request for a new child process in the pipe connecting to the main process

        :param sub_class: The class of the subprocess
        :param name: The name of the process
        :type name: str
        :param kwargs: The kwargs to be pass to the new process
        :type kwargs: dict
        :return:
        """
        self.pipes['subprocess'].put((True, sub_class, name, kwargs))

    def _close_subprocess(self, keys):
        """
        Puts a new request in the pipe connecting to the main process for closing child processes

        :param keys: a list of the names of the processes to close
        :type keys: list
        :return:
        """
        self.pipes['subprocess'].put((False, keys))

    def run(self):
        """
        Method called at process start
        Calls the _run() method and on exit class exit()

        :return:
        """
        try:
            self._run()
        except StopIteration:
            pass
        self.exit()

    def _run(self):
        """
        Placeholder for _run() method

        :return:
        """
        pass

    def check_exit_event(self):
        """
        Checks if the exit event is set. If yes, raises StopIteration to exit the process

        :return:
        """
        if self.exit_event.is_set():
            raise StopIteration

    def pipe_put(self, key, item):
        """
        Puts a new item to a pipe and repeatedly retries if the pipe is too full

        :param key: The name of the pipe
        :param key: str
        :param item: the item to put in pipe
        :return:
        """
        while True:
            try:
                self.pipes[key].put(item, block=False)
            except queue.Full:
                # self.terminal.warning(f"pipe {key} is full")
                time.sleep(var.PIPE_RETRY_DELAY)
            else:
                break

    def pipe_get(self, key):
        """
        Gets a new item from a pipe and repeatedly retries if the pipe is empty
        If the pipe is empty checks for exit event

        :param key: The name of the pipe
        :param key: str
        :return:
        """
        while True:
            try:
                new = self.pipes[key].get(block=False)
            except queue.Empty:
                # if not key=="database":
                #    self.terminal.print(f"pipe {key} is empty")
                time.sleep(var.PIPE_RETRY_DELAY)
            else:
                break
            self.check_exit_event()
        return new

    def wait_for_pipe(self, key):
        """
        Waits for the pipe to empty

        :param key: The name of the pipe
        :param key: str
        :return:
        """
        while not self.pipes[key].empty():
            time.sleep(var.PIPE_RETRY_DELAY)

    def exit(self):
        """
        Exits the process and clears the exit event

        :return:
        """
        self.exit_event.clear()

    def track_error(self, to_file=True, error=None, additional=None):
        """
        Handles the error given

        :param to_file: boolean representing if the error has to be written to file
        :type to_file: bool
        :param error: The error raised
        :type error: Exception
        :param additional: Additional data to add to the file
        :type additional: dict
        :return:
        """
        if error:
            self.terminal.error("{}: {}".format(self.name, error))
        if to_file:
            try:
                file = os.path.join(var.ERROR_DIR, self.name.split("_")[0], "{}_{}.txt".format(self.name,utl.get_time()))
                with open(file, 'w') as f:
                    traceback.print_exc(file=f)
                    if additional:
                        f.write("\n\n\n")
                        for i in additional:
                            f.write("{}: {}\n".format(i, additional[i]))
            except FileNotFoundError:
                os.mkdir(os.path.join(var.ERROR_DIR, self.name.split("_")[0]))
                file = os.path.join(var.ERROR_DIR, self.name.split("_")[0], "{}_{}.txt".format(self.name,utl.get_time()))
                with open(file, 'w') as f:
                    traceback.print_exc(file=f)
                    if additional:
                        f.write("\n\n\n")
                        for i in additional:
                            f.write("{}: {}\n".format(i, additional[i]))
