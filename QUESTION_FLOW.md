# Portimao question flow (V2.26)

Every question in the order it is asked, with where each answer leads. The question text is the text on screen.

**How to read it**

- The questions are asked in Portimao's window. If the window cannot open, nothing is asked: a message says why and what to do (in the Mac app, with a **Copy details** button to send the details with the Mac problem form).
- **The guide** on the left of the window lists the steps, numbered, one line each, under the names of the stages: **Import** (steps 1 to 4, sections 1 and 2 here), **Set-up** (5 to 9, section 3), **Experiment processing** (10 to 13, section 4), **Experiment export** (14 to 16, section 5), **Dataset figures** (17 to 20, sections 6 and 7) and **Dataset export** (21, section 9). The guide has four levels, largest first: the stage name, the steps under it, then in the open step the explanations and the question. Only the stage of the step open lists its steps, its name large and bold; the others show their name a little smaller and paler, with the numbers of their steps and a tick once they are passed. In the stage shown, a step done has a tick, a step passed without being asked (the previous processing of a dataset never opened, the OD values when you do not give them) stays in the list, greyed, with "· not needed this run", and the steps to come are paler.
- **The step open** sits under its line, marked ▸: what was said since your last answer (the explanations in a light grey, the messages), then the question in pink, larger than the rest, then its answers. The stage name is not repeated there. What was said before your last answer folds away when the next question is asked; all of it stays in the run's log.
- **Answers are clicked**, not typed:
    - something done on the plot or in the boxes above it (2.1, 4.4, 4.6, 5.1): one big **Continue** button (in 2.1 with **Export full + trimmed csv** and **Export trimmed csv** above it, buttons of the same size);
    - a yes or no question: **Yes** and **No**, one above the other;
    - a numbered list: a button for each choice; a long list in two columns;
    - several choices from a list: a tick button for each, then **Continue** (greyed while none is ticked); the choices offered at first are ticked, and where the order matters it is the order you tick them in;
    - a number or a name, the only answers typed: a box that starts with what Continue alone gives (the default, with its unit in the question), then **Continue**, or Enter in the box, with "Type a number, then click Continue or press Enter." under it;
    - a table: **Confirm** under it.

  The answer Enter gives is the highlighted button, which holds the keyboard. In this list, `(Y/n)` and `(y/N)` say which of Yes and No is highlighted (the capital letter), `(1/2/3)` with a number in bold which choice is, and `[value]` what the box starts with (`[skip]`: empty, which leaves the answer out). The answer clicked is written under the question, after an arrow.
- The defaults shown here are the standard settings, offered for a dataset you have never run. Once you have started a run, your answers, your OD values and event labels among them, are saved in a small file inside the data folder (`portimao_settings.json`), and the next time that dataset is opened you choose whether to load them (**1.3**), on this computer or on another one the folder is copied to.
- After an answer that cannot be used (a number out of its limits), one line in red says what to type, and the question waits for the next answer.
- Some answers are typed in a table, which opens in the step under the last few lines of its text: one row per file (the OD values, 3.2.1) or per event (the event labels, 3.3). Click a cell and type, or select what is there and type over it; Tab moves across and Enter moves down. A cell that cannot be used turns red. Press **Confirm** under the table when it is filled in. If a cell is still wrong, or a label is empty, one line names it and the table stays open; the OD table can be confirmed with cells left empty (3.2.1). The grey text of a table (its headings, the file names, the text in the file) is light enough to read on the dark card, and what you type is bold in a plain font. A row of **Symbols** (µ, ⁻¹, ₂ ...) is under a table and under a box for a name.
- **Going back to an earlier step.** A change in the boxes above the plot that belongs to an earlier step opens that step in the guide: the tabs of the Time regions box belong to step 4 (Trim / Ignore), 11 (Ox / Red) and 13 (Averaging); Edit ODs to step 7 (OD values) and Edit labels to step 9 (Event labels); the fit, the background, the spectra, the Haem decomposition tick, Build a fit and Keep to compare to step 10 (Haems); the Δψ box to step 12 (Δψ); the journal, the width, the height and Export master to step 14 (Figure). How the haems, the OCR and the labels are shown, the angle of the labels and the order of the panels belong to every step, and open none. The step waited at then reads **→ ... ← you were here**, the step opened says so above its messages with a few words on where to change it, and a **Back to** *step* button takes the place of the answers (the trim step keeps its two export buttons above it): click it to answer the question waiting. A click on the line of a step done opens it in the same way. A change that belongs to a later step ticks that step, as done: the guide is a guide, and the steps can be done in any order.
- The **Help** button under the answers is greyed out for now.
- **Yes → / No →** says which question comes next. **Next** means the next question in this list.
- In sections 1 to 5 and 9 the numbers on screen are the numbers here (all but 5.8, which is still numbered in the order asked). A question asked again keeps its number, and when a question is skipped the next one keeps its own, so 3.3 follows 3.2 when the OD values are not asked. A question asked inside another's step shows that step's number: the name of each component shows 4.1.7, replacing a fit file 4.1.9. In sections 6 and 7, the numbers here are for reference: on screen they are given in the order the questions are asked, so when a branch is skipped the later numbers move up, and every "Do you accept...?" question takes a number of its own.
- A "Do you accept...?" question with one way to change is a yes or no question, `(Y/n)`: the grey line just above it says what **No** does ("Click No to change the labels again."). One with more ways to change is a numbered list starting with **1) Yes, accept**, which moves on; its other answers (**2) No, ...**, and **3**, **4** ... where there are more) each say what is asked again, with your last answers as the defaults.
- The plot on the right is redrawn after each step marked **(plot)**. You can flick through the files with the arrows or the drop-down above the plot at any time while a question waits. The file shown and the one on each side of it are redrawn at once; any other file is drawn when you go to it, with its last plot under the **Plotting data …** sign meanwhile (clicking a cell of a table shows its file in the same way). From section 6 on, every file shows the plot saved for it (after **5.9**); a file whose plot could not be saved says so.
- The **boxes** above the plot, in one row under the file name and its arrows, show what the run uses. Every question that sets one of them says so, and it can be changed there at any time without typing the answer again:
    - **Time regions**: three tabs, **Trim / Ignore**, **Ox / Red** and **Averaging**, the one pressed having its edges on the plot and its numbers in the box (section 2, 4.C and 4.E). The guide presses the tab of its step (2.1, 4.4, 4.6). A tab can be pressed at any time: its edges come onto the plot (Trim / Ignore on the whole recording, with the edges in use as red dashed lines; the other two on the processing plot), and the change is used when you press another tab, or answer the question that waits. The edges of the step that waits stay as you left them meanwhile. A changed trim keeps the regions and the windows at their minutes; nothing is exported again by itself (press an export button in the trim step).
    - **View**, one line each, in this order: **OCR as** (how the OCR is shown) with its **per OD** box, **Haems as** (how the haems are shown) with its **per OD** box, **Labels as** (what the event labels show), the **Label angle** of the event labels (0 to 90°, 45 at first), then the **Edit ODs** and **Edit labels** buttons side by side. Edit ODs is always there, so OD values can be given later even after answering No at 3.2.
    - **Haem decomposition**, with its tick as the title (ticked when the haems are worked out and shown), in this order: **Spectra** (the spectrometer whose spectra hold the haems), the **Scatter** (the background fitted under the haems) with **ⓘ** for its formula, the **Fit**, **Build a fit** (with **Save fit**) beside **Do PCA**, and **Keep to compare** (with **Keep old** and **Keep new** under it while one is kept, and beside them the switch **Side by side / Overlaid**: side by side shows the kept one as a plot of its own headed Old on the left of the plot in use, headed New; overlaid draws it faint and thin under the plot in use, drawn bold; side by side at first, and the choice is kept with the dataset).
    - **Δψ**, with its tick as the title: the numbers of Δψ, shown while it is ticked (4.D). The tick can be clicked only while Δψ can be worked out.
    - **Figure**: the **Journal**, the **Width** and the **Height** of the figure of each file, the **Export master** button and the **Standard order** button.
    - The **panels** of the plot of a file can be moved: while the boxes can be used, a small up and a down arrow sit left of each panel, and a click moves that panel one place (the arrow that cannot be used, up on the top panel, is paler). No question is asked: the plot is redrawn at once and one line in the terminal says the new order. The order holds for every file and for the figure saved for each, and is kept with the dataset. A panel that comes later (a haem ticked since, Δψ switched on) is drawn just above the panel that follows it in the standard order, or at the bottom. **Standard order** puts the panels back: oxygen, OCR, the haems a then b then c, Δψ. The arrows are away while edges are dragged on the plot (trimming, the regions, the averaging windows) and while the plot is being redrawn.
    - **Spectra** is shown only when your files share more than one spectrometer (Cyt and NADH). Picking the other one works the haems out from its spectra.
    - **Haems as** swaps the haems between ΔD (mOD), the change from the start; % oxidised (reduced region = 0 %, oxidised region = 100 %); and Absorbance (mOD). % oxidised is in the list only when at least one file has both regions (4.4); a file without both stays in ΔD, as its axis says. The choice holds for every plot of your files and for the figure saved for each file.
    - **per OD** (beside Haems as) scales the haems by OD. The box is shown only once you have entered the OD values of every file (3.2.1). It is greyed while the haems are in % oxidised, which has no per OD.
    - **OCR as** swaps the OCR between µM min⁻¹; % of the range; and % of baseline (the average in the baseline window = 100 %), in the list only once the averaging windows are set up (4.6). Its **per OD** box, shown once you have entered the OD values of every file (3.2.1), makes µM min⁻¹ the OCR per OD (µM min⁻¹ OD⁻¹); it is greyed for the two % views, which have no per OD. A file without a baseline (less than 10 s of data before its first addition, or no addition) keeps its usual OCR, as its axis says, and one line says so. The choice holds for every plot of your files and for the figure saved for each file.
    - **Labels as** swaps the event labels between **In the chamber** (the concentration in the chamber after the addition, `400 µM KCN`; the standard) and **What was added** (`10 µL of 200 mM KCN`). An event with no stock and volume shows its concentration in the chamber either way, and one with no concentration its label alone. The choice holds for every plot of your files, the figure saved for each file and the labels under the windows of the haem and OCR figure, and is kept with the dataset.
    - While your files are on the plot (sections 2 to 5), you can change it whenever a question waits. The plot is redrawn at once, the run uses the change, and the question goes on waiting.
    - **Label angle** sets the angle of the event labels on every plot and in the figure saved for each file. A number outside 0 to 90 turns the box red, with what to type under it.
    - **Edit ODs** and **Edit labels** open their step again in the guide (OD values or Event labels, with "you were here" on the step that waits) and its table (3.2.1 or 3.3), with **Confirm** above the **Back to** button; after Confirm the plot is redrawn and the guide goes back to the question that waits.
    - Unticking Haem decomposition leaves the haems out of the run. Ticking it, or picking a fit, works them out with the fit shown and ticks the box.
    - If a fit cannot be used, one line says why and the box goes back to what it showed.
    - A new journal, width or height redraws the plot only in section 5, the one plot drawn at the figure's size. Before that the change is kept for section 5.
    - The **Journal** list holds every journal of the `journals` folder. Choosing one makes the figure follow what it asks: the widths offered, the tallest figure, the text sizes, the panel letters, the font and the thickness of the lines.
    - **Export master** saves one page of the journal as a PDF in the results folder (`<file>_master_<journal>.pdf`): the figure of the file shown at its printed size, a box where its legend goes and grey lines where the text of the paper goes. It works in section 5, where that figure is on the plot; before that, one line says so. With **None** the page is Nature's. A journal whose page size is not known is shown on an A4 page, and the page says so.
    - The boxes are greyed out while you choose the folder, during the questions of 4.A.1, and from section 6 on.
