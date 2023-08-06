import sys
import signal
import hashlib
import time
import psutil
from time import sleep
from typing import Dict, List, NoReturn
from lockfile.pidlockfile import PIDLockFile

from .logging import LoggingMixin


def check_if_pidfile_process_is_running(pid_file: str, process_name: str):
    """
    Checks if a pidfile already exists and process is still running.
    If process is dead then pidfile is removed.

    :param pid_file: path to the pidfile
    :param process_name: name used in exception if process is up and
        running
    """
    pid_lock_file = PIDLockFile(path=pid_file)
    # If file exists
    if pid_lock_file.is_locked():
        # Read the pid
        pid = pid_lock_file.read_pid()
        if pid is None:
            return
        try:
            # Check if process is still running
            proc = psutil.Process(pid)
            if proc.is_running():
                raise Exception("The {0} is already running under PID {1}.".format(process_name, pid))
        except psutil.NoSuchProcess:
            # If process is dead remove the pidfile
            pid_lock_file.break_lock()


class GunicornMonitor(LoggingMixin):
    """
    Runs forever, monitoring the child processes of @gunicorn_master_proc and
    restarting workers occasionally or when files in the plug-in directory
    has been modified.

    Each iteration of the loop traverses one edge of this state transition
    diagram, where each state (node) represents
    [ num_ready_workers_running / num_workers_running ]. We expect most time to
    be spent in [n / n]. `bs` is the setting webserver.worker_refresh_batch_size.
    The horizontal transition at ? happens after the new worker parses all the
    dags (so it could take a while!)
       V ────────────────────────────────────────────────────────────────────────┐
    [n / n] ──TTIN──> [ [n, n+bs) / n + bs ]  ────?───> [n + bs / n + bs] ──TTOU─┘
       ^                          ^───────────────┘
       │
       │      ┌────────────────v
       └──────┴────── [ [0, n) / n ] <─── start
    We change the number of workers by sending TTIN and TTOU to the gunicorn
    master process, which increases and decreases the number of child workers
    respectively. Gunicorn guarantees that on TTOU workers are terminated
    gracefully and that the oldest worker is terminated.

    :param gunicorn_master_pid: PID for the main Gunicorn process
    :param num_workers_expected: Number of workers to run the Gunicorn web server
    :param master_timeout: Number of seconds the webserver waits before killing gunicorn master that
        doesn't respond
    :param worker_refresh_interval: Number of seconds to wait before refreshing a batch of workers.
    :param worker_refresh_batch_size: Number of workers to refresh at a time. When set to 0, worker
        refresh is disabled. When nonzero, airflow periodically refreshes webserver workers by
        bringing up new ones and killing old ones.
    :param reload_on_plugin_change: If set to True, SMQ will track files in plugins_folder directory.
        When it detects changes, then reload the gunicorn.
    """

    def __init__(
            self,
            gunicorn_master_pid: int,
            num_workers_expected: int,
            master_timeout: int,
            worker_refresh_interval: int,
            worker_refresh_batch_size: int,
            reload_on_plugin_change: bool,
    ):
        super().__init__()
        self.gunicorn_master_proc = psutil.Process(gunicorn_master_pid)
        self.num_workers_expected = num_workers_expected
        self.master_timeout = master_timeout
        self.worker_refresh_interval = worker_refresh_interval
        self.worker_refresh_batch_size = worker_refresh_batch_size
        self.reload_on_plugin_change = reload_on_plugin_change

        self._num_workers_running = 0
        self._num_ready_workers_running = 0
        self._last_refresh_time = time.monotonic() if worker_refresh_interval > 0 else None
        self._restart_on_next_plugin_check = False

    def _generate_plugin_state(self) -> Dict[str, float]:
        """
        Generate dict of filenames and last modification time of all files in PLUGINS_FOLDER
        directory.
        """

        PLUGINS_FOLDER = None

        if not PLUGINS_FOLDER:
            return {}

        ## Can't support plugins currently.
        # all_filenames: List[str] = []
        # for (root, _, filenames) in os.walk(PLUGINS_FOLDER):
        #     all_filenames.extend(os.path.join(root, f) for f in filenames)
        # plugin_state = {f: self._get_file_hash(f) for f in sorted(all_filenames)}
        # return plugin_state

    @staticmethod
    def _get_file_hash(fname: str):
        """Calculate MD5 hash for file"""
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_num_ready_workers_running(self) -> int:
        """Returns number of ready Gunicorn workers by looking for READY_PREFIX in process name"""
        workers = psutil.Process(self.gunicorn_master_proc.pid).children()

        def ready_prefix_on_cmdline(proc):
            try:
                cmdline = proc.cmdline()
                if len(cmdline) > 0:  # pylint: disable=len-as-condition
                    return "[ready] " in cmdline[0]
            except psutil.NoSuchProcess:
                pass
            return False

        ready_workers = [proc for proc in workers if ready_prefix_on_cmdline(proc)]
        return len(ready_workers)

    def _get_num_workers_running(self) -> int:
        """Returns number of running Gunicorn workers processes"""
        workers = psutil.Process(self.gunicorn_master_proc.pid).children()
        return len(workers)

    def _wait_until_true(self, fn, timeout: int = 0) -> None:
        """Sleeps until fn is true"""
        start_time = time.monotonic()
        while not fn():
            if 0 < timeout <= time.monotonic() - start_time:
                raise Exception("No response from gunicorn master within {0} seconds".format(timeout))
            sleep(0.1)

    def _spawn_new_workers(self, count: int) -> None:
        """
        Send signal to kill the worker.

        :param count: The number of workers to spawn
        """
        excess = 0
        for _ in range(count):
            # TTIN: Increment the number of processes by one
            self.gunicorn_master_proc.send_signal(signal.SIGTTIN)
            excess += 1
            self._wait_until_true(
                lambda: self.num_workers_expected + excess == self._get_num_workers_running(),
                timeout=self.master_timeout,
            )

    def _kill_old_workers(self, count: int) -> None:
        """
        Send signal to kill the worker.

        :param count: The number of workers to kill
        """
        for _ in range(count):
            count -= 1
            # TTOU: Decrement the number of processes by one
            self.gunicorn_master_proc.send_signal(signal.SIGTTOU)
            self._wait_until_true(
                lambda: self.num_workers_expected + count == self._get_num_workers_running(),
                timeout=self.master_timeout,
            )

    def _reload_gunicorn(self) -> None:
        """
        Send signal to reload the gunciron configuration. When gunciorn receive signals, it reload the
        configuration, start the new worker processes with a new configuration and gracefully
        shutdown older workers.
        """
        # HUP: Reload the configuration.
        self.gunicorn_master_proc.send_signal(signal.SIGHUP)
        sleep(1)
        self._wait_until_true(
            lambda: self.num_workers_expected == self._get_num_workers_running(), timeout=self.master_timeout
        )

    def start(self) -> NoReturn:
        """Starts monitoring the webserver."""
        try:  # pylint: disable=too-many-nested-blocks
            self._wait_until_true(
                lambda: self.num_workers_expected == self._get_num_workers_running(),
                timeout=self.master_timeout,
            )
            while True:
                if not self.gunicorn_master_proc.is_running():
                    sys.exit(1)
                self._check_workers()
                # Throttle loop
                sleep(1)

        except (Exception, OSError) as err:
            self.log.error(err)
            self.log.error("Shutting down webserver")
            try:
                self.gunicorn_master_proc.terminate()
                self.gunicorn_master_proc.wait()
            finally:
                sys.exit(1)

    def _check_workers(self) -> None:
        num_workers_running = self._get_num_workers_running()
        num_ready_workers_running = self._get_num_ready_workers_running()

        # Whenever some workers are not ready, wait until all workers are ready
        if num_ready_workers_running < num_workers_running:
            self.log.debug(
                '[%d / %d] Some workers are starting up, waiting...',
                num_ready_workers_running,
                num_workers_running,
            )
            sleep(1)
            return

        # If there are too many workers, then kill a worker gracefully by asking gunicorn to reduce
        # number of workers
        if num_workers_running > self.num_workers_expected:
            excess = min(num_workers_running - self.num_workers_expected, self.worker_refresh_batch_size)
            self.log.debug(
                '[%d / %d] Killing %s workers', num_ready_workers_running, num_workers_running, excess
            )
            self._kill_old_workers(excess)
            return

        # If there are too few workers, start a new worker by asking gunicorn
        # to increase number of workers
        if num_workers_running < self.num_workers_expected:
            self.log.error(
                "[%d / %d] Some workers seem to have died and gunicorn did not restart them as expected",
                num_ready_workers_running,
                num_workers_running,
            )
            sleep(10)
            num_workers_running = self._get_num_workers_running()
            if num_workers_running < self.num_workers_expected:
                new_worker_count = min(
                    num_workers_running - self.worker_refresh_batch_size, self.worker_refresh_batch_size
                )
                self.log.debug(
                    '[%d / %d] Spawning %d workers',
                    num_ready_workers_running,
                    num_workers_running,
                    new_worker_count,
                )
                self._spawn_new_workers(num_workers_running)
            return

        # Now the number of running and expected worker should be equal

        # If workers should be restarted periodically.
        if self.worker_refresh_interval > 0 and self._last_refresh_time:
            # and we refreshed the workers a long time ago, refresh the workers
            last_refresh_diff = time.monotonic() - self._last_refresh_time
            if self.worker_refresh_interval < last_refresh_diff:
                num_new_workers = self.worker_refresh_batch_size
                self.log.debug(
                    '[%d / %d] Starting doing a refresh. Starting %d workers.',
                    num_ready_workers_running,
                    num_workers_running,
                    num_new_workers,
                )
                self._spawn_new_workers(num_new_workers)
                self._last_refresh_time = time.monotonic()
                return

        # if we should check the directory with the plugin,
        if self.reload_on_plugin_change:
            # compare the previous and current contents of the directory
            new_state = self._generate_plugin_state()
            # If changed, wait until its content is fully saved.
            if new_state != self._last_plugin_state:
                self.log.debug(
                    '[%d / %d] Plugins folder changed. The gunicorn will be restarted the next time the '
                    'plugin directory is checked, if there is no change in it.',
                    num_ready_workers_running,
                    num_workers_running,
                )
                self._restart_on_next_plugin_check = True
                self._last_plugin_state = new_state
            elif self._restart_on_next_plugin_check:
                self.log.debug(
                    '[%d / %d] Starts reloading the gunicorn configuration.',
                    num_ready_workers_running,
                    num_workers_running,
                )
                self._restart_on_next_plugin_check = False
                self._last_refresh_time = time.monotonic()
                self._reload_gunicorn()