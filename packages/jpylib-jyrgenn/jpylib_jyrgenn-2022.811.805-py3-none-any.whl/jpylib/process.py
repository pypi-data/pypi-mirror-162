# -*- python -*-

# Do things with processes.

import subprocess
from .alerts import *

# we take these characters as the indication to run a command in the shell, if
# not otherwise indicated
shellmeta = "\"'`|&;[(<>)]*?$"

def backquote(command, shell=None, full_result=False, silent=False):
    """Similar to Perl's \`command\` feature: run process, return output.

    If command is a tuple or a list, run it directly. Otherwise, make it a
    string if necessary and:
    
     - If `shell` is `True`, run command as shell command line with `/bin/sh`.

     - If `shell` is otherwise true, use it as the shell and run command in it.
    
     - If `shell` is `None` (or unspecified), run command with `/bin/sh` if it
       contains shell meta characters. Otherwise, split the string into a list
       and run it directly. This is the default.

     - If `shell` is otherwise false, split the string into a list and run it
       directly.

    If `full_result` is false (the default), return only stdout as a string. In
    this case, a `ChildProcessError` is raised if the exit status of the command
    is non-zero or stderr is not empty. This can be suppressed by setting
    `silent` to true.

    If `full_result` is true, return a tuple of (stdout, stderr, exit status).
    No exception for exit status or stderr is raised, regardless of the value
    of `silent`.

    In any case, however, there will be an exception raised if the called
    program cannot be found.

    """
    run_shell = False                   # for testing
    if not isinstance(command, (list, tuple)):
        command = str(command)
        if shell:
            if shell is True:
                shell = "/bin/sh"
            command = [shell, "-c", command]
            run_shell = True
        elif shell is None:
            if any([ ch in shellmeta for ch in command ]):
                command = ["/bin/sh", "-c", command]
                run_shell = True
            else:
                command = command.split()
        else:
            command = command.split()

    with subprocess.Popen(command, stdin=subprocess.DEVNULL,
                          stderr=subprocess.PIPE,
                          stdout=subprocess.PIPE) as proc:
        proc.wait()
        result = (proc.stdout.read().decode("utf-8"),
                  proc.stderr.read().decode("utf-8"),
                  proc.returncode)
    if full_result:
        if full_result == "plus":
            return result, run_shell
        return result
    else:
        if not silent and (result[1] or result[2]):
            raise ChildProcessError("command {} exited status {}; stderr: {}"
                                    .format(command, result[2],
                                            repr(result[1])))
        return result[0]