- While the program draws a picture of its own (the components found from the data, the figures of sections 6 and 7), the **Plotting data …** sign is on the plot: a large spinning wheel on a yellow card in the middle of the plot, with "Plotting data …" under it in large letters. The same sign shows while a file is read or a plot redrawn, and whenever the program is still working on an answer or a Confirm 0.2 s after the click (after an OD value is confirmed, for example). It goes when the picture is shown or the next question is asked.
- Sections **1** and **2** are the import: your files, where the results go, and the parts of the files that are used. Section **3** is the set-up: what is known about each run (the OD values, the temperature and the labels). The experiment processing starts with section **4**.

---

## 1. Import: your files

| # | Question | Answer leads to |
|---|---|---|
| 1.1 | Choose the folder with the .paf files, then press Continue. | The folders in the program folder (in the Mac app, in the Portimao folder in your home folder) that hold `.paf` files are buttons, each with how many files it holds; the folder used last time is highlighted. Click one to highlight it, then **Continue**. **Other folder…** opens a box for the full path of another folder (it starts with the folder used last time; a folder can be dragged in), with **Browse…** beside it, which opens your computer's own folder picker, the one window that pops up. A folder that does not exist, or one with no `.paf` files, is refused: one line says what to choose and the question waits. Otherwise every file is read and listed, then **1.2**. |
| 1.2 | Choose the folder for the results, then press Continue. | Every folder inside the data folder is a button, with what it holds ("holds results of 12 of 12 files", "no results"); the results folder offered (`results` inside the data folder, or for a dataset opened before, as a message says, the results folder it used) is highlighted, and is first among them, marked "new folder", when it does not exist yet. **Other folder…** and **Browse…** work as at 1.1; a typed name without a path, such as `quadratic_scatter_results`, is made inside the data folder, so a second set of results can sit beside the first. A file, or a folder that cannot be saved to, is refused: one line says what to choose and the question waits. **1.2.1** if the folder already holds results of any of these files; otherwise **1.3** for a dataset opened before, or the standard plot is drawn **(plot)**, then **2.1** |

| # | Question | Yes → | No → |
|---|---|---|---|
| 1.2.1 | *(only when the folder already holds results of these files; above it: "results already holds results of 12 of these 12 files.")* Do you want to write over them? `(y/N)` | **1.3** for a dataset opened before, or the standard plot is drawn **(plot)**, then **2.1**; results written later replace those there | **1.2** again, with a free name (`results_2`) highlighted first among the buttons as a new folder, and the line "Choose another folder, or the new folder results_2." |

| # | Question | Yes → | No → |
|---|---|---|---|
| 1.3 | *(only for a dataset opened before; above it: "Its trim and ignore edges, OD values, labels, fit, regions, Δψ, windows and figure were saved with it. No starts it fresh, as a dataset never opened.")* Do you want to load the previous processing? `(Y/n)` | every answer saved with the dataset is offered as the default from here on; the standard plot is drawn **(plot)** with them, then **2.1** | the dataset starts from the standard settings, as one never opened: the standard edges, no OD values, the labels as written in the files, the standard fit, no regions, no Δψ, the standard windows and figure. A line says what was saved with it is replaced only when you start the run (9.1). The standard plot is drawn **(plot)**, then **2.1** |

The standard plot of every file is then drawn with no question asked: the set and measured oxygen, the OCR and the haems (as the change from the start), with the event labels as written in the file. A dataset saved with Δψ switched on (4.5) also has its Δψ panel (the lowest, unless you moved it) on the files with both regions, and a dataset saved with its panels moved is drawn in that order. The haems are worked out with the standard fit (the preset `bswitch_no2_mycobl_b557.csv`), or with the fit last saved for the dataset. If that fit is not in the `fits/` folder or cannot be read, or the files do not share the spectrometer it is used on, a message says the haems are not shown yet, and only the oxygen and the OCR are drawn. A dataset last saved without haems is drawn without them, and its Haem decomposition box offers the standard fit. The boxes then become usable: Haem decomposition is ticked when the haems are shown.

