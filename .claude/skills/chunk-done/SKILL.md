---
name: chunk-done
description: Close a chunk of _USER_REVIEW/TODO.md once the user accepts it as built - work from its Closing note, ask about any file it shares with another open chunk, run the release its Order table row names (only this chunk's files; a major line is given for the user to type), or note that its files already went out, then have small helpers delete the chunk, update the Order table and add the new words to the glossary, and list each next row's prompt to copy.
argument-hint: "[chunk, e.g. A4]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Agent, Bash(git release --minor *), Bash(git release --hotfix *), Bash(git status --porcelain *), Bash(git log -1 *), PowerShell(git release --minor *), PowerShell(git release --hotfix *), PowerShell(git status --porcelain *), PowerShell(git log -1 *)
---

# Close a finished chunk

The user has accepted a chunk of `_USER_REVIEW/TODO.md` as built. The chunk to close: $ARGUMENTS

With no chunk named, close the one this session was started on (its prompt names it). If the conversation does not say which, ask and change nothing. The session is usually fresh (the user typed `/clear` first): work from the to-do alone, above all the chunk's Closing note.

## 1 Before changing anything

- Plan mode is on: change nothing, and say "Plan mode is on: press Shift+Tab to leave it, then type /chunk-done again."
- Grep the to-do's headings, then read only the Order table, the chunk and the parts the reply needs. Read them just before anything changes: another session may be editing the to-do at the same time.
- The chunk is not in the to-do: say so and change nothing.
- The chunk has no Closing note (the line `Closing note:` at its end): its last session has not finished, or the chunk runs over several sessions. Ask whether the whole chunk is finished, with its mini chunks, and change nothing until the user says. If it is, ask for the release summary in one line, or offer one from the chunk's title.
- The chunk still has items under "Provisional (ideas; ask before building):" that the user has not answered: ask about each (it was done here, give it its own chunk later, or back to Ideas), and change nothing until the user says. Each answer goes to the helper in step 4.

## 2 The chunk's files

The chunk's release takes only the files on its list, `_USER_REVIEW/logs/chunks/<letter>.txt`, which the hooks write: one file per line, a file Claude edited as its name alone, any other as its name, a tab, then `seen during the turn` or `unsure`. Skip this step when the Order table's Release cell says none.

- Read this chunk's list, and the list of every other chunk still in the to-do (Glob `_USER_REVIEW/logs/chunks/*.txt`; a list whose chunk is not in the to-do is left over, so ignore it).
- Already released: run `git status --porcelain -- <each file on the list>`. Nothing on the list has a change left (every file went out with other releases): skip the questions below and step 3; run `git log -1 --format=%s -- <the files>` for the version that took them last, and the reply says "already released in V<version>".
- A file that is also on another chunk's list, or is marked `unsure`, may hold another tab's unfinished work. Ask about each in plain words, numbered from Q1, and release nothing and change nothing else until the user answers:
    - on another list: "B13 also changed shell.js: release it now with B13's part, or wait for B13?"
    - `unsure`: "shell.js changed while another tab was working: is it this chunk's (release it now), or does it wait?"
- "Wait": take that file's line out of this chunk's list with Edit, and nothing else. The file then goes out with the other chunk's release.
- "Release it now": leave the list as it is.
- There is no list (the session's first prompt named no chunk): say so in one line; the release is then given to the user (step 3), without `--chunk`, with the warning that it takes every change in the folder.

## 3 The release

The kind of release is the chunk's Release cell in the Order table (minor, hotfix, major or none); the Release block gives the command's shape when the cell is missing. The summary is the one in the Closing note; fill any placeholder left from it, or ask and release nothing until the user answers. The line ends with `--chunk <letter>` (unless step 2 found no list). Release none, or already released: skip this step.

- minor or hotfix, with a list from step 2: run it yourself, typing `/chunk-done` was the user's yes. Run it alone, in exactly one of these forms (the command hook lets nothing else through), with the longest timeout the shell allows (10 minutes), as a project's release hook may build files:
    - `git release --minor "<summary>" --chunk <letter>`
    - `git release --hotfix "<summary>" --chunk <letter> --yes`

  The summary is in double quotes, with no `"`, `$`, backtick or backslash in it, and does not start with `/` (Git Bash on Windows would turn it into a folder path): write "chunk-done ..." rather than "/chunk-done ...".
    - The output says `committed V<version>`: keep the version for the reply and go on.
    - Anything else (an error, no network, nothing to commit, nothing to release): leave the chunk in the to-do, skip steps 4 and 5, and say in one plain sentence what went wrong and what to do, from the release's own last lines.
- Anything else: major, no list, a condition this session cannot settle ("only if anything was fixed"), or another command (such as `git guide release`): run nothing; the reply gives the line for the user to type.

## 4 The helpers

Hand the edits to two small helpers, started together with the Agent tool and `model: haiku`, and wait for both. Give each exactly what to do; neither decides anything.

- **The to-do:** a `general-purpose` agent, told to read `_USER_REVIEW/TODO.md` just before editing it and to make only these edits with Edit:
    - Delete the chunk: its heading (`#### A4 ...`) and everything under it up to the next heading, its Prompt, Release and Close blocks, steps, mini chunks, provisional items, checks and Closing note included.
    - In the Order table, delete the chunk's row, take the chunk out of every other row's "Waits for" (a cell left empty becomes "–"), and put `**next**` in the Now cell of every row whose "Waits for" is "–" (rows already marked keep theirs, `**next\***` included).
    - Each provisional item the user answered in step 1: its own chunk goes under "Later (order to be decided)" as one line; back to Ideas goes under its topic in "# Ideas" of `_USER_REVIEW/scratchpad.md`.
    - Never edit between the style guide's marker lines (`<!-- >>> style guide ... -->` to `<!-- <<< style guide -->`), renumber no chunk, and change nothing else.
- **The glossary:** the `glossary-keeper` agent, given the new words from the Closing note with what each meant. It takes only two kinds: computer science words the user met (hook, agent, class, function...) and words the project defined (a precise term it fixes, or an abbreviation); an obvious phrase is left out. No such words: skip this helper.

A row for one of the user's own tasks goes only when the user says the task is done: then tell the to-do helper to take it out, its name from the "Waits for" cells and its line from the chunk's "Before this, you:". The chunk was the last of its thread: ask whether the thread's heading and notes go too, and tell the helper only once the user says.

## 5 Reply

The working rules' report:

- **Done:** one line: the chunk closed and the version released (`Released V3.4 with --minor, only A4's files`), or "already released in V3.3". A second line for the words the glossary took, if any. A release that stopped: the chunk is still open, and why.
- **Questions for you:**
    - Only when step 3 ran nothing (and the files were not already released): the release line, in its own `text` block. A condition goes in a few words above the block. Release none: say "No release for A4." instead of the block.
    - Unless the release stopped, under the line "Type /clear, check that plan mode shows (Shift+Tab), then paste a prompt.": each row now marked **next** or **next\*** whose Who is Claude or Claude with you, as its step's name and then its Prompt block in its own `text` block (for a chunk split into mini chunks, the first mini chunk not yet done). Rows marked **next\*** say which device they share. Then one line naming the rows marked **next** whose Who is You, with what the user does in each.
    - Anything asked in steps 1 to 4, numbered from Q1.
- **Status:** Ready.
