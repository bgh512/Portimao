---
name: feedback-send
description: Send the agreed entries of _USER_REVIEW/FEEDBACK.md to the style guide as GitHub issues - list the entries not yet sent, and on the user's yes file each as an issue on the guide's repository, labelled by guide file, and write the issue number beside the entry.
argument-hint: "[all, or entry numbers, e.g. 1 3]"
disable-model-invocation: true
allowed-tools: Read, Grep, Edit, Write, Bash(gh auth status*), Bash(gh issue create *), Bash(gh issue list *), Bash(gh label create *), Bash(git -C style remote get-url origin), Bash(git remote get-url origin)
---

# Send feedback to the guide as issues

The user wants the entries of `_USER_REVIEW/FEEDBACK.md` that they agree with filed as issues on the style guide's GitHub repository. What they typed after the command: $ARGUMENTS

An issue is outside the project and cannot be taken back, so nothing is sent before the user says which entries go.

## 1 Before sending anything

- Plan mode is on: change nothing, and say "Plan mode is on: press Shift+Tab to leave it, then type /feedback-send again."
- Find the guide's repository: `git -C style remote get-url origin`; in the style guide's own repository (no `style/` folder), `git remote get-url origin`. Take `<owner>/<name>` from the address. No GitHub address: say so and stop.
- Run `gh auth status`. `gh` is missing or not signed in: say "GitHub's command line tool is not signed in: run gh auth login in a terminal, then type /feedback-send again." and stop.
- Read `_USER_REVIEW/FEEDBACK.md` just before using it. An entry is a bullet (`- <date> <section>: ...`, with any lines indented under it) below a `## <guide file>` heading. An entry that ends with an issue number, `(#12)`, was sent already. Never read the text between the style guide's marker lines as an entry.
- No entry without a number: say "Every entry has been sent." and stop.

## 2 Ask which entries go

List the entries not yet sent, numbered from 1, each as one line: its guide file heading, its date and its first sentence. Then ask one question, Q1: send all (a), only some (b, the user gives the numbers), or none (c). When the user typed "all" or numbers after the command, that is the answer: show the list and go on.

Send nothing until the user has answered. An entry the user wants changed first is changed in the file, shown again, and sent only on their yes.

## 3 File each issue

One entry at a time, in the order of the file:

- The label is the entry's `## ` heading, as written (for example `Tools and hooks`). Make sure it exists: `gh label create "<heading>" --repo <owner>/<name> --color 0e8a16 --force`.
- The title: `<section>: <what happened>`, the entry's first sentence, cut at about 70 characters, without the date.
- The body, written to a file in your session scratchpad: the whole entry as it stands in `FEEDBACK.md`, then a last line `From project: <the project folder's name>, guide V<the number in style/VERSION>`.
- `gh issue create --repo <owner>/<name> --title "<title>" --body-file <the file> --label "<heading>"`. It prints the issue's address; the number is its last part.
- Straight away, before the next entry, write the number at the end of the entry's last line in `FEEDBACK.md`, as ` (#<number>)`. Read the file again first if anything else may have edited it. The entry stays in the file.
- A command that fails: stop, say what failed in one sentence, and leave the entries not yet sent as they are. Never send an entry twice: an entry with a number is never sent again.

Never edit between the style guide's marker lines, and change nothing else in the file.

## 4 Reply

The working rules' report:

- **Done:** one line per issue filed: its number, its label and its title.
- **Questions for you:** anything asked above, numbered from Q1, or "None".
- **Status:** Ready.

## In the style guide's own repository

The guide's sessions start from the open issues, not from a copied file: `gh issue list --state open` (add `--label "<guide file>"` for one file). An issue is closed by the release that acts on it; the projects' check sessions then remove the entries whose issue is closed.