---

## 2. Import: trimming and ignoring

The last step of the import. Above the question, in grey, the key, its "=" signs lined up:

```
TRIM (orange)  = data not plotted or used for calculations
IGNORED (grey) = data plotted but not used for calculations
```

The plot shows the standard plot of the whole recording of each file (with the haems, when they are shown; the Haem decomposition box turns them on and off and picks their fit), with four edges (bars) on it: the trimmed start and end in orange (the parts trimmed away orange and hatched) and the ignored start and end in grey (the parts ignored grey, as they are on every later plot). Each edge has a handle above the plot with its minutes beside it, the trimmed ones in the top row and the ignored ones just under them. Moving an edge never draws the plot again.

- **Drag** an edge by its handle or by its line; over an edge the mouse becomes a two-way arrow. The shading follows at once, and the edge moves in steps of 0.1 min. A trimmed edge stops at the first or the last event, so no addition is cut away, and the ignored parts stay inside the kept part without crossing. Where two edges meet, the line takes the ignored one; the trimmed one is still taken by its handle.
- **Type** the minutes under **Trim / Ignore** in the Time regions box above the plot, on two lines: **Trim before** and **after**, then **Ignore before** and **after**, each a time on the whole recording (min), as on the time axis of this plot. The boxes always show the full times, so when the edges are opened again they show where the edges are on the whole recording, and you can trim or ignore again from there. Press Enter or leave the box. A number that cannot be used turns the box red, with what to type beside it; a number beyond a limit is kept at the limit.
- **Apply to all**, unticked when the step opens, so an edge moved or typed changes only the file shown. Ticking it copies the four edges of the file shown to every file once, to the same minutes from each file's own start or end, within that file's limits; while that file stays shown, a change moves every file too. It unticks itself when the next file is shown, so that file can be changed alone. Ox / Red (4.C) and Averaging (4.E) have the same tick, which works the same way. A file whose times differ from most files is marked **(own times)** in the drop-down.
- The edges start where they were left the last time the dataset was run; for a dataset never run, the first 5 minutes are ignored and nothing else. When the edges are opened again (the **Trim / Ignore** tab of the Time regions box at any later step, or going back at **5.8**), the limits they had are drawn as red dashed lines, so you can see how far you moved them.
- **Export full + trimmed csv** and **Export trimmed csv**, above Continue: the quick export, the only one before the experiment export. Each asks **3.4** (whether to write the spectra too) and writes the files with the edges as they are, so you can plot them outside Portimao: the trimmed data, and with **Export full + trimmed csv** the whole recording of each trimmed file too; then the step waits again. Nothing is asked unless you press one, so it can be skipped, and Portimao can be closed once it has written the files. The OD values and labels are in the workbook once you have typed them. Nothing is exported again by itself when the edges change later: the trim step opened again (the Trim / Ignore tab) keeps its two export buttons, to write new files.

| # | Question | Leads to |
|---|---|---|
| 2.1 | Drag the bars on the plot, or type the times in the Time regions box. Check each experiment, then press Continue. (above it, in grey: the key, "Ticking Apply to all copies the times of the experiment shown to every experiment; it unticks itself when the next one is shown." and "The export buttons write the data of every experiment with these times, to plot it outside Portimao.") | **Export full + trimmed csv** or **Export trimmed csv**: **3.4**, then 2.1 waits again. **Continue**: the limits of every file are listed, the plot shows the data they keep **(plot)**, then **3.1**. |

---

## 3. Set-up: temperature, OD values and event labels

The last part of the set-up: what is known about each run (the temperature, the OD values and the event labels). The OD values and event labels saved for the dataset (in `portimao_settings.json`) are offered as defaults. The plot is the standard plot, cut to the limits of section 2.

### 3.A Temperature and OD values

The temperature is asked first, of every dataset: one value for all its runs, kept with the dataset. Δψ (4.5) is worked out with it; nothing else uses it. It is the same value as the Temperature of the Δψ box (4.D): changing one changes the other.

| # | Question | Leads to |
|---|---|---|
| 3.1 | What was the temperature of the runs (°C)? `[37]` | a number from 0 to 100; then **3.2** |

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.2 | Do you want to provide OD values? `(y/N)` (above it, in grey: "Scaling by OD divides the OCR and the haems by dilution factor × OD × volume; the View box above the plot then offers per OD for each.") | **3.2.1** | **3.3** (no OD scaling, until Edit ODs gives the values) |

The OD table opens on the terminal side, with one row per file and a column each for the OD, the volume (mL) and the dilution factor. The values stored for a file are filled in, and the dilution factor is 1 when none is stored. Clicking a cell of a file shows that file on the plot. Above the table, in grey, the key, its "=" signs lined up:

```
OD          = measured OD of the sample
Volume (mL) = total volume of cells spun down
Dilution    = any dilution factor after additions
```

| # | Question | Leads to |
|---|---|---|
| 3.2.1 | Fill in the table, then press Confirm. | If a cell is not a number above 0, one line names those cells and the table stays open. Otherwise the table closes and the values of every file are listed, a missing one as "missing". With every value in, the next step is **3.2.2**. With cells left empty, a warning names them ("OD values are missing for: a: volume, b: OD. The OD scaling stays off until every file has its values: Edit ODs in the View box fills them in."); the values typed are kept, nothing is scaled by OD, and the next step is **3.3**. |

**Edit ODs** in the View box opens this table again at any later step, also after No at 3.2 or while values are missing; after Confirm the same warning is given while a value is missing, and the OD scaling comes on once every value is in (or goes off again while one is missing). Once every value is in, the View box above the plot shows the **per OD** boxes beside OCR as and Haems as. The plot follows them from here on, and so does the figure saved for each file.

| # | Question | Leads to |
|---|---|---|
| 3.2.2 | Use the View box to show the OCR and the haems per OD. **Continue** (above it, in grey: "The OCR is now shown per OD. You can change it under OCR as in the View box at any time.") | Asked once every OD value is in. **OCR as** is set to per OD before it, unless the dataset was saved with the OCR as % of the range, which it keeps (the grey line then says "as % of the range"); the plot is redrawn **(plot)**. **Continue**: **3.3** |

### 3.B Event labels

If no file has any event, nothing is asked here and the next step is **4.1**.

The labels table opens on the terminal side: one row per event, under the name of its file, with the time of the event (min), the text in the file (grey, not typed in), the **Volume added (µL)**, the **Stock (mM)**, the **Chemical** (the label shown on the plot, in a wider box) and the concentration **In the chamber (µM)**. Each row starts as saved for the dataset, or else filled in from the text in the file: a number with a volume unit (nL, µL or mL; `ul` for µL) is the volume added, a number with a molar unit (nM, µM, mM or M, in any capitals; `1m` is 1 M) the stock, or the concentration in the chamber when the text gives no volume, and what is left the chemical, written tidily (`8ug ml-1` as 8 µg mL⁻¹). `1ul 8mm nd-011992` gives 1, 8 and nd-011992; `100uM KCN` gives KCN with 100 in the chamber. What cannot be worked out is left empty, and a text that names no chemical (`2 ul`) gives `IGNORE`. An event left out before reads `IGNORE`. Clicking a cell of a file shows that file on the plot. The **Symbols** row under the table types µ, ⁻¹, ₂ and the like into the cell last typed in.

- A number typed alone is in the unit of its column: mM for the stock, µM in the chamber; a typed unit (nM, µM, mM or M) is also taken. Once a row has both a stock and a volume, its concentration in the chamber fills itself in, in green, and cannot be typed in: stock × volume ÷ 5 mL (the chamber), the same chemical added again in a file adding up (10 µL of 200 mM KCN gives 400 µM, the next 800 µM). The maths is in `MATHS.md`, section 8.
- A row with no stock and volume takes a concentration in the chamber typed by hand, or none.
- A stock is always written in mM and a concentration in the chamber in µM, in the table and on the labels of the plots alike (1200 µM, not 1.2 mM).
- The chemical is kept as typed: only what the program fills in from the file is tidied.

