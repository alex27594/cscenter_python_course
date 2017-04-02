from contextlib import redirect_stdout
from enum import Enum
import functools
import io
import sys
import traceback
from urllib.request import urlopen



class assert_raises:
    def __init__(self, exc_type):
         self.exc_type = exc_type

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError("did not raise '{}'".format(self.exc_type.__name__))
        elif self.exc_type == exc_type:
            return True
        else:
            return False


class closing:
    def __init__(self, res):
        self.res = res

    def __enter__(self):
        return self.res

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.res.close()
        del self.res


class log_exceptions:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        traceback.print_exception(exc_type, exc_val, exc_tb)
        return True


class with_context:
    def __init__(self, context_man):
        self.context_man = context_man

    def __call__(self, func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with self.context_man:
                func(*args, **kwargs)
        return inner


class Op(Enum):
    NEXT = ("Ook.", "Ook?")
    PREV = ("Ook?", "Ook.")
    INC = ("Ook.", "Ook.")
    DEC = ("Ook!", "Ook!")
    PRINT = ("Ook!", "Ook.")
    INPUT = ("Ook.", "Ook!")
    START_LOOP = ("Ook!", "Ook?")
    END_LOOP = ("Ook?", "Ook!")


def ook_tokenize(ook_string):
    ooks = ook_string.split()
    ook_pairs = [(ooks[i], ooks[i + 1]) for i in range(0, len(ooks), 2)]
    ook_commands = []
    for ook_pair in ook_pairs:
        for op in Op:
            if ook_pair == op.value:
                ook_commands.append(op)
                break
    return ook_commands


def find_loops(code):
    loops = {}
    loop_levels = []
    for com_id in range(len(code)):
        if code[com_id] == Op.START_LOOP:
            loop_levels.append(com_id)
        elif code[com_id] == Op.END_LOOP:
            end_of_loop = loop_levels.pop()
            loops[end_of_loop] = com_id
            loops[com_id] = end_of_loop
    return loops


def ook_eval(source, *, memory_limit=2**16):
    code = ook_tokenize(source)
    memory = [0] * memory_limit
    mp = 0
    com_id = 0
    loops = find_loops(code)
    while com_id < len(code):
        command = code[com_id]
        if command == Op.NEXT:
            mp += 1
            com_id += 1
        elif command == Op.PREV:
            mp -= 1
            com_id += 1
        elif command == Op.INC:
            memory[mp] += 1
            com_id += 1
        elif command == Op.DEC:
            memory[mp] -= 1
            com_id += 1
        elif command == Op.PRINT:
            sys.stdout.write(chr(memory[mp]))
            com_id += 1
        elif command == Op.INPUT:
            memory[mp] = ord(sys.stdin.read(1))
            com_id += 1
        elif command == Op.START_LOOP:
            if memory[mp] == 0:
                com_id = loops[com_id] + 1
            else:
                com_id += 1
        elif command == Op.END_LOOP:
            if memory[mp] != 0:
                com_id = loops[com_id] + 1
            else:
                com_id += 1
    print()

"""
class Pipe:
    def __init__(self, server_url):
        self.server_url = server_url

    def pull(self):
        with urlopen()
"""

ook_eval("Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. Ook! Ook. Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. Ook. Ook. Ook! Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook. Ook! Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook. Ook. Ook? Ook. Ook? Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. Ook! Ook. Ook. Ook? Ook. Ook? Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. Ook? Ook. Ook? Ook. Ook? Ook. Ook? Ook. Ook! Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook. Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. Ook. Ook? Ook. Ook? Ook. Ook. Ook! Ook.")







