# Project style

This project's own rules for its own kinds of file. They add to the shared style guide (`style/rules/CODING_STYLE.md`, section 3.12).

## Question flow

`QUESTION_FLOW.md`, in the project root, lists every question the program asks, in the order it asks them, with where each answer leads. It is written for the lab members who use the program, so they can see what is coming and check an answer before a run. The questions are those asked through `utils_shared/questions.py`, wherever in the code they are asked.

**It changes with the program.** A question that is added, removed, reworded or moved, a changed first-run default, a changed branch (which question an answer leads to), or a changed message that says why a step is skipped: the list is changed in the same piece of work. A list that disagrees with the program is a fault, like a wrong docstring.

**A test guards the wording and the numbers.** `tests/test_question_flow.py` reads the text of every question out of the code and fails when one is missing from the list or worded differently; the parts that vary (*file*, *time*) may be any words. It can only read a question that is written in the call that asks it, or handed on through an input called `question`, and it fails when it meets one it cannot read. A question given its own number in the call (`number='3.5'`, shown on screen as it is) must sit in the row of that number. The questions of sections 1 to 3 have their numbers; the others are numbered on screen in the order asked. Run it with `sh style/setup/run_tool.sh enforce/tools/test_runner.py` after changing a question. The order, the branches, the defaults, the option labels, the messages, and a question the program no longer asks are not tested: they are still checked by reading.

**Layout**

- The title is `# Portimao question flow (V<version>)`. The version is the program version, written by `.style/release_hook.py` at every release and never by hand.
- "How to read it" comes first: what the end of a question means (the `(Y/n)` letters, the numbers of a list such as `(1/2/3)` or `(1–7)`, `[value]` and `[skip]`, the brighter default), the line said after a wrong answer, what **Next** and **(plot)** mean, and how the numbers on screen can differ from the numbers in the list.
- One `## <number>. <title>` heading for each section the program prints, in the same order and with the same title as on screen, with a `---` line between sections.
- Within a section, a lettered sub-heading for each group of questions (`### 3.A Haem decomposition`), and one level more for a branch with questions of its own (`#### 3.A.1`).
- The questions are in tables, one row each, with one of these sets of columns:
    - `# | Question | Yes → | No →` for yes or no questions, among them a "Do you accept...?" question with one way to change (what **n** does, as on screen, in its row);
    - `# | Question | 1 → | 2 →` for a "Do you accept...?" question with more ways to change and other numbered choices;
    - `# | Question | Leads to` (or `Answer leads to`) for everything else.
- A row holds:
    - the number, following the sections and the nesting on screen (`3.1`, `3.1.1`);
    - the question in the words shown on screen, with the part that varies in italics (*file*, *time*);
    - the end of the question as it is shown, with the first-run default: `(y/N)`, `(Y/n)`, `(1/2/3)`, `[value]` or `[skip]`;
    - where each answer leads, as the number of the next question in bold (**3.2**);
    - **(plot)** wherever the plot is redrawn.
- A question that is asked only sometimes says when, in italics in its row or in a sentence above its table.
- Plain sentences between the tables give what the program says or does without asking: messages, steps that are skipped and why, and what is written to the results folder.
- Plain words throughout: no function, file or variable names from the code, apart from the files and folders a user sees.

## Maths

`MATHS.md`, in the project root, says how the program works out each of its haem numbers. It is written for a scientist who checks the maths without reading the code (the user's supervisor), so that they can say whether the program does what they want.

**It changes with the program.** Maths that is added or changed (a new quantity, a changed equation, a changed number such as how many spectra a level is taken from, a changed rule for what is refused or left empty) is changed in the document in the same piece of work, with its test. A document that disagrees with the program is a fault, like a wrong docstring.

**Layout**

- The title is `# Portimao maths`, then a few lines on what the document is and the words used throughout (spectrum, median).
- One `## <number>. <quantity>` heading for each quantity, in the order the program works them out, with a `---` line between them; a quantity worked out in steps has one `### <number>.<step>` heading per step.
- Each quantity, or step, has these parts in this order:
    - the equation, in a `text` block, one equation per line, in the form `y = m × x + c`: the quantity on the left, plain letters, `×` and `÷`, a level or a time told apart by a word after an underscore (`D_start`, `t_new`);
    - a list of every letter in it, each with what it is, its unit in brackets and, when it comes from another section, which one;
    - "Notes:", a list of what the equation does not show: what is skipped, kept, refused or left empty;
    - "Example:", worked in numbers a reader can follow by hand, each step written out. Its numbers are the numbers of its test; when the test uses a smaller number than the program (3 spectra in place of 50), the example says so;
    - "Checked by:", the name of each test and its file.
- Plain words throughout: no function, file or variable names from the code, apart from the tests. No symbols a reader must look up (no Greek letters apart from Δ, no sums written as series, no matrices): a sum is written out in words.