| # | Question | Leads to |
|---|---|---|
| 3.3 | Fill the table in with the details of the additions, then press Confirm. (above it, in grey: "Type IGNORE as a label to not show it.") | An event labelled `IGNORE` (in any capitals) is left out, and its other cells are greyed out. If a chemical is empty, a stock, volume or concentration cannot be used, or a row has a stock without a volume (or a volume without a stock), one line names those cells and the table stays open. Otherwise the table closes, the concentrations are worked out, the labels of every file are listed (with what was added and the concentration in the chamber), one line says "Event labels saved! Edit labels in the View box above the plot changes them at any time." and the labels are drawn **(plot)**; then **4.1**. |

Confirm only confirms: there is no question to accept the labels, as **Edit labels** in the View box opens the labels table again at any later step, and the plot is redrawn after Confirm.

Going to another step while the table is open keeps it as it is. In the set-up, opening an earlier step puts the table away, and **Back to Event labels** brings it back as you left it. Opened with **Edit labels** (or **Edit ODs**), **Back to** *step* or a click on another step takes the table as it is, without checking it (a cell that cannot be used counts as empty), and redraws the plot; the next **Edit labels** opens it as you left it, wrong cells included. **Edit ODs** pressed while the labels table is open opens the OD table, and the labels table comes back as you left it once the OD table is confirmed.

### 3.C The export buttons of the trim step

The quick export is asked only from the two export buttons of the trimming step (2.1), the first time and whenever the Trim / Ignore tab is opened again; it is not offered after the labels. **Export trimmed csv** writes the trimmed data; **Export full + trimmed csv** that and the whole recording of each trimmed file.

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.4 | Do you want the spectra as csv files too? `(y/N)` (above it, in grey: "A workbook is written for each file (about *size*). The spectra as csv files are large (about *size*) and take a while to write."; and, after **Export full + trimmed csv** when no file is trimmed: "No file is trimmed, so this writes the same as Export trimmed csv.") No is highlighted the first time, then your last answer. | every file is exported with its spectra, then a message says where; the trimming step waits again | every file is exported without its spectra, then a message says where; the trimming step waits again |

The sizes are worked out for your files, less for a trimmed one: about 0.3 MB of workbook and 1.2 GB of spectra for each 100 MB `.paf` file. Each file is exported to its own folder in the results folder, `<results>/<file>/`:

- `<file>.xlsx`, with either button: the trimmed data (all of it for a file not trimmed), with the sheets **Measured O2** and **Set O2**, **OCR**, **Events** (the time, the text in the file, your label, the stock (mM) and volume added (µL), what the addition added and the concentration in the chamber (µM), and whether the event is ignored) and **Metadata** (your OD, volume and dilution, the trimmed and ignored edges in minutes, and the spectrometers). The experiment export (**5.9**) later writes this workbook again with its own results added.
- the spectra csv files, after Yes at 3.4: one per spectrometer and kind (`Cyt_transmiss.csv`, `Cyt_intensity.csv`, `Cyt_attenuation.csv`, and the same for `NADH`), wavelengths down and one column per spectrum; the workbook lists them on a first sheet, **Spectral data**.
- `full/`, with **Export full + trimmed csv**, only for a file you trimmed: the same for the whole recording (its spectra after Yes at 3.4). It does not record the edges, so it stays as it is when they change.

Nothing is scaled by OD, decomposed or averaged, and the ignored parts are included.

---

## 4. Experiment processing

The plot is the standard plot, cut to the limits of section 2, with the event labels of section 3. It is redrawn after each step marked **(plot)**.

### 4.A Haem fit

The haems on the plot are those of the import, worked out with the standard fit, the fit last saved for the dataset, or the fit you picked or built in the Haem decomposition box, with the scatter in that box. A message names that fit ("The haems are worked out with *fit*.", or "... with Your own haems: *c1_myco, bH_bswitch, ...*"); when the plot shows no haems yet (the dataset was last saved without them, the fit could not be used, or you unticked Haem decomposition) it says instead: "No haems are worked out yet: tick Haem decomposition to work them out with the fit shown, or leave it unticked to go on without haems." Nothing is asked about the fit: it is set in the box.

| # | Question | Leads to |
|---|---|---|
| 4.1 | Edit the haem decomposition using the Haem decomposition box, press Continue when ready. | **Continue**: with Haem decomposition ticked, **4.4** with the decomposition on the plot; unticked, **4.6** (no haems, unless you tick Haem decomposition later). Anything typed is answered with "Change the fit, the scatter or the spectra in the Haem decomposition box above the plot; press Continue when the haems look right." |

