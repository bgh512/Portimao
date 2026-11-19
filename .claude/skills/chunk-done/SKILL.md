---
name: chunk-done
description: Close a chunk of _USER_REVIEW/TODO.md once the user accepts it as built - delete it and its row in the Order table, mark next every row it unblocks, ask about any file it shares with another open chunk, add the session's new words to the glossary, and give the release line (which takes only this chunk's files) and the next chunk's prompt, each in its own code block.
argument-hint: "[chunk, e.g. A4]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Agent
---

# Close a finished chunk

The user has accepted a chunk of `_USER_REVIEW/TODO.md` as built. The chunk to close: $ARGUMENTS

With no chunk named, close the one this session was started on (its prompt names it). If the conversation does not say which, ask and change nothing.

## 1 Before changing anything

- Plan mode is on: change nothing, and say "Plan mode is on: press Shift+Tab to leave it, then type /chunk-done again."
- Grep the to-do's headings, then read only the Order table, the chunk and the parts the reply needs. Read them just before editing: another session may be editing the to-do at the same time.
- The chunk is not in the to-do: say so and change nothing.
- The chunk runs over several sessions (it says "one per session", or its prompt picks the work "this session"): ask whether the whole chunk is finished, and change nothing until the user says.
- The chunk still has items under "Provisional (ideas; ask before building):" that the user has not answered: ask about each (it was done here, give it its own chunk later, or back to Ideas), and change nothing until the user says. Then, before deleting the chunk, put each where the user said: its own chunk goes under "Later (order to be decided)" as one line; back to Ideas goes under its topic in "# Ideas" of `_USER_REVIEW/scratchpad.md`.

## 2 Change the to-do

- Delete the chunk: its heading (`#### A4 ...`) and everything under it up to the next heading, its Prompt, Release and Close blocks, steps, provisional items and checks included.
- In the Order table (columns Now, Step, Who, Waits for):
    - Delete the chunk's row.
    - Take the chunk out of every other row's "Waits for". A cell left with nothing in it becomes "–".
    - Put `**next**` in the Now cell of every row whose "Waits for" is "–" (rows already marked keep it).
- A row for one of the user's own tasks (Who: You, linked to the chunk it holds up) goes only when the user says the task is done; then take its name out of the "Waits for" cells too, and its "Before this, you:" line from the chunk.
- Never edit between the style guide's marker lines (`<!-- >>> style guide ... -->` to `<!-- <<< style guide -->`): the sync keeps that text up to date.
- Change nothing else. No chunk is renumbered here: letters change only when a set moves or a chunk is split, never in this command. The user may be typing the release in the terminal meanwhile, so touch nothing but the to-do, the glossary, for an idea sent back the scratch pad, and for a file that waits (step 3) this chunk's own list.
- The chunk was the last of its set: ask whether the set's heading and notes go too.

## 3 The chunk's files

The chunk's release takes only the files on its list, `_USER_REVIEW/logs/chunks/<letter>.txt`, which the hooks write: one file per line, a file Claude edited as its name alone, any other as its name, a tab, then `seen during the turn` or `unsure`. Skip this step for "Release: none".

- Read this chunk's list, and the list of every other chunk still in the to-do (Glob `_USER_REVIEW/logs/chunks/*.txt`; a list whose chunk is not in the to-do is left over, so ignore it).
- A file that is also on another chunk's list, or is marked `unsure`, may hold another tab's unfinished work. Ask about each in plain words, numbered from Q1, and give no release line until the user answers:
    - on another list: "B13 also changed shell.js: release it now with B13's part, or wait for B13?"
    - `unsure`: "shell.js changed while another tab was working: is it this chunk's (release it now), or does it wait?"
- "Wait": take that file's line out of this chunk's list with Edit, and nothing else. The file then goes out with the other chunk's release.
- "Release it now": leave the list as it is.
- There is no list (the session's first prompt named no chunk): say so in one line, and give the release line without `--chunk`, with the warning that it takes every change in the folder.

## 4 The glossary

After the to-do is changed, start the `glossary-keeper` agent with the technical words this session used with the user: the project's own words, and any workflow or tool word the user asked about or used in a way that seemed off. One short line of meaning per word, as it was used here. No such words: skip this step.

## 5 Reply

The working rules' report, with the two blocks under Questions for you:

- **Done:** one line: the chunk closed and the rows now marked next. A second line for the words `glossary-keeper` added, if any.
- **Questions for you:**
    - The release line, in its own `text` block: the one given for this chunk at the end of its session, if this conversation holds it; otherwise the command in the chunk's Release block. Fill a placeholder (`<part>`) from what the session built, or ask. A condition on the Release line ("only if anything was fixed") goes in a few words above the block. "Release: none": say "No release for A4." instead of the block. The line ends with `--chunk <letter>` (add it when the Release block lacks it, unless step 3 found no list). When step 3 found nothing shared, say above the block: "The release takes only this chunk's files; you can /clear at once."
    - The next prompt, in its own `text` block, under the line "Type /clear, check that plan mode shows (Shift+Tab), then paste this prompt.": the Prompt block of the first row in the Order table marked **next** whose Who is Claude or Claude with you. Then one line naming any rows marked **next** whose Who is You, with what the user does there.
    - Anything asked in steps 1 to 3, numbered from Q1.
- **Status:** Ready.
