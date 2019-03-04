from . import var
from . import utility as utl
import multiprocessing as mprc
import queue, traceback, os, time


class Process(mprc.Process):
    def __init__(self, name, pipes, terminal, **kwargs):
        super(Process, self).__init__()
        self.name = name
        self.pipes = pipes
        self.terminal = terminal
        self.exit_event = mprc.Event()

        self.daemon = True

    def _new_subprocess(self, sub_class, name, kwargs=None):
        self.pipes['subprocess'].put((True, sub_class, name, kwargs))

    def _close_subprocess(self, keys):
        self.pipes['subprocess'].put((False, keys))

    def run(self):
        try:
            self._run()
        except StopIteration:
            pass
        self.exit()

    def _run(self):
        pass

    def check_exit_event(self):
        if self.exit_event.is_set():
            raise StopIteration

    def pipe_put(self, key, item):
        while True:
            try:
                self.pipes[key].put(item, block=False)
            except queue.Full:
                # self.terminal.warning(f"pipe {key} is full")
                time.sleep(var.PIPE_RETRY_DELAY)
            else:
                break

    def pipe_get(self, key):
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
        while not self.pipes[key].empty():
            time.sleep(var.PIPE_RETRY_DELAY)

    def exit(self):
        self.exit_event.clear()

    def track_error(self, to_file=True, error=None, additional=None):

        if error:
            self.terminal.error(f"{self.name}: {error}")
        if to_file:
            try:
                file = os.path.join(var.ERROR_DIR, self.name.split("_")[0], f"{self.name}_{utl.get_time()}.txt")
                with open(file, 'w') as f:
                    traceback.print_exc(file=f)
                    if additional:
                        f.write("\n\n\n")
                        for i in additional:
                            f.write(f"{i}: {additional[i]}\n")
            except FileNotFoundError:
                os.mkdir(os.path.join(var.ERROR_DIR, self.name.split("_")[0]))
                file = os.path.join(var.ERROR_DIR, self.name.split("_")[0], f"{self.name}_{utl.get_time()}.txt")
                with open(file, 'w') as f:
                    traceback.print_exc(file=f)
                    if additional:
                        f.write("\n\n\n")
                        for i in additional:
                            f.write(f"{i}: {additional[i]}\n")