While 4.1 waits, the Haem decomposition box changes the decomposition, and the plot is redrawn after each change. Its parts, in this order:
- **Spectra** *(only when the files share more than one spectrometer)*: the spectrometer whose spectra hold the haems, Cyt or NADH.
- **Scatter**: the background fitted under the haems: **Rowan scatter** (the standard), **Palencia** (once called Valencia; a dataset saved with Valencia opens with Palencia), **Inverse** (flat + 1/wavelength), **Inverse²** (flat + 1/wavelength + 1/wavelength²) and **Linear** (flat + a straight line). The **ⓘ** button beside it shows the formula of the scatter picked, written as a textbook writes it (as in `MATHS.md` 1.3), with a line saying what its letters are; click it again to hide it.
- **Fit**: another preset or fit file of your own, each shown by its name without .csv; a preset may give itself a name of its own (the Rowan fit 11-2026, once `temp_fit_037v`; a dataset saved with the old name opens with it).
- **Haems as** (in the View box): ΔD (mOD), % oxidised (once a file has both regions, 4.4) or Absorbance (mOD), with **per OD** beside it when OD values were entered. In ΔD and in Absorbance the haem panels share one scale, so the size of a change can be compared between them (ΔD: the same range on every panel; Absorbance: the same height of range, around each haem's own level); in % oxidised each keeps its own.
- **Do PCA** (beside Build a fit): finds the components from the whole dataset with the questions of 4.A.1; they then become the fit in use.
- **Build a fit**: folds out a tick box for each haem of the library, the a, b and c haems each together with their type in front, at most three on a line (so the five boxes fit across a 1920 × 1080 screen); the boxes start with the haems of the preset in use. Ticking or unticking a box works the haems out with the ones ticked, and the Fit drop-down reads *Your own haems*. Ticking a haem with the same name as one already ticked (c1_myco and c1_037v are both Cyt cc) unticks the other, and the last box cannot be unticked; a note beside the height says so. Under the boxes, type a name and click **Save fit** (or press Enter) to save the haems ticked as a fit file of that name in the fits folder: it becomes the fit in use, is in the Fit list from then on, and the dataset is saved with it. A name already used by a preset or a fit file is refused with one sentence, so nothing is overwritten. Click the button again to fold the boxes away.
- **Keep to compare**: keeps everything as it is on the plot at the click (the fit, the background, the oxidised and reduced regions of every file and the numbers of the Δψ box), and a line in the box says which one is kept. Change the fit, the haems ticked, the background, the regions or a number of the Δψ box, and the kept one is shown on every file in one of two ways, chosen with the switch **Side by side / Overlaid** beside Keep new. **Side by side** (at first): the file worked out with the kept one is a plot of its own on the left, the same size as the plot in use on the right, and each panel has the same y range on both sides; the edges you drag, the arrows and the shading stay on the plot in use. The two plots are headed **Old** (the kept one) and **New** (the one in use), and the haem panels keep one scale on both sides. **Overlaid**: the kept (old) haems are drawn as faint, thin lines in the same colours under the new ones, drawn bold, and the kept Δψ the same way in the Δψ panel (4.D); the key under the plot says "faint = old (kept), bold = new". The choice is kept with the dataset. Under the plot, each haem in both has two numbers, largest / average: the largest and the average distance between its two traces, in the units of the haem panels; Δψ has the same two numbers in mV, over the spectra where both have a value. A file that had no regions when you clicked has no kept Δψ, and one sentence under the plot says so. While one is kept, Keep to compare is greyed and two buttons under it choose between the two, and either one takes the kept one away: **Keep new** carries on with what is on the plot; **Keep old** puts the kept fit, haems, background, spectrometer, Δψ numbers and regions of every file back in use (while you are still choosing the regions in 4.4, the regions stay as they are on the plot, and one line says so). The terminal says which one you carry on with. To compare again, click *Keep to compare* again. Each file takes about twice as long to draw while one is kept.

To leave the haems out, untick Haem decomposition; Continue then goes on without haems, to **4.6**.

#### 4.A.1 Components from the data (principal component analysis)

Asked when **Do PCA** is clicked in the Haem decomposition box while 4.1 waits (clicked at another step, one line says to go back to the processing to do it). All the spectra of all the files are analysed together, so the components are one set for the whole dataset. The boxes are greyed out until the questions are answered, and the fit list then includes a fit file saved in 4.1.9; 4.1 then waits again, with the components as the fit in use (or the fit as it was, after *No, keep the fit in the box instead*). The numbers keep counting up when a question is asked again, and each component name is a question of its own, so the numbers on screen can be higher than these. The files are read for their spectra (trimmed, without the ignored parts; this can take a moment). Once the components are made, the plot window gets a *PCA components* picture (one panel per component, coloured by the haem type it looks like) and a *PCA examples* picture (the best and worst described spectrum and their residuals) after the files **(plot)**. The **Plotting data …** sign is on the plot while they are made. They go when the decomposition is drawn.

| # | Question | Leads to |
|---|---|---|
| 4.1.1 | Where should the spectral window start (nm)? | **4.1.2** |
| 4.1.2 | Where should the spectral window end (nm)? | **4.1.3** (or this question again if the analysis cannot be run, for example the window is too narrow) |
| 4.1.3 | How many components should be found? (The data suggest *N*; use as few as describe the data, extra ones only fit noise.) | a whole number; the number used last time, or else the suggestion, is the default; then **4.1.4** |
| 4.1.4 | Do you want to rotate the components so each is as peak-like as possible (varimax)? `(Y/n)` | **4.1.5** |
| 4.1.5 | Over how many nm should the components be smoothed to remove their noise (0 for none)? (default 4, or the width used last time; at most a quarter of the window) | the components and the examples are drawn **(plot)**, with one line per component (type, peak, share of the change) and the residual, then **4.1.6** |

| # | Question | 1 → | 2 → | 3 → | 4 → |
|---|---|---|---|---|---|
| 4.1.6 | Do you accept these components? `(1/2/3/4)` | **4.1.7** | **4.1.3** (the number of components) | **4.1.1** (the window) | *No, keep the fit in the box instead*: back to **4.1**, the fit as it was |

| # | Question | Leads to |
|---|---|---|
| 4.1.7 | Do you want to name the components? `(y/N)` | yes: one question for each component, "What is component *N* (*type*, largest peak at *X* nm) called?", suggesting a name from its type such as *a-like* (a name that is empty, has a comma or is used twice is asked again), then **4.1.8**; no (PC1, PC2, ...): **4.1.8** |
| 4.1.8 | Do you want to save these components as a fit file in the fits folder? `(Y/n)` | yes: **4.1.9**; no: the decomposition is drawn **(plot)**, then back to **4.1** |
| 4.1.9 | What should the fit file be called (without .csv)? | the name of a preset is refused (one line says so and the question waits); if a fit file of that name exists, it asks "*name*.csv already exists. Do you want to replace it?" `(y/N)` (no asks for a name again); then the decomposition is drawn **(plot)**, then back to **4.1** |

### 4.B Trim and ignore times again

No question is asked: the trim and ignore edges stay movable with the **Trim / Ignore** tab of the Time regions box, at any step. There is no 4.3: the numbers of the later questions are kept.

### 4.C The oxidised and reduced regions

*(only when the haems are decomposed)* The oxidised region is a stretch of the run where the haems are fully oxidised, the reduced region one where they are fully reduced. Each haem's level in the two (its median there) is what its % oxidised is worked out from. The program never places a region: you pull each out on the plot, in red for oxidised and blue for reduced, or leave it as it is.

- Both regions start **not chosen**: one red handle at the left of the used part of the run reading "oxidised: not chosen", one blue handle at the right reading "reduced: not chosen". **Pull** a handle out, by the handle or its line, and the region opens from that side, shaded in its colour; its second edge then has a handle too, and the times of the region are written beside it. The edges move in steps of 0.1 min, and moving one never draws the plot again.
- **Type** the times under **Ox / Red** in the Time regions box above the plot, on two lines: **Oxidised from** and **to**, then **Reduced from** and **to**, in minutes as on the time axis of the plot. Press Enter or leave the box.
- An edge stays in the used part of the run (not trimmed, not ignored). Moved past the other edge of its region, it pushes that edge along. The two regions never overlap: an edge moved into the other region stops at that region's nearer side, so moved on past its middle it comes out on the far side.
- A region shorter than 10 spectra (5 s when a spectrum is taken every 0.5 s) counts as not chosen: its shading goes and its handle reads "not chosen" again.
- **Apply to all**, unticked when the step opens, so only the file shown changes. Ticking it copies the regions of the file shown to every file once, and while that file stays shown an edge set on it is copied too: each edge goes to every file at the same distance from the addition nearest to it, counted in order (1.5 min before the 3rd addition of the file shown is 1.5 min before the 3rd addition of every file), then kept within that file's own limits. An edge after the last addition goes instead at the same distance from the end of the used part of each file (1 min before the end to the end is 1 min before the end to the end on every file). A file with fewer additions keeps an edge that is not after the last addition. It unticks itself when the next file is shown.
- If you press **Ox / Red** at another step, or go back to the processing step later in the run, the regions are where you left them, on the same data even when the trim has changed. Changed there, they are listed when you press another tab or answer the question that waits.
- The regions are saved with the dataset (in `portimao_settings.json`), so they are on the plot the next time it is opened.
- The regions are optional. A file with both has each haem's oxidised and reduced level, and its haems can be shown in % oxidised (Haems as in the View box, and 7.2.2); a file with none, or with only one, cannot, and nothing else changes for it. Once a file has both, a message says: "The haems can now be shown in % oxidised: choose it under Haems as in the View box above the plot."

| # | Question | Leads to |
|---|---|---|
| 4.4 | Drag the regions out on the plot, or type the times in the Time regions box. Check each experiment, then press Continue. (above it, in grey: the key, "OXIDISED (red) = haems fully oxidised: each haem's level here is 100 %" and "REDUCED (blue) = haems fully reduced: each haem's level here is 0 %" with their "=" lined up, "Ticking Apply to all copies the regions of the experiment shown to every experiment; it unticks itself when the next one is shown." and "With no regions the haems cannot be shown in % oxidised; everything else is the same.") | **Continue**: the regions of every file are listed, then **4.5** (**4.6** when Δψ cannot be worked out). A file without both regions stays in ΔD; nothing is asked about it. A warning names the files that kept an edge of their own because they have fewer additions. |

### 4.D Δψ, the membrane potential

Δψ is worked out from how reduced the two b haems, bH and bL, are, at the temperature of 3.1 (the maths is in `MATHS.md`). It can be worked out for a file with both regions (4.4), when the fit has one bH and one bL. 4.5 is asked only when at least one file has both regions and the fit has the two haems. Otherwise nothing is asked and the run has no Δψ; for a dataset saved with Δψ switched on, a message says what it needs.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.5 | *(only when Δψ can be worked out)* Do you want to plot Δψ? `(y/N)`, or `(Y/n)` when the Δψ box is already ticked (above it, in grey: "Δψ is the membrane potential, worked out from how reduced bH and bL are.") | the plot is redrawn **(plot)** with a **Δψ (mV)** panel under the haems (or where you moved it to), the **Δψ** box is ticked and shows its numbers, and the terminal says "Δψ (mV) is worked out from the bH and bL haems, for the files with both regions, and drawn in its own panel:", then the formula written as a textbook writes it (Δψ = (E_H − E_L) ÷ β, with E_H = M_H1 − RT/F × ln(h ÷ n) and E_L = M_L1 − RT/F × ln(l ÷ n), as in `MATHS.md` section 6), a line saying what its letters are, and "It has gaps where bH or bL is less than 10 % or more than 90 % reduced. To compare two sets of numbers, click Keep to compare first."; then **4.5.1** | **4.6** (no Δψ in the run; the box is unticked) |
| 4.5.1 | Set the midpoints of bH and bL and the shift in the Δψ box, press Continue when ready. | **Continue**: **4.6**. Anything typed in the answer box is answered with one line saying to type the numbers in the Δψ box above the plot. |

The tick of the **Δψ** box switches Δψ on and off at any time while it can be worked out, and the plot is redrawn with or without its panel. At a later step, unticking it only takes the panel away and the step you are at stays open; ticking it, or typing a number in its box, opens the Δψ step, with "you were here" on the step you left.

The Δψ panel is the lowest panel of the plot of each file with both regions: one line, with gaps where bH or bL is less than 10 % or more than 90 % reduced, as Δψ cannot be given there. A file without both regions has no Δψ panel. The panel is also in the figure saved for each file (section 5), and Δψ is in the workbook of each file written in the experiment export (5.9). The limits of 10 and 90 % are the ones the program starts with.

The **Δψ** box holds the numbers of the method, and shows them only while Δψ is ticked. No question is asked: type a number, press Enter (or click away), and the Δψ panel is redrawn at once, with one line in the terminal saying what the numbers now are. The numbers are kept with the dataset. To see what a change does, click **Keep to compare** (4.A) first: the Δψ of before the change stays on the plot on the left, headed Old (side by side), or in the panel as a faint, thin line under the new one, drawn bold (overlaid), with the largest and the average distance between the two under the plot. Then click **Keep new** to carry on with the change, or **Keep old** to undo it.

- ***b*<sub>H</sub>** and ***b*<sub>L</sub>** (written as in the figures): the midpoint potential of each haem while the other is oxidised (mV); 40 and −20. After each arrow, greyed, is its midpoint while the other haem is reduced (−30 and −90): the program fills it in, and it cannot be typed in.
- **shift**: how far each midpoint falls when the other haem is reduced (mV); 70. Typing it refills both greyed numbers (a shift of 60 gives −20 and −80); typing a midpoint refills its own (bH 50 gives −20).
- **More options**, unticked, leaves the other numbers as one grey line ("share 0.5 · 37 °C · given between 10 and 90 % reduced"); ticked, they are boxes on two lines: the **Share** of the membrane potential that lies between the two haems and the **Temperature** of the runs (°C, the value of 3.1), then the two limits (**Given from** ... **to** ... **% reduced**).
- A number that cannot be used turns its box red, with one sentence under the row, and the number in use stays: something that is not a number; a share of 0 or less; a temperature outside 0 to 100 °C (as 3.1); a lowest limit that is not above 0 and below the highest; a highest limit that is not above the lowest and below 100.

### 4.E The averaging windows

An averaging window is a stretch before an addition that an average is taken over: it ends a set time before the next addition (the last one 0.5 min before the end of the recording), the level once things have settled after the addition before. The quick windows, which start a set time after their own addition, are hidden for now: they are not offered, and a dataset saved with them has them switched off.

The windows are placed around the events as they were left in 3.B: an event marked `IGNORE` gets none. Every window has the same length unless you set one on its own, so each moves with its addition in every file and one setting fits the whole dataset. The window before the first addition is the baseline, which every other window is compared with; it has the length and the time before the addition of the other windows unless it has its own.

The Averaging tab of the Time regions box holds, from the top:

- **Averaging windows**, a tick box: ticked when the step first opens on a dataset. Untick it for no windows: the windows go from the plot, the rest of the tab is greyed, nothing is averaged, and the figures of each file show none.
- **Use**, a numbered tick for each window of the file shown (the baseline has none): untick one to leave that window out. It is shaded grey with no edges, it is not averaged, its row stays in the Averages sheet with empty numbers, and the figures leave a gap.
- **Adjust region manually**, with a button for each window beside it (**Baseline**, **1**, **2** ...): ticked, it picks window 1, and you pick another with its button. Only the window picked (its button bold and pressed in) changes, on the file shown only, by dragging its edges or typing its numbers; the other windows are grey with no edges until picked, and **Apply to all** is greyed. With the last window picked, a note says its time is before the end of the file, and the second box sets that. Unticked, each window keeps what it was given until the next change of that number, which puts every window back to one value.
- **Region length (s)** and **Time before next addition (s)**: type the numbers in seconds, then press Enter or leave the box. They change every window, or the window picked while Adjust region manually is ticked. A window of 0 s is not taken.
- **Apply to all**: unticked as the step opens, so a change is made on the file shown only, and that file keeps windows of its own. Ticking it copies the windows of the file shown to every file once, and a change is made on every file while that file stays shown; it unticks itself when the next file is shown. The drop-down marks the files whose windows differ.

On the plot:

- The baseline is **shaded gold** on the plot of every file, with "baseline" and its length by its first edge; the other windows are **shaded blue**, 120 s long and ending 30 s before the next addition, or as they were saved with the dataset. They are over the plot only in this step; the steps before it show none.
- **Pull the start** of a window, by its handle or its line, to change its length; **pull its end** to change the time before the addition. Every window in the file follows (only the window picked while Adjust region manually is ticked), in steps of 5 s, and the plot is not drawn again. **Pull the end of the last window** to change how long before the end of the recording it ends (0.5 min unless changed).
- A window that **does not fit** is shaded red with hatching: a window that would start before its own addition, or a baseline shorter than 10 s. After Continue a warning names these windows for each file; they are left out of the averages.
- The windows are saved with the dataset (in `portimao_settings.json`), ticked or not, with each window set on its own or left out and each file fixed by hand.
- When none of the files has an addition, the step is not asked and one line says there are no averaging windows.

| # | Question | Leads to |
|---|---|---|
| 4.6 | Drag the windows on the plot, or type their numbers in the Time regions box, press Continue when ready. (above it, in grey: what the windows are, "The baseline (gold) is the window before the first addition; every other window (blue) is compared with it.", which edge to pull for what, "A change moves every window, on the file shown; ticking Apply to all copies its windows to every file, and it unticks itself when the next file is shown. Untick a number under Use to leave that window out (grey), or untick Averaging windows for none." and "Tick Adjust region manually to change one window of one file: pick it with the buttons beside it, then drag its edges or type its numbers; the other windows are grey until picked.") | **Continue**: one line says the windows chosen (or one line that there are none), one line names the windows set on their own and those left out, one the files with windows of their own, a warning names those that do not fit (not those left out), the plot is redrawn with the windows **(plot)**, then **5.1**. |

Three later figures need the averaging windows: the 2x2 grid (**6.3**), the time response (**7.1**) and the haem and OCR response (**7.2**). They use the windows chosen here and never ask for a window or a gap of their own. When you say yes to one of them and no windows are set up (Averaging windows unticked in 4.6, or no file with an addition), one line says "No averaging windows are set up, and this figure needs them.", and 4.6.1 is asked before the figure's own questions. It keeps this number wherever it is asked. The OCR as % of baseline is offered under OCR as only once the windows are set up, so it never asks.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.6.1 | Do you want to add them now? `(Y/n)` | **4.6** opens on the plot of every file, by itself (nothing else of the processing is asked again, and the boxes stay greyed out apart from the rows of the windows), with Averaging windows ticked; the guide opens step 13 (Averaging windows) meanwhile, then goes back to the figure. After Continue, with windows set up, the figure's own questions follow; with none still, one line says the figure is not made and the next figure is asked | one line says the figure is not made, and the next figure is asked |

Once windows are added this way they are the dataset's windows: the later figures do not ask, and they are saved with the dataset.

Each of the three figures uses one kind of window, with the baseline. While the quick windows are hidden only the settled windows can be set up, so 4.6.2 is not asked. With both kinds set up (once the quick windows come back), 4.6.2 is asked before the figure's own questions (after 4.6.1 when that was asked); it keeps this number wherever it is asked, and each figure remembers its own answer. With one kind set up nothing is asked: one line says the figure uses that kind.

| # | Question | Leads to |
|---|---|---|
| 4.6.2 | Which windows should this figure use? `(1/2)` 1) Settled, before the next addition; 2) Quick, after each addition | the figure's own questions |

