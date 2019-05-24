import errno
import os
import sys


def execute():
    child_pid = os.fork()
    if child_pid == 0:
        os.execvpe('terraform', ['terraform'] + sys.argv[1:], os.environ)
    else:
        while True:
            try:
                _, exit_status = os.waitpid(child_pid, 0)
            except KeyboardInterrupt:
                pass
            except OSError as error:
                if error.errno == errno.ECHILD:
                    # No child processes.
                    # It has exited already.
                    break
                elif error.errno == errno.EINTR:
                    # Interrupted system call.
                    # This happens when resizing the terminal.
                    pass
                else:
                    # An actual error occurred.
                    raise
            else:
                exit_code = exit_status >> 8
                return exit_code
