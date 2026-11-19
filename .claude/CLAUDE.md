# Project instructions

Portimao reads Espana Scientific Software `.paf` files, plots every experiment and the combined figures, and exports Excel workbooks that can be checked by hand. It is used by lab members who do not program: they double-click a launcher and answer questions in a window with a terminal and a plot.

- Run: `python main.py`, or a launcher (`Portimao.pyw`, `Portimao.app`, `run.bat`, `run.sh`, all through `launchers/bootstrap.pyw`).
- Folders: `utils_shared/` (reading, processing, plots and export of one experiment), `utils_viewer/` (the window, the questions and the previews), `utils_custom/` (the protocol-specific summary figures and their workbooks), `fits/` (haem fit files), `config.py` (defaults, journal sizes, colours).
- Easy to get wrong: every question the program asks is listed in `QUESTION_FLOW.md`, so a changed question means a changed list; the `*_data/` folders are local sample data and are not in git; `last_answers.json` is written by the program.

<!-- >>> style guide (managed block, do not edit between these lines) -->
## Style guide

Follow the shared style guide for all code and documentation in this project:

@../style/rules/RULES.md
@../style/enforce/claude/WORKING_RULES.md

How to work with this user, and what Claude has learnt about this project (see "Files you keep" in the working rules):

@../style/enforce/claude/USER_WAYS.md
@../_USER_REVIEW/CLAUDE_MEMORY.md
@../_USER_REVIEW/PROJECT_MEMORY.md
<!-- <<< style guide -->
