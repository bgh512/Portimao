---
name: todo-tidy
description: Condense and clear the notes in _USER_REVIEW/TODO.md - remove built items, merge repeats and shorten notes, without touching the Order table, the chunks or the standing reviews. Use when the user asks to tidy, condense, clean up or clear the to-do.
---

# To-do tidy

The work is done by the `todo-keeper` agent (Haiku), so it costs little of your own context. Do not read or rewrite the to-do yourself.

It tidies only each set's aim, "For you to do", "Notes" and "Information needed", and "Later". The Order table, the chunks (blocks, steps, checks, provisional items), the Standing reviews and "How this file works" stay exactly as they are; a chunk leaves only through `/chunk-done`.

1. Ask the `todo-keeper` agent to tidy `_USER_REVIEW/TODO.md`. Tell it, in one or two lines, what this session finished or dropped, if anything.
2. Pass on its lines in your report (Done, Questions for you, Status). Anything it was unsure about goes under Questions for you, numbered from Q1.
