import sys
from collections import defaultdict

CELL_ROT = { "\\": 1, "/": -1 }
MP_MOVE = { "<": -1, ">": 1 }
TOP_COPY = { "(": -1, ")": 1 }
OPERATORS = { "+": "+",
              "-": "-",
              "*": "*",
              ",": "//" }

class _Getch:
    """
    Provide cross-platform getch functionality. Shamelessly stolen from
    http://code.activestate.com/recipes/134892/
    """
    def __init__(self):
        try:
            self._impl = _GetchWindows()
        except ImportError:
            self._impl = _GetchUnix()

    def __call__(self): return self._impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()

def read_character():
    # read one character from stdin. Returns 0 when no input is available.
    if online:
        try:
            char = ord(inputs.pop(0))
        except:
            char = 0
        return char
    elif sys.stdin.isatty():
        # we're in console, read a character from the user
        char = getch()
        # check for ctrl-c (break)
        if ord(char) == 3:
            sys.stdout.write("^C")
            sys.stdout.flush()
            raise KeyboardInterrupt
        elif ord(char) in [13]: # \r should act as a newline
            char = "\n"
        elif ord(char) == 27 or ord(char) > 255: # if input is <Esc> or is greater than 127, treat as EOF
            char = 0
        return char if char == 0 else ord(char)
    else:
        # input is redirected using pipes
        char = sys.stdin.read(1)
        # return 0 if there is no more input available or if the character is out of range
        if char != "" and ord(char) > 127: char = ""
        return ord(char) if char != "" else 0

class Interpreter:
    """
    Hello Hell interpreter.
    """
    def __init__(self, code):

        self._code = ''.join(code.split("\n"))
        
        # construct a defaultdict to contain the tape
        self._tape = defaultdict(lambda: [0, 0, 0])
        self._cell = 0

        # initialize the tape with Hello, World!
        for i in range(13):
            temp = ord("Hello, World!"[i])
            self._tape[i] = [temp, temp, temp]

        self._code_index = 0
        self._tape_index = 0

        self._rot = False

        # record of all running loops, each loop is [start_pos, loop_cell, [current, cell, values], [values, to, loop, over]] and yes I know this comment is way longer than recommended. Frick you because it's my language so I can do what I want. Sue me.
        self._loops = []

    def next_cmd(self):
        """
        Execute the next command in the program
        """

        try:
            cmd = self._code[self._code_index]
        except IndexError:
            for cell in self._tape:
                if online:
                    out[1] += chr(self._tape[cell][0])
                print(chr(self._tape[cell][0]), end="")

        try:
            self.handle_instruction(cmd)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            raise StopExecution()

        self._code_index += 1
        changed = False
        for loop in range(len(self._loops)): # for each loop:
            for value in range(3): # for each value in the cell that the loop points to:
                if self._loops[loop][2][value] != self._tape[self._loops[loop][1]][value]:
                    # if the pointed-to cell has changed:
                    if not self._rot:
                        self._loops[loop][3].append(self._tape[self._loops[loop][1]][value])
                        # add the changed values to the loop if there wasn't a rotation

                    changed = True

            if changed:
                self._loops[loop][2] = [*self._tape[self._loops[loop][1]]]


    def handle_instruction(self, command):
        """
        Do the do of the do
        """
        self._rot = False
        mem_i = self._tape_index
        cell = self._tape[mem_i]
        cell_a = cell[0]
        cell_b = cell[1]
        if len(self._loops):
            current_loop = self._loops[-1]

        if command in CELL_ROT: # rotate the current cell
            self._tape[mem_i] = cell[CELL_ROT[command]:3] + cell[:CELL_ROT[command]]
            self._rot = True

        elif command in MP_MOVE: # move the memory pointer
            self._tape_index += MP_MOVE[command]

        elif command in TOP_COPY: # copy the top of the cell to an adjecent cell
            self._tape[mem_i + TOP_COPY[command]][0] = cell_a

        elif command in OPERATORS: # execute c = a <operator> b
            self._tape[mem_i][2] = eval(f"{cell[0]}{OPERATORS[command]}{cell[1]}")%256

        elif command == "^": # set b and c equal to a
            self._tape[mem_i] = [cell_a, cell_a, cell_a]

        elif command == "!": # get input and store it in a
            self._tape[mem_i][0] = read_character()

        elif command == "[": # start a loop
            self._loops.append([self._code_index, mem_i, [*cell], [x for x in cell if x]])
            if cell == [0, 0, 0]:
                self._skip("[", "]")

        elif command == "]": # end a loop
            if len(self._loops): # don't error if we're not in a loop
                if len(current_loop[3]):
                    current_loop[3].pop(0) # remove the looped over value

                if len(current_loop[3]): # loop if there's more to loop over
                    self._code_index = current_loop[0]

                else:
                    self._loops.pop() # otherwise end the loop

        elif command == "~":
            if len(self._loops):
                self._tape[mem_i][0] = current_loop[3][0]

        elif command == "{": # start an if statement
            if not cell_a: self._skip("{", "}")


    def _skip(self, start, end):
        # skip to the matching bracket in the code

        depth = 1

        while depth:
            try:
                cmd = self._code[self._code_index + 1]
            except IndexError:
                if online:
                    raise StopExecution()
                exit("\n")

            if cmd == start:
                depth += 1

            elif cmd == end:
                depth -= 1

            self._code_index += 1


class StopExecution(Exception):
    pass


def execute(code, input_list, output_var):
    """
    Online interpreter execution
    """
    global out
    global online
    global inputs
    out = output_var
    out[1] = ""
    out[2] = ""
    online = True
    inputs = [char for char in input_list]

    interp = Interpreter(code)

    while True:
        try:
            interp.next_cmd()
        except StopExecution:
            return


if __name__ == "__main__":
    """
    Offline interpreter execution
    """
    global online
    online = False

    try:
        if sys.argv[1] == "h":
            exit(f"Usage: $ python {sys.argv[0]} path/to/program")
        else:
            try:
                code = open(sys.argv[1], 'r').read()
            except:
                exit(f"Error: There was a problem reading the file - {sys.argv[1]}")
    except IndexError:
        exit(f"Error: A file path is required: $ python {sys.argv[0]} path/to/program")

    interp = Interpreter(code)

    try:
        while True:
            try:
                interp.next_cmd()
            except StopExecution:
                exit("\n")
    except KeyboardInterrupt:
        exit("\nKeyboardInterrupt")