The plots and the workbook of each experiment (section 5) show both kinds: the quick windows green, the settled windows blue and the baseline gold with "Baseline" written above it, and a **Kind** column in the Averages sheet.

---

## 5. Experiment export: the figure of each file

The figure saved for each file is drawn at once **(plot)**, at its real size and as it will be saved, with the standard settings or, for a dataset run before, the settings last saved for it. Every panel is in it:

- the set and measured oxygen, always;
- the OCR, always, as **OCR as** in the View box shows it: per OD (µM min⁻¹ OD⁻¹) as standard once every OD value is in (3.2.2), otherwise µM min⁻¹;
- while **Haem decomposition** is ticked, every haem of the fit, as **Haems as** in the View box shows them: ΔD, the change from the start, as standard (scaled by OD as well when its per OD box is ticked); unticked, no haem panels;
- Δψ (mV) as the lowest panel while the **Δψ** box is ticked, for a file with both regions;
- the event labels at the **Label angle** of the View box (45° as standard);
- the journal, the width and the height of the **Figure** box: Nature, 1 column wide and 0.5 of a page tall as standard.

Every change in the boxes redraws the figure at once. A message under the first one says so.

| # | Question | Leads to |
|---|---|---|
| 5.1 | Change the figure in the boxes above the plot, then click Continue. | **Continue**: **5.8**. |

