# Part of jpylib: read lines/items from one or more files. Skip empty and
# commented lines (matching /^\s*#/), strip leading and trailing blanks.

import os
import sys
import re
from .assorted import identity

def all_input_lines(fnames=[], cont_err=False):
    """Like Perl's diamond operator `<>`, return lines from files or stdin.

    (Generator) If `fnames` is empty, return lines from stdin, otherwise
    lines from the named files, in succession. The file name `-` stands
    for stdin. Typically, something like `sys.argv[1:]` would be passed
    as an argument. If `cont_err` is true, continue after a file open error,
    printing an error message. If `cont_err` is a callable, call it with
    the file name and the exception on error.
    """
    if not fnames:
        fnames = ["-"]
    for fname in fnames:
        try:
            if fname == "-":
                # Read from sys.stdin (not "/dev/stdin") for easier testing.
                for line in sys.stdin:
                    yield line
            else:
                with open(fname) as f:
                    for line in f:
                        yield line
        except Exception as e:
            if cont_err:
                if callable(cont_err):
                    cont_err(fname, e)
                else:
                    program = os.path.basename(sys.argv[0])
                    print(program+":", e, file=sys.stderr)
            else:
                raise e


def read_items(fname, lstrip=True, rstrip=True, strip_newline=True,
               comments_re="^\\s*#", skip_comments=True, skip_empty=True):
    
    """Read lines/items from one or more files (generator).

    With the defaults, comment like `# ...` and empty lines are skipped, and
    whitespace is stripped from the left and right ends of each line.

    `fname` is the name of the file to read; `-` may be used for stdin.

    If `lstrip` is True, whitespace will be stripped from the left side of
    each line. If it is a string, it specifies the characters to be stripped.

    If `rstrip` is True, whitespace will be stripped from the right side of
    each line. If it is a string, it specifies the characters to be stripped.

    If `strip_newline` is true, newlines will be stripped from the line even
    if `rstrip` does not contain the newline character.

    `comments_re` is used to match comment lines to be skipped (after the
    above stripping is done).

    If `skip_comments` is false, comments will be skipped without regard
    for `comments_re`.

    If `skip_empty` is true, lines that are empty after the stripping of
    whitespace (or what else is specified) are skipped.

    """
    def lstrip_func(chars):
        """Return function to strip chars from the left siide of a string."""
        def lstrip_f(s):
            return s.lstrip(chars)
        return lstrip_f

    def rstrip_func(chars):
        """Return function to strip chars from the right side of a string."""
        def rstrip_f(s):
            return s.rstrip(chars)
        return rstrip_f

    if lstrip:
        if isinstance(lstrip, str):
            lstripper = lstrip_func(lstrip)
        else:
            lstripper = str.lstrip
    else:
        lstripper = identity

    if rstrip:
        if isinstance(rstrip, str):
            if strip_newline and "\n" not in rstrip:
                rstrip += "\n"
            rstripper = rstrip_func(rstrip)
        else:
            rstripper = str.rstrip
    else:
        if strip_newline:
            rstripper = rstrip_func("\n")
        else:
            rstripper = identity

    if comments_re and skip_comments:
        skip_re = re.compile(comments_re)
    else:
        skip_re = False

    for line in all_input_lines((fname,)):
        stripped_line = rstripper(lstripper(line))
        if skip_empty and not stripped_line:
            continue
        if skip_re and skip_re.search(stripped_line):
            continue
        yield(stripped_line)

# EOF
