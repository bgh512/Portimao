---
name: new-file
description: Create a new source file (Python, C, C++, JavaScript, CSS or HTML) with the style guide layout already in place. Use whenever a new code file is needed, instead of writing the module docstring, banners and docstring skeletons by hand.
---

# New file

Create the file with the file maker, then fill it in:

`sh style/setup/run_tool.sh enforce/tools/file_maker.py <path> "<one-sentence summary>" --kind <kind>`

- `<kind>` is for Python only: `module` (helpers and main functions, the default), `class`, `job` (a job script) or `main` (the entry point).
- The suffix picks the language: `.py`, `.c`/`.cpp`/`.h`/`.hpp`, `.js`, `.css`, `.html`.
- Replace the example functions, keeping the banners and docstring sections. The hooks format the file after each edit.