The % of baseline (OCR as) is the OCR divided by its average in the baseline window (the window before the first addition, 4.6) × 100, so the baseline is 100 %; it is offered once the averaging windows are set up. A file without a baseline keeps its usual OCR (per OD if you entered OD values, otherwise µM min⁻¹), as its axis says, and one line says so.

How the haems are shown (**Haems as**): ΔD (mOD), the change from the start; % oxidised (reduced region = 0 %, oxidised region = 100 %), *only offered when at least one file has both regions (4.4)*; and Absorbance (mOD). There are no 5.2 to 5.6: the numbers of the later questions are kept.

- A file without both regions stays in ΔD, as its axis says, while the files with both are in %.
- A dataset saved with % oxidised opens with ΔD when no file has both regions any more.
- No concentration: only cells are measured, and a haem amount depends on the size of its shape; a dataset saved with concentration opens with ΔD.

### 5.E Journal and size

The Figure box sets the journal, width and height of this figure, so these questions are not asked here. They are listed because the figures of sections 6 and 7 ask their own size with them, each with its own default size; each of those sections says what comes next.

| # | Question | Leads to |
|---|---|---|
| 5.7 | Which journal format would you like? 1) None (use the default: Nature, *the figure's default width and height*) 2) Nature 3) Science 4) Cell 5) PNAS 6) ACS journals 7) PLOS ONE (every journal of the `journals` folder) | **None**: the default size is used. **A journal**: **5.7.1** |
| 5.7.1 | How wide should the figure be? (the widths that journal allows: 1, 1.5 or 2 columns for most, 1, 2 or 3 columns for Science) | **5.7.2** |
| 5.7.2 | How tall should the figure be, as a fraction of the page height (1 = a full page = *X* mm)? | the figure is drawn at its real size **(plot)** |

### 5.F Going back

| # | Question | Leads to |
|---|---|---|
| 5.8 | Do you want to go back to any of these steps? 1) No, continue 2) Import: trimming and ignoring 3) Set-up: OD values, temperature and event labels 4) Experiment processing 5) Experiment export: the figure of each file | **1**: **5.9**. **2, 3, 4 or 5**: that section's questions are asked again from its first question, with your answers as the defaults. Your answers to the later sections are kept. Then **5.8** is asked again. |

### 5.G The workbook of each file

The processing and the figure are accepted, so each experiment's workbook is written now, with its plot, and not when the run starts. One line says what it holds: "Every experiment gets a workbook with everything worked out for it: the measured and set oxygen, the OCR, the haems, Δψ, the averages, the events and your OD/volume/dilution entries."

| # | Question | Leads to |
|---|---|---|
| 5.9 | *(only when the export of the trim step did not write the spectra)* Do you want to export the spectra as csv files too (large, and it takes a while)? `(y/N)` | the plot and the workbook of every file are saved, then **6.1** |

If an export button of the trim step wrote the spectra (Yes at 3.4), 5.9 is not asked: one line says the spectra are not written again, and the workbook of each experiment still lists them on its **Spectral data** sheet.

