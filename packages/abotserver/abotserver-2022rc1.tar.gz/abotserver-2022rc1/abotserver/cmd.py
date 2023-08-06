import os
import signal
import sys
import logging
import textwrap
import subprocess
import click
import psutil
from time import sleep
from contextlib import suppress
from daemon import DaemonContext
from daemon.pidfile import TimeoutPIDLockFile
from lockfile.pidlockfile import read_pid_from_pidfile

from .process import GunicornMonitor, check_if_pidfile_process_is_running

log = logging.getLogger(__name__)

LOG_DIR = "/var/log/abotserver"
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

RUN_DIR = "/var/run/abotserver"
if not os.path.exists(RUN_DIR):
    os.mkdir(RUN_DIR)


def setup_logging(filename):
    """Creates log file handler for daemon process"""
    root = logging.getLogger()
    handler = logging.FileHandler(filename)
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    return handler.stream


@click.group()
def cli():
    pass


@cli.command("run", short_help="run a server")
@click.option("--bind", default="0.0.0.0:8000", show_default=True,
              type=click.STRING, help="The socket to bind.")
@click.option("--daemon/--no-daemon", default=False, show_default=True, help="Daemonize the Gunicorn process.")
@click.option("--workers", default=1, type=click.INT, show_default=True,
              help="The number of worker processes for handling requests.")
@click.option("--worker-class", default="uvicorn.workers.UvicornWorker", show_default=True,
              type=click.STRING, help="The type of workers to use.")
@click.option("--timeout", default=60, type=click.INT, show_default=True,
              help="Workers silent for more than this many seconds are killed and restarted.")
@click.option("--log-level", default="info", show_default=True,
              type=click.Choice(["debug", "info", "warning", "error", "critical"], case_sensitive=False),
              help="The granularity of Error log outputs.")
@click.option("--env", default=None, show_default=True, help="Set environment variable (key=value)")
def run_server(bind, daemon, workers, worker_class, timeout, log_level, env):
    pid_file = os.path.join(RUN_DIR, f'abotserver.pid')
    daemon_file = os.path.join(LOG_DIR, f'daemon.log')
    check_if_pidfile_process_is_running(pid_file=pid_file, process_name="abotserver")
    print(
        textwrap.dedent(
            """\
            Running the Server with:
            Bind: {bind}
            Workers: {workers} {worker_class}
            Timeout: {timeout}
            LogLevel: {log_level}
            =================================================================\
        """.format(
                bind=bind,
                workers=workers,
                worker_class=worker_class,
                timeout=timeout,
                log_level=log_level,
            )
        )
    )

    run_args = [
        "gunicorn",
        "--bind",
        str(bind),
        "--workers",
        str(workers),
        "--worker-class",
        str(worker_class),
        "--timeout",
        str(timeout),
        "--graceful-timeout",
        str(timeout),
        "--log-level",
        str(log_level),
        "--name",
        "abotserver",
        "--pid",
        pid_file,
    ]

    run_args += ["--access-logfile", os.path.join(LOG_DIR, "access.log")]
    run_args += ["--error-logfile", os.path.join(LOG_DIR, "error.log")]
    run_args += ["--logger-class", "abotserver.logging.Logger"]
    run_args += ["--capture-output"]
    if daemon:
        run_args += ["--daemon"]
    else:
        run_args += ["--reload"]

    if env:
        run_args += ["--env", env]

    run_args += ["abotserver.main:app"]

    gunicorn_master_proc = None

    def kill_proc(signum, _):
        log.info("Received signal: %s. Closing gunicorn.", signum)
        gunicorn_master_proc.terminate()
        with suppress(TimeoutError):
            gunicorn_master_proc.wait(timeout=30)
        if gunicorn_master_proc.poll() is not None:
            gunicorn_master_proc.kill()
        sys.exit(0)

    def monitor_gunicorn(gunicorn_master_pid: int):
        # Register signal handlers
        signal.signal(signal.SIGINT, kill_proc)
        signal.signal(signal.SIGTERM, kill_proc)

        # These run forever until SIG{INT, TERM, KILL, ...} signal is sent
        GunicornMonitor(
            gunicorn_master_pid=gunicorn_master_pid,
            num_workers_expected=workers,
            master_timeout=timeout,
            worker_refresh_interval=30,
            worker_refresh_batch_size=1,
            reload_on_plugin_change=False,
        ).start()

    if daemon:
        handle = setup_logging(daemon_file)
        base, ext = os.path.splitext(pid_file)
        stdout = os.path.join(LOG_DIR, f'daemon.out')
        stderr = os.path.join(LOG_DIR, f'daemon.err')
        with open(stdout, 'w+') as stdout, open(stderr, 'w+') as stderr:
            ctx = DaemonContext(
                pidfile=TimeoutPIDLockFile(f"{base}-monitor{ext}", -1),
                files_preserve=[handle],
                stdout=stdout,
                stderr=stderr,
            )
            with ctx:
                subprocess.Popen(run_args, close_fds=True)

                # Reading pid of gunicorn master as it will be different that
                # the one of process spawned above.
                while True:
                    sleep(0.1)
                    gunicorn_master_proc_pid = read_pid_from_pidfile(pid_file)
                    if gunicorn_master_proc_pid:
                        break

                # Run Gunicorn monitor
                gunicorn_master_proc = psutil.Process(gunicorn_master_proc_pid)
                monitor_gunicorn(gunicorn_master_proc.pid)
    else:
        gunicorn_master_proc = subprocess.Popen(run_args, close_fds=True)
        monitor_gunicorn(gunicorn_master_proc.pid)


@cli.command("stop", short_help="Stop the server")
def stop_server():
    pid_file = os.path.join(RUN_DIR, f'abotserver.pid')
    pid = read_pid_from_pidfile(pidfile_path=pid_file)
    if pid:
        click.echo(click.style(">>> Stop the Server[PID:{}] ......".format(pid), fg='yellow'))
        try:
            os.kill(pid, signal.SIGSTOP)
            click.echo(click.style("[SUCCESS]: {}".format("The server already has been stop."), fg='green'))
        except OSError as e:
            click.echo(click.style("[FAILED]: {}".format(str(e)), fg='red'))
        finally:
            sleep(1)
    else:
        click.echo(click.style("[Failed]: {}".format("The server didn't running."), fg='red'))
