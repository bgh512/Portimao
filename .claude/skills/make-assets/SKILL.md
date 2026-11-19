---
name: make-assets
description: Check a program's pixel-art masters and regenerate every icon and header from them. Use when the user has added or remade a master (icon_1024.png, icon_32.png, header_1920x640.png), or asks to regenerate, rebuild or update the app icons, favicon or header.
---

# Make assets

The rules are in `style/rules/ASSET_STYLE.md`. Masters live in `assets/master/` of the project, or of the sub-project they belong to; everything made from them goes to `assets/generated/`.

1. Find the assets folder: `assets/` in the project root, or the sub-project's `assets/` if the user means one (look for `*/assets/master/`). If there is no `master/` folder, tell the user the layout from `ASSET_STYLE.md` section 3 and stop.
2. Build:
   `sh style/setup/run_tool.sh enforce/tools/image_maker.py build <assets folder> --name <program>`
   The name is the program's name in snake_case, used in the icon file names. Without `--name` the folder that holds `assets/` is used.
3. Lines with an `IM` code are problems, and nothing was written. Explain each in plain words and what to change in the master or its prompt (`ASSET_STYLE.md` section 2). Never edit a master yourself.
4. Lines with `note:` are fixes the script made (resizing, shifting, merging colours). Pass them on in one line each.
5. Look at `assets/generated/master/icon_1024.png` and one small size such as `linux/hicolor/32x32/apps/<name>.png`, and tell the user if anything looks wrong.
6. Never edit files in `assets/generated/`; they are rewritten on every build. To check one new master without building, run `... image_maker.py check <master>`.
7. Finish with your usual report (Done, Questions for you, Status).