Each file is then read once more, so this takes a moment: the terminal counts the files ("Saving file 3 of 12: *name*"), and for each the plot is saved in the results folder (svg and png, in the file's own folder; unless nothing is plotted) and shown in the window **(plot)**, and its workbook is written beside it, with the spectra csv files when you said yes. A plot or a workbook that could not be saved (a workbook open in Excel) says so in one line, and is tried again when the run starts.

Every workbook has each sheet named in plain words with the unit in its headings: **Measured O2**, **Set O2**, **OCR** and, when they were worked out, **OCR per OD**, **OCR % of range**, **OCR % of baseline** (every file with a baseline window, whichever way the OCR is plotted), the haems in every view (**Haems ΔD**, **Haems absorbance**, **Haems % oxidised**, and the first two **per OD**), **Δψ** and **Averages**; then **Events**, **How it was worked out** (the fit and the background, where ΔD starts, the oxidised and reduced regions and each haem's level in them, the numbers Δψ was worked out with, the OD scaling, the baseline window and the average OCR in it that is 100 % of baseline) and **Metadata**.

- The run does not write these plots and workbooks a second time. They are saved again only when a later answer changes them: at once when a later figure adds the averaging windows (**4.6.1**; the spectra are not written again), and in the run when a summary figure changes the haem fit.
- If you cancel after this, the plots and workbooks stay in the results folder, and the closing line says so.

---

## 6. Dataset figures: several experiments

If nothing is plotted in section 5, a message says these figures reuse the panels chosen for the individual experiment plots and are skipped, and the next step is **7.1**.

From here on the boxes are greyed out: these figures ask their own journal and size.

Each figure is drawn from your data once its questions are answered (this reads the files again, so it takes a moment, and the **Plotting data …** sign is on the plot meanwhile) and shown in the plot area. None of these figures is saved to the results folder until the run starts.

### 6.A Two experiments side by side

6.1 is only asked when there are at least 2 files.

| # | Question | Yes → | No → |
|---|---|---|---|
| 6.1 | Do you want to plot two experiments side by side? `(y/N)` | **6.1.1** | **6.3** |

| # | Question | Leads to |
|---|---|---|
| 6.1.1 | Which experiment goes on the left? | **6.1.2** |
| 6.1.2 | Which experiment goes on the right? | **6.1.3** |
| 6.1.3 | Which journal format would you like? (then, for a journal, how wide and how tall, as in 5.7) | the figure is drawn **(plot)**, then **6.2** |

| # | Question | Yes → | No → |
|---|---|---|---|
| 6.2 | Do you accept this figure? `(Y/n)` (above it: "Click No to change its settings.") | **6.3** | **6.1** |

If the figure cannot be previewed, a message says so and the figure is kept as it is.

### 6.B Four experiments in a 2x2 grid

6.3 is only asked when there are at least 4 files.

| # | Question | Yes → | No → |
|---|---|---|---|
| 6.3 | Do you want to plot four experiments in a 2x2 grid (knockdown and control, two addition orders)? `(y/N)` | **6.3.1** | **7.1** |

File names are read as `<strain>_<order>_run<N>`, for example `knockdown_kcn_then_bd_run1`. If no file name fits, the figure is skipped and the next step is **7.1**.

The figure starts at the baseline averaging window, so it needs the averaging windows of 4.6. With none set up, **4.6.1** is asked first (section 4.E); without windows the figure is not made and the next step is **7.1**. With both kinds of window set up, **4.6.2** then asks which kind the figure shows.

| # | Question | Leads to |
|---|---|---|
| 6.3.1 | Which run number should be shown? | **6.3.2** |
| 6.3.2 | Do you want the run name written faintly on each plot? `(Y/n)` | **6.3.3** |
| 6.3.3 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then **6.4** |

| # | Question | Yes → | No → |
|---|---|---|---|
| 6.4 | Do you accept this figure? `(Y/n)` (above it: "Click No to change its settings.") | **7.1** | **6.3** |

---

## 7. Dataset figures: summaries

As in section 6, the **Plotting data …** sign is on the plot while each picture is drawn. Both summary figures need the haem fit. If the haems were not decomposed in section 4 (or Haem decomposition was unticked), the fit is asked first, without a number of its own: *Which fit would you like to use?* (a numbered list of the presets of the haem library, then your own fit files in the `fits/` folder; the fit in the Haem decomposition box is the default), then, when the files have more than one spectrometer in common and the one saved is not among them, *Which spectrometer holds the haem spectra?*. Only the fit files are offered here, not the components found from the data. If the `fits/` folder holds no `.csv` file, or the fit cannot be used, a message says so and the figure is skipped. Both figures also average around the events, over the averaging windows of 4.6. With none set up, **4.6.1** is asked after the fit and before the figure's own questions (section 4.E); without windows the figure is not made and the next figure is asked. With both kinds of window set up, **4.6.2** then asks which kind the figure averages over; in the time response, the difference spectrum is the last window of that kind minus the one before it.

### 7.A Time response

| # | Question | Yes → | No → |
|---|---|---|---|
| 7.1 | Do you want to plot a time response? `(y/N)` | **7.1.1** | **7.2** |

File names need a group word and the hours, for example `control_7hours`.

The figure is built up in the plot window: the drop-down lists the individual experiment plots (marked locked, final) and the time response being built. Panels not chosen yet are empty boxes ("Kinetic trace 1", "Decomposition 1" ...). After every choice below the figure is redrawn **(plot)** and an accept question is asked (shown in the second table).

| # | Question | Leads to |
|---|---|---|
| 7.1.1 | What are the two group words, separated by a comma? | **7.1.2**. If there are not exactly two words, if either group has no file, or if fewer than two files have hours in their name, the time response is skipped and the next step is **7.2** |
| 7.1.2 | Which time points (hours) should be skipped in the waterfall plots? Separate them with commas, or type none. | the waterfalls are drawn **(plot)**, then the accept question, then **7.1.3** |
| 7.1.3 | Which experiment should the first kinetic trace show? | drawn **(plot)**, accept question, then **7.1.4** |
| 7.1.4 | Which experiment should the second kinetic trace show? | drawn **(plot)**, accept question, then **7.1.5** |
| 7.1.5 | Which experiment should decomposition plot 1 show? | drawn **(plot)**, accept question, then **7.1.6** |
| 7.1.6 | Which experiment should decomposition plot 2 show? | drawn **(plot)**, accept question, then **7.1.7** |
| 7.1.7 | Which experiment should decomposition plot 3 show? | drawn **(plot)**, accept question, then **7.1.8** |
| 7.1.8 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then the final accept question |

Each is a yes or no question, `(Y/n)`, with what **n** does on the grey line above it.

| Question | Yes → | No → |
|---|---|---|
| Do you accept these waterfall plots? | the next question | **7.1.2** again ("Click No to choose the time points again.") |
| Do you accept this plot? (after each kinetic trace and decomposition plot) | the next question | the same choice again ("Click No to choose another experiment.") |
| Do you accept this figure? (final) | **7.2** | **7.1** ("Click No to change its settings.") |

### 7.B Haem and OCR response

| # | Question | Yes → | No → |
|---|---|---|---|
| 7.2 | Do you want to plot a haem and OCR response? `(y/N)` | **7.2.1** | **9.1** |

File names need the strain, the addition order and the run number, for example `knockdown_kcn_then_bd_run1`. The files found are listed. If no file name fits, the figure is skipped and the next step is **9.1**.

The figure is built up in the plot window in stages. First only the baseline OCR and the OCR response are drawn, then all the haems are added, then they are redrawn with the haems and order you chose. Each stage has its own accept question (second table).

| # | Question | Leads to |
|---|---|---|
| 7.2.1 | Which OCR would you like to use? 1) OCR (µM min⁻¹) 2) OCR / OD (µM min⁻¹ OD⁻¹), *only offered if you said yes to OD scaling in 3.1* 3) OCR (% of the range) (this figure has a % of baseline of its own) | the OCR plots are drawn **(plot)**, accept question, then **7.2.2** |
| 7.2.2 | How would you like to show the haems? (the same options as Haems as in the View box, but % oxidised is offered only when every file of the figure has both regions, as the figure averages the files together) | **7.2.3** if you said yes to OD scaling in 3.1 and did not choose % oxidised, otherwise all the haems are drawn **(plot)**, accept question, then **7.2.4** |
| 7.2.3 | Do you want to scale the haems by OD as well? `(Y/n)` | all the haems are drawn **(plot)**, accept question, then **7.2.4** |
| 7.2.4 | Which haems should get a row, and in which order? | drawn **(plot)**, accept question, then **7.2.5** |
| 7.2.5 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then the final accept question |

Each is a yes or no question, `(Y/n)`, with what **n** does on the grey line above it.

| Question | Yes → | No → |
|---|---|---|
| Do you accept the OCR plots? | **7.2.2** | **7.2.1** again ("Click No to choose the OCR again.") |
| Do you accept these haem plots? | **7.2.4** | **7.2.2** again ("Click No to choose how to show the haems again.") |
| Do you accept these haem rows? | **7.2.5** | **7.2.4** again ("Click No to choose the haems again.") |
| Do you accept this figure? (final) | **9.1** | **7.2** ("Click No to change its settings.") |

---

## 8. Dataset export

Nothing is asked here: the workbook of each experiment, and its spectra, are written in the experiment export (**5.9**). The number 8 is kept for the dataset workbook still to come.

---

## 9. Dataset export: summary

A summary of all your answers is printed (files, results folder, trimming, ignoring, decomposition, OD scaling, temperature, Δψ, averaging, plots, figure sizes, and how many workbooks were written at 5.9).

| # | Question | Yes → | No → |
|---|---|---|---|
| 9.1 | Do you want to start? `(Y/n)` | Your answers are saved in the data folder (`portimao_settings.json`) for the next time this dataset is opened, and the run starts. If the data folder cannot be written to, a message says the dataset will start from the standard settings next time. Every file is processed again for the multi-experiment figures and summaries, which are then made; a plot or workbook saved at 5.9 is not written again (unless a summary figure changed the fit), and one not saved then is written now. | The program stops and nothing else is changed: data you exported with the export buttons of the trim step, and the plots and workbooks saved at 5.9, are kept, and the last line says so. |
