---
name: style-check
description: Style pass - format, review and fix code so it follows the shared style guide exactly, then bring the documents up to date. Use only when the user asks for a style pass, or to check, review, tidy or clean up code for style. Add "all" to cover the whole project instead of the changed files.
---

# Style pass

The fixing is done by the `style-fixer` agent (Sonnet), so this pass costs little of your own context. Do not read or fix the files yourself.

1. Decide the files: the ones the user named; every code file git tracks (`git ls-files`) if they said "all"; otherwise the changed files from `git status --short`. Leave out `style/` and what `.style/styleignore` lists.
2. Ask the `style-fixer` agent to fix them. For more than about 15 files, split them by folder and start one `style-fixer` per group in the same message, so they run in parallel.
3. For each `Left:` line: fix it yourself only if it is clearly right and changes no behaviour; otherwise ask the user.
4. If the pass renamed anything, or the user said "all", ask the `docs-keeper` agent to bring the documents in line with the code.
5. Finish with your report (Done, Questions for you, Status), passing on the agents' lines in short. Wait for every agent before writing "Ready".
