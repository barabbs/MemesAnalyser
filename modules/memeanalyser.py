from . import var
from . import utility as utl
from . import process as prc
from . import databaser as db

from .template import Template
from .downloader import DownloadHandler
from .analyser import Analyser
from .databaser import Databaser
import multiprocessing as mprc
import sosso_terminal.terminal as stt
import queue, time


class MemeAnalyser(object):
    def __init__(self):
        self.terminal = stt.ASyncTerminal(["shutdown", "update"])
        self.terminal.start()

        self.pipes = {i: mprc.Queue(var.PIPES[i]) for i in var.PIPES}
        self.sources = db.read_database_lines("sources")
        self.templates = list()
        templ_list = db.read_database_lines('templates')
        for i in templ_list:
            try:
                self.templates.append(Template(*i))
            except Exception as e:
                self.terminal.error(e)
        self.terminal.ok("Sources and Templates loaded")

        self.subprocesses = dict()
        self.init_subprocesses()
        self.terminal.ok("Subprocesses started")

    def init_subprocesses(self):
        self._new_subprocess(DownloadHandler, "DownloadHandler", {'sources': self.sources})
        for i in range(var.ANALYSERS_NUMBER):
            self._new_subprocess(Analyser, f"Analyser_{i}", {'templates': self.templates})
        self._new_subprocess(Databaser, "Databaser", {'sources': self.sources})

    def _new_subprocess(self, sub_class, name, kwargs=None):
        sub = sub_class(name, self.pipes, self.terminal, **kwargs)
        self.subprocesses[sub.name] = sub
        self.subprocesses[sub.name].start()

    def _close_subprocess(self, keys, pipe=None):
        for k in keys:
            self.subprocesses[k].exit_event.set()
        if pipe:
            self.wait_for_pipe(pipe)
        try:
            printed = False
            start_try = time.time()
            while time.time() < start_try + var.EXIT_TIMEOUT:
                iterate = keys.copy()
                for k in iterate:
                    if not self.subprocesses[k].exit_event.is_set():
                        self.subprocesses[k].terminate()
                        self.terminal.print(f"{k} closed")
                        keys.remove(k)
                if len(keys) == 0:
                    break
                time.sleep(1)
                if time.time() > start_try + 10 and not printed:
                    self.terminal.warning(f"Waiting for {keys}")
                    printed = True
                self._check_commands()
        except KeyboardInterrupt:
            self.terminal.error(f"KEYBOARD INTERRUPT")
        except StopIteration:
            self.terminal.warning("FORCING EXIT")
        for k in keys:
            self.subprocesses[k].terminate()
            self.terminal.warning(f"{k} forced exit")

    def wait_for_pipe(self, key):
        start = time.time()
        self.terminal.info(f"Waiting for pipe {key} to empty...")
        try:
            while not self.pipes[key].empty():
                time.sleep(var.PIPE_RETRY_DELAY)
                self._check_commands()
                if time.time() > start + var.EXIT_TIMEOUT:
                    raise StopIteration
        except KeyboardInterrupt:
            self.terminal.error(f"KEYBOARD INTERRUPT")
        except StopIteration:
            self.terminal.warning("Pipe waiting timeout")
        else:
            self.terminal.info(f"Pipe {key} is empty")

    def run(self):
        self.terminal.info("STARTING")
        try:
            while True:
                try:
                    new = self.pipes['subprocess'].get(block=False)
                except queue.Empty:
                    pass
                else:
                    if new[0]:
                        self._new_subprocess(*new[1:])
                    else:
                        self._close_subprocess(new[1])
                self._check_commands()
        except (StopIteration, KeyboardInterrupt):
            pass
        self.terminal.info("EXITING")
        self.exit()

    def _check_commands(self):
        command = self.terminal.update()
        if command == 'update':
            pipes_statuses = list()
            for k in self.pipes:
                if self.pipes[k].full():
                    s = "full"
                elif self.pipes[k].empty():
                    s = "empty"
                else:
                    s = "normal"
                pipes_statuses.append((f"{k}: {s}",))
            self.terminal.set_inputs(pipes_statuses)
        elif command == 'shutdown':
            raise StopIteration

    def exit(self):
        for i in [(["DownloadHandler", ],), ([f"Downloader_{i}" for i in range(var.DOWNLOADERS_NUMBER)], 'download'), ([f"Analyser_{i}" for i in range(var.ANALYSERS_NUMBER)], 'memes'),
                  (["Databaser", ], "database")]:
            self._close_subprocess(*i)
        self.terminal.ok("DONE! Just wait a few seconds :)")
        time.sleep(5)
        self.terminal.exit()
