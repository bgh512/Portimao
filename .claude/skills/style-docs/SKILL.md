---
name: style-docs
description: Create or update the project documentation (README.md, FUNCTION_LIST.md, DATA_FORMAT.md, COMMUNICATION_PROTOCOL.md) so it follows the style guide templates and matches the code. Use when the user asks to write, update or check the docs, or after code or data formats change.
---

# Documentation update

1. Regenerate the function list instead of writing it by hand:
   `python style/tools_format/function_list_generator.py --project "<Project Title>"`
   Use the title from the top of `README.md`. Add `--root <folder>` for a sub-project.
2. For each of `README.md`, `DATA_FORMAT.md` and `COMMUNICATION_PROTOCOL.md`, read the matching template in `style/templates/` (`README_TEMPLATE.md`, `DATA_FORMAT_TEMPLATE.md`, `COMMUNICATION_PROTOCOL_TEMPLATE.md`) and section 6 of `style/CODING_STYLE.md`.
   - If the file is missing and the project needs it, create it from the template. `COMMUNICATION_PROTOCOL.md` is only needed when the project talks to hardware or another program.
   - If it exists, check that its sections follow the template in order, then check its content against the code: run commands, options, folder layout, file formats, units and array shapes.
3. Keep the project's own wording where it is correct. Change only what is missing, out of date or out of order.
4. Do not change the version in the README title. It is not updated automatically.
5. Finish with a list of what changed in each file, and any question the code cannot answer (for example the units of a value that is never stated).
