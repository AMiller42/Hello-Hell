# Hello Hell

Hello Hell is an esolang with one true purpose: "Hello, World!" programs. Everything else is simply an afterthought, and is quite painful to implement. The memory is a right-infinite tape, where each cell is actually another tape, each with 3 cells. At the beginning of the program, the first 13 cells are filled with the ASCII values of "Hello, World!". Other than input, these are the only literal values available to you, and any other values must come from manipulating those.

---

## Getting Started

Hello Hell requires Python 3.
```
$ python HelloHell.py h
Usage: $ python HelloHell.py path/to/program
```
---

## Commands

* -1a, -1b, -1c refer to the first second, and third values in the previous cell.
* 0a, 0b, 0c refer to the first, second, and third values in the current cell.
* 1a, 1b, 1c refer to the first, second, and third values in the next cell.

| Command | Function                                                              |
|:-------:|---------------------------------------------------------------------  |
|   `\/`   | Rotate the current cell left or right, respectively                  |
|   `<>`   | Move the Memory Pointer (MP) left or right, respectively             |
|   `()`   | Copy 0a to -1a or 1a, respectively                                   |
|   `[]`   | Start/End a loop                                                     |
|   `{}`   | Start/End an if statement                                            |
|  `+-*,`  | Add, Subtract, Multiply, Divide. Does `0c = 0a <operator> 0b`        |
|   `~`    | Within a loop, sets 0a to the current iteration value                |
|   `^`    | Sets the entire cell equal to 0a                                     |
|   `!`    | Set 0a to the next character of input                                |

All other characters are ignored by the interpreter and act as NOPs.

---

## Input

Input is done one character at a time. If input is piped in from another command, upon reaching EOF, the value in the cell at the MP is set to 0. If inputting from STDIN on the console, <kbd>Esc</kbd> represents EOF. In either form of input, characters whose ordinal values are greater than 255 are ignored, and are instead treated as EOF.

---

## Output

Once execution finishes, the top value of every cell on the tape in printed, skipping any 0's. This is the only way to print in Hello Hell, meaning that an infinite loop will never print. Since the tape is initialized with "Hello, World!", a blank program is essentially a Hello World program.

---

## Loops & If Statements

`If` statements are quite simple. If the top of the current cell is nonzero, the commands in the `if` statement will be executed. Otherwise, the statement is skipped.

The only loops in Hello Hell are `for` loops. The loop will collect any nonzero values in the current cell, and execute the commands in the loop once for each value. Within a loop, the `~` command will set the top of the current cell to the current loop value. The unique thing about these loops is that if you change any of the values in the cell being looped over, the changed values are added to the values to be looped over, allowing you to create longer loops.

---

## Computational Class

I'm *pretty sure* Hello Hell is Turing-Complete, but I haven't proved it just yet.

---

## Tests

There are a couple example programs available in the repo:

## Hello, World!
```
```

## Truth-Machine
```
[+^-/>]!*/*/>[+^>][+-/<]-/<[{*+}/]
```
* Hello Hell can't print when there's an infinite loop, so inputting 1 just loops indefinitely.
