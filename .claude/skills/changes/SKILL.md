---
name: changes
description: Suggest the summary (Added X, Updated X with Y, Fixed X) and the git release command (--minor, --major or --hotfix) for the user's changes. Use when the user asks what to commit, for a commit message, or for release notes. Never commits.
---

# Change lines

Ask the `change-logger` agent for the lines: a minor update by default, a major release summary if the user mentioned a release, or a hotfix if they mentioned a fix to `main`. Show the user its lines and the `git release` command exactly as it gives them. Do not run the command; the user runs it.
