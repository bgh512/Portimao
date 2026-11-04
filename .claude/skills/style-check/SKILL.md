---
name: style-check
description: Check code against the shared style guide (style/CODING_STYLE.md) and fix what does not match. Use when the user asks to check, review, tidy or clean up code for style, or before a commit of a larger change.
---

# Style check

Check the files the user names, or, if none are named, the files changed since the last commit (`git status --short` and `git diff --name-only`). Skip anything listed in `.styleignore` and everything inside `style/`.

1. Run the automatic tools first, so only the judgement calls are left:
   - Python: `ruff check --fix <files>`. Do not run yapf; its layout does not match section 3.1 of the guide.
   - C and C++: `clang-format -i <files>`.
   - All: `python style/tools_format/banner_formatter.py <files>`.
   If a tool is not installed, say so and carry on.
2. Run `ruff check <files>` again and fix every problem it still reports, including unused imports.
3. Read each file and compare it with `style/CODING_STYLE.md`, which the tools cannot check fully:
   - names (functions start with the subject and end in `-er` or `-or`, helpers start with `_`, booleans read as statements, units in names such as `_nm`)
   - multiline layouts as in section 3.1 (arguments aligned with the first, closing bracket on its own line, trailing commas)
   - the order of banners and sections (imports, constants, helpers, main functions)
   - every docstring section present and in order (Summary, Inputs, Globals read, Outputs, Globals mutated, Equations, Helpers), with units stated
   - the Helpers list matches the functions actually called
   - numbered major stages and substeps inside long functions
   - British spelling in comments, docstrings and text shown to users
4. Fix what does not match. If a fix would change behaviour, ask first.
5. Finish with a short list of what was changed, file by file, and anything left for the user to decide.
