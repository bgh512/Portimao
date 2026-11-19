---
name: guide-change
description: Change the central style guide from inside this project - take the pass that lets this one session edit style/, have the user type git guide start, make the change so that it holds in any project, and give the git guide release line.
argument-hint: "[what should change in the guide]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Change the guide from this project

The user wants the style guide itself changed, here, in this project's `style/` folder. What they asked for: $ARGUMENTS

Only one session on the laptop may do this at a time. That session holds the pass.

## 1 Take the pass

- Run exactly: `sh style/setup/run_tool.sh git/guide_changer.py open ${CLAUDE_SESSION_ID}`
- It says another project holds the pass: give the user that line as it is, and stop.
- It says this is the guide's own repository: no pass is needed there; go to step 3.
- Otherwise give the user this one line to type in the terminal, in its own `text` block, and wait for them to say it is done:

```text
git guide start
```

- Never run `git guide` yourself. An edit under `style/` is refused until the user has typed it.

## 2 Before editing

- Nothing said what should change: ask, and edit nothing.
- Check the change would hold in any project. Anything true only here (this project's name, its folders, its own words, its edge case) goes into `.style/PROJECT_STYLE.md` instead, and nothing in the guide names a project.
- Plan as the working rules say: a one-line plan for a small change, the plan file for a larger one. Bigger guide work (a new tool, a reworked section) is not done here: note it in `_USER_REVIEW/FEEDBACK.md` and say so.

## 3 Make the change

- Edit the files in `style/`, never the copies the sync makes (`.claude/skills/...`, `.claude/agents/...`): those follow at the release.
- A rule or tool taken out: write it into `style/notes/V<next version>.md` (the next whole number after `style/VERSION`; make the file if it is missing, laid out as the newest one there), so projects that relied on it are told.
- A change to a tool comes with its test in `style/tests/`.
- The files you edit in `style/` are formatted when the turn ends, as project files are; write them as you would any other.

## 4 Reply

The working rules' report. Under **Questions for you**, the release line in its own `text` block, with the summary filled in:

```text
git guide release "<summary>"
```

and below it one line: "To give the change up instead: git guide stop".
