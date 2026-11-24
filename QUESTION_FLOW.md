# Portimao question flow (V2.19)

Every question in the order it is asked, with where each answer leads. The question text is the text on screen.

**How to read it**

- The questions are asked in Portimao's window. If the window cannot open, nothing is asked: a message says why and what to do (in the Mac app, with a **Copy details** button to send the details with the Mac problem form).
- **The guide** on the left of the window lists the steps, numbered, one line each, under the names of the stages: **Import** (steps 1 to 3, section 1 here), **Set-up** (4 to 9, sections 2 and 3), **Experiment processing** (10 to 13, section 4), **Experiment export** (14 to 16, section 5), **Dataset figures** (17 to 20, sections 6 and 7) and **Dataset export** (21, section 9). The guide has four levels, largest first: the stage name, the steps under it, then in the open step the explanations and the question. Only the stage of the step open lists its steps, its name large and bold; the others show their name a little smaller and paler, with the numbers of their steps and a tick once they are passed. In the stage shown, a step done has a tick, a step passed without being asked (the previous processing of a dataset never opened, the OD values when you do not scale by OD) stays in the list, greyed, with "· not needed this run", and the steps to come are paler.
- **The step open** sits under its line, marked ▸: what was said since your last answer (the explanations in a light grey, the messages), then the question in pink, larger than the rest, then its answers. The stage name is not repeated there. What was said before your last answer folds away when the next question is asked; all of it stays in the run's log.
- **Answers are clicked**, not typed:
    - something done on the plot or in the boxes above it (2.1, 4.4, 4.6, 5.1): one big **Continue** button (in 2.1 with **Export csv** above it);
    - a yes or no question: **Yes** and **No**, one above the other;
    - a numbered list: a button for each choice; a long list in two columns;
    - several choices from a list: a tick button for each, then **Continue** (greyed while none is ticked); the choices offered at first are ticked, and where the order matters it is the order you tick them in;
    - a number or a name, the only answers typed: a box that starts with what Continue alone gives (the default, with its unit in the question), then **Continue**, or Enter in the box, with "Type a number, then click Continue or press Enter." under it;
    - a table: **Confirm** under it.

  The answer Enter gives is the highlighted button, which holds the keyboard. In this list, `(Y/n)` and `(y/N)` say which of Yes and No is highlighted (the capital letter), `(1/2/3)` with a number in bold which choice is, and `[value]` what the box starts with (`[skip]`: empty, which leaves the answer out). The answer clicked is written under the question, after an arrow.
- The defaults shown here are the standard settings, offered for a dataset you have never run. Once you have started a run, your answers, your OD values and event labels among them, are saved in a small file inside the data folder (`portimao_settings.json`), and the next time that dataset is opened you choose whether to load them (**1.3**), on this computer or on another one the folder is copied to.
- After an answer that cannot be used (a number out of its limits), one line in red says what to type, and the question waits for the next answer.
- Some answers are typed in a table, which opens in the step under the last few lines of its text: one row per file (the OD values, 3.1.1) or per event (the event labels, 3.2). Click a cell and type, or select what is there and type over it; Tab moves across and Enter moves down. A cell that cannot be used turns red. Press **Confirm** under the table when it is filled in. If a cell is still wrong, or a label is empty, one line names it and the table stays open; the OD table can be confirmed with cells left empty (3.1.1). The grey text of a table (its headings, the file names, the text in the file) is light enough to read on the dark card, and what you type is bold in a plain font. A row of **Symbols** (µ, ⁻¹, ₂ ...) is under a table and under a box for a name.
- **Going back to an earlier step.** A change in the boxes above the plot that belongs to an earlier step opens that step in the guide: the tabs of the Time regions box belong to step 4 (Trim / Ignore), 11 (Ox / Red) and 13 (Averaging); Edit ODs to step 6 (OD values) and Edit labels to step 9 (Event labels); the fit, the background, the spectra, the Haem decomposition tick, Build a fit and Keep to compare to step 10 (Haems); the Δψ box to step 12 (Δψ); the journal, the width, the height and Export master to step 14 (Figure). How the haems, the OCR and the labels are shown, the angle of the labels and the order of the panels belong to every step, and open none. The step waited at then reads **→ ... ← you were here**, the step opened says so above its messages with a few words on where to change it, and a **Back to** *step* button takes the place of the answers (the trim step keeps its **Export csv** button above it): click it to answer the question waiting. A click on the line of a step done opens it in the same way. A change that belongs to a later step ticks that step, as done: the guide is a guide, and the steps can be done in any order.
- The **Help** button under the answers is greyed out for now.
- **Yes → / No →** says which question comes next. **Next** means the next question in this list.
- In sections 1 to 5 and 9 the numbers on screen are the numbers here (all but 5.8, which is still numbered in the order asked). A question asked again keeps its number, and when a question is skipped the next one keeps its own, so 3.1.2 follows 3.1 when the OD values are not asked. A question asked inside another's step shows that step's number: the name of each component shows 4.1.1.7, replacing a fit file 4.1.1.9. In sections 6 and 7, the numbers here are for reference: on screen they are given in the order the questions are asked, so when a branch is skipped the later numbers move up, and every "Do you accept...?" question takes a number of its own.
- A "Do you accept...?" question with one way to change is a yes or no question, `(Y/n)`: the grey line just above it says what **No** does ("Click No to change the labels again."). One with more ways to change is a numbered list starting with **1) Yes, accept**, which moves on; its other answers (**2) No, ...**, and **3**, **4** ... where there are more) each say what is asked again, with your last answers as the defaults.
- The plot on the right is redrawn after each step marked **(plot)**. You can flick through the files with the arrows or the drop-down above the plot at any time while a question waits. The file shown and the one on each side of it are redrawn at once; any other file is drawn when you go to it, with its last plot under the **Plotting data …** sign meanwhile (clicking a cell of a table shows its file in the same way). From section 6 on, every file shows the plot saved for it (after **5.9**); a file whose plot could not be saved says so.
- The **boxes** above the plot, in one row under the file name and its arrows, show what the run uses. Every question that sets one of them says so, and it can be changed there at any time without typing the answer again:
    - **Time regions**: three tabs, **Trim / Ignore**, **Ox / Red** and **Averaging**, the one pressed having its edges on the plot and its numbers in the box (section 2, 4.C and 4.E). The guide presses the tab of its step (2.1, 4.4, 4.6). A tab can be pressed at any time: its edges come onto the plot (Trim / Ignore on the whole recording, with the edges in use as red dashed lines; the other two on the processing plot), and the change is used when you press another tab, or answer the question that waits. The edges of the step that waits stay as you left them meanwhile. A changed trim keeps the regions and the windows at their minutes; nothing is exported again by itself (press **Export csv** in the trim step).
    - **View**: **OCR as** (how the OCR is shown) with its **per OD** box, **Haems as** (how the haems are shown) with its **per OD** box, **Edit ODs** (once you chose to scale by OD, even with values missing), **Labels as** (what the event labels show), the **Angle** of the event labels (0 to 90°, 45 at first) and **Edit labels**.
    - **Haem decomposition**, with its tick as the title (ticked when the haems are worked out and shown): the **Fit**, the **Scatter** (the background fitted under the haems), **Spectra** (the spectrometer whose spectra hold the haems), **Build a fit** (with **Save fit**) and **Keep to compare** (with **Keep old** and **Keep new** under it while one is kept, and beside them the switch **Side by side / Overlaid**: side by side shows the kept one as a plot of its own on the left of the plot in use, overlaid draws it dashed over the plot in use; side by side at first, and the choice is kept with the dataset).
    - **Δψ**, with its tick as the title: the numbers of Δψ, shown while it is ticked (4.D). The tick can be clicked only while Δψ can be worked out.
    - **Figure**: the **Journal**, the **Width** and the **Height** of the figure of each file, the **Export master** button and the **Standard order** button.
    - The **panels** of the plot of a file can be moved: while the boxes can be used, a small up and a down arrow sit left of each panel, and a click moves that panel one place (the arrow that cannot be used, up on the top panel, is paler). No question is asked: the plot is redrawn at once and one line in the terminal says the new order. The order holds for every file and for the figure saved for each, and is kept with the dataset. A panel that comes later (a haem ticked since, Δψ switched on) is drawn just above the panel that follows it in the standard order, or at the bottom. **Standard order** puts the panels back: oxygen, OCR, the haems a then b then c, Δψ. The arrows are away while edges are dragged on the plot (trimming, the regions, the averaging windows) and while the plot is being redrawn.
    - **Spectra** is shown only when your files share more than one spectrometer (Cyt and NADH). Picking the other one works the haems out from its spectra.
    - **Haems as** swaps the haems between ΔD (mOD), the change from the start; % oxidised (reduced region = 0 %, oxidised region = 100 %); and Absorbance (mOD). % oxidised is in the list only when at least one file has both regions (4.4); a file without both stays in ΔD, as its axis says. The choice holds for every plot of your files and for the figure saved for each file.
    - **per OD** (beside Haems as) scales the haems by OD. The box is shown only once you have entered the OD values of every file (3.1.1), and a message says so then. It is greyed while the haems are in % oxidised, which has no per OD.
    - **OCR as** swaps the OCR between µM min⁻¹; % of the range; and % of baseline (the average in the baseline window = 100 %), in the list only once the averaging windows are set up (4.6). Its **per OD** box, shown once you have entered the OD values of every file (3.1.1), makes µM min⁻¹ the OCR per OD (µM min⁻¹ OD⁻¹); it is greyed for the two % views, which have no per OD. A file without a baseline (less than 10 s of data before its first addition, or no addition) keeps its usual OCR, as its axis says, and one line says so. The choice holds for every plot of your files and for the figure saved for each file.
    - **Labels as** swaps the event labels between **In the chamber** (the concentration in the chamber after the addition, `400 µM KCN`; the standard) and **What was added** (`10 µL of 200 mM KCN`). An event with no stock and volume shows its concentration in the chamber either way, and one with no concentration its label alone. The choice holds for every plot of your files, the figure saved for each file and the labels under the windows of the haem and OCR figure, and is kept with the dataset.
    - While your files are on the plot (sections 2 to 5), you can change it whenever a question waits. The plot is redrawn at once, the run uses the change, and the question goes on waiting.
    - **Angle** sets the angle of the event labels on every plot and in the figure saved for each file. A number outside 0 to 90 turns the box red, with what to type under it.
    - **Edit ODs** and **Edit labels** open their step again in the guide (OD values or Event labels, with "you were here" on the step that waits) and its table (3.1.1 or 3.2), with **Confirm** above the **Back to** button; after Confirm the plot is redrawn and the guide goes back to the question that waits.
    - Unticking Haem decomposition leaves the haems out of the run. Ticking it, or picking a fit, works them out with the fit shown and ticks the box.
    - If a fit cannot be used, one line says why and the box goes back to what it showed.
    - A new journal, width or height redraws the plot only in section 5, the one plot drawn at the figure's size. Before that the change is kept for section 5.
    - The **Journal** list holds every journal of the `journals` folder. Choosing one makes the figure follow what it asks: the widths offered, the tallest figure, the text sizes, the panel letters, the font and the thickness of the lines.
    - **Export master** saves one page of the journal as a PDF in the results folder (`<file>_master_<journal>.pdf`): the figure of the file shown at its printed size, a box where its legend goes and grey lines where the text of the paper goes. It works in section 5, where that figure is on the plot; before that, one line says so. With **None** the page is Nature's. A journal whose page size is not known is shown on an A4 page, and the page says so.
    - The boxes are greyed out while you choose the folder, during the questions of 4.A.1, and from section 6 on.
- While the program draws a picture of its own (the components found from the data, the figures of sections 6 and 7), the **Plotting data …** sign is on the plot: a large spinning wheel on a yellow card in the middle of the plot, with "Plotting data …" under it in large letters. The same sign shows while a file is read or a plot redrawn, and whenever the program is still working on an answer or a Confirm 0.2 s after the click (after an OD value is confirmed, for example). It goes when the picture is shown or the next question is asked.
- Section **1** is the import: your files and where the results go. Sections **2** and **3** are the set-up: the parts of the files that are used, and what is known about each run (the OD values, the temperature and the labels). The experiment processing starts with section **4**.

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

## 2. Set-up: trimming and ignoring

TRIM = data that is not imported, plotted or used. IGNORE = data that is plotted but not used for calculations. The plot shows the standard plot of the whole recording of each file (with the haems, when they are shown; the Haem decomposition box turns them on and off and picks their fit), with four edges on it: the trimmed start and end in grey (the parts trimmed away grey and hatched) and the ignored start and end in amber (the parts ignored amber). Each edge has a handle above the plot with its minutes beside it, the trimmed ones in the top row and the ignored ones just under them. Moving an edge never draws the plot again.

- **Drag** an edge by its handle or by its line; over an edge the mouse becomes a two-way arrow. The shading follows at once, and the edge moves in steps of 0.1 min. A trimmed edge stops at the first or the last event, so no addition is cut away, and the ignored parts stay inside the kept part without crossing. Where two edges meet, the line takes the ignored one; the trimmed one is still taken by its handle.
- **Type** the minutes under **Trim / Ignore** in the Time regions box above the plot, on two lines: **Trim before** and **after**, then **Ignore before** and **after**, each a time on the whole recording (min), as on the time axis of this plot. The boxes always show the full times, so when the edges are opened again they show where the edges are on the whole recording, and you can trim or ignore again from there. Press Enter or leave the box. A number that cannot be used turns the box red, with what to type beside it; a number beyond a limit is kept at the limit.
- **Apply to every experiment**, ticked when the step opens: an edge moved or typed on the file shown moves on every file, to the same minutes from its own start or end, within that file's limits. Unticked, only the file shown changes. A file whose times differ from most files is marked **(own times)** in the drop-down.
- The edges start where they were left the last time the dataset was run; for a dataset never run, the first 5 minutes are ignored and nothing else. When the edges are opened again (the **Trim / Ignore** tab of the Time regions box at any later step, or going back at **5.8**), the limits they had are drawn as red dashed lines, so you can see how far you moved them.
- **Export csv**, above Continue: the quick export, the only one before the experiment export. It asks **3.4** (what to export, your last choice highlighted) and writes the files with the edges as they are, so you can plot them outside Portimao; then the step waits again. Nothing is asked unless you press it, so it can be skipped, and Portimao can be closed once it has written the files. The OD values and labels are in the workbook once you have typed them. Nothing is exported again by itself when the edges change later: the trim step opened again (the Trim / Ignore tab) keeps its **Export csv** button, to write new files.

| # | Question | Leads to |
|---|---|---|
| 2.1 | Drag the edges on the plot, or type the times in the Time regions box above it. Click Continue when every file looks right. (above it, in grey: what TRIM and IGNORE mean, "Grey edges trim, amber edges ignore; with "Apply to every experiment" ticked, a change moves every file." and "Export csv writes the data of every file with these edges, to plot it outside Portimao.") | **Export csv**: **3.4**, then 2.1 waits again. **Continue**: the limits of every file are listed, the plot shows the data they keep **(plot)**, then **3.1**. |

---

## 3. Set-up: OD values, temperature and event labels

The last part of the set-up: what is known about each run (the OD values, the temperature and the event labels). The OD values and event labels saved for the dataset (in `portimao_settings.json`) are offered as defaults. The plot is the standard plot, cut to the limits of section 2.

### 3.A OD values and temperature

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.1 | Do you want to scale by OD? `(y/N)` (above it, in grey: "Scaling by OD divides the OCR and the haems by dilution factor × OD × volume; the View box above the plot then offers per OD for each.") | **3.1.1** | **3.1.2** (no OD scaling anywhere in the run) |

The OD table opens on the terminal side, with one row per file and a column each for the OD, the volume (mL) and the dilution factor. The values stored for a file are filled in, and the dilution factor is 1 when none is stored. Clicking a cell of a file shows that file on the plot.

| # | Question | Leads to |
|---|---|---|
| 3.1.1 | Fill in the OD, volume and dilution of each file, then press Confirm. (above it, in grey: "One row per file: the OD of the cells added, the volume of cells (mL) spun down and resuspended in 5 mL, and the dilution factor if the cells were diluted mid run.") | If a cell is not a number above 0, one line names those cells and the table stays open. Otherwise the table closes and the values of every file are listed, a missing one as "missing". With every value in, one line says "OD values entered for every file." and the next step is **3.1.1.1**. With cells left empty, a warning names them ("OD values are missing for: a: volume, b: OD. The OD scaling stays off until every file has its values: Edit ODs in the View box fills them in."); the values typed are kept, nothing is scaled by OD, and the next step is **3.1.2**. |

**Edit ODs** in the View box opens this table again at any later step, once you chose to scale by OD, also while values are missing; after Confirm the same line or warning is given, and the OD scaling comes on once every value is in (or goes off again while one is missing). Once every value is in, the View box above the plot shows the **per OD** boxes beside OCR as and Haems as; at 3.1.1 a message says so: "The OCR and the haems can now be shown per OD: the per OD boxes beside OCR as and Haems as in the View box above the plot." The plot follows them from here on, and so does the figure saved for each file.

| # | Question | Leads to |
|---|---|---|
| 3.1.1.1 | How would you like the OCR shown? `(1/2/3)` 1) OCR (µM min⁻¹) 2) OCR / OD (µM min⁻¹ OD⁻¹) 3) OCR (% of the range); 2 is highlighted, or the one the dataset was saved with. (above it, in grey: "The OD values are in, so the OCR can be shown per OD.") | **OCR as** in the View box is set to the answer, one line says "You can change this under OCR as in the View box above the plot at any time.", the plot is redrawn **(plot)**, then **3.1.2** |

The temperature is asked of every dataset, whether or not you scale by OD: one value for all its runs, kept with the dataset. Δψ (4.5) is worked out with it; nothing else uses it. It is the same value as the Temperature of the Δψ box (4.D): changing one changes the other.

| # | Question | Leads to |
|---|---|---|
| 3.1.2 | What was the temperature of the runs (°C)? `[37]` | a number from 0 to 100; then **3.2** |

### 3.B Event labels

If no file has any event, nothing is asked here and the next step is **4.1**.

The labels table opens on the terminal side: one row per event, under the name of its file, with the time of the event (min), the text in the file (grey, not typed in), its label, the **Stock**, the volume **Added (µL)** and the concentration **In the chamber**. Each row starts as saved for the dataset, or else with the label as written in the file; an event left out before reads `ignore`. Clicking a cell of a file shows that file on the plot. The **Symbols** row under the table types µ, ⁻¹, ₂ and the like into the cell last typed in.

- Type the stock with its unit (nM, µM, mM or M, in any capitals; `u` for µ); a number alone is mM. Once a row has both a stock and a volume, its concentration in the chamber fills itself in, in green, and cannot be typed in: stock × volume ÷ 5 mL (the chamber), the same label added again in a file adding up (10 µL of 200 mM KCN gives 400 µM, the next 800 µM). The maths is in `MATHS.md`, section 8.
- A row with no stock and volume takes a concentration in the chamber typed by hand (a number alone is µM), or none.
- Concentrations are written in their most readable unit: 1.2 mM, not 1200 µM.

| # | Question | Leads to |
|---|---|---|
| 3.2 | Fill in the label, the stock and the volume added of each event, then press Confirm. (above it, in grey: "One row per event. Write ignore as the label to leave an event out. Type the stock with its unit (nM, µM, mM or M; a number alone is mM) and the volume added, and the concentration in the chamber (5 mL) is worked out, the same label added again adding up. Or leave them empty and type the concentration in the chamber (a number alone is µM).") | An event labelled `ignore` (in any capitals) is left out, and its other cells are greyed out. If a label is empty, a stock, volume or concentration cannot be used, or a row has a stock without a volume (or a volume without a stock), one line names those cells and the table stays open. Otherwise the table closes: **3.2.1** if a label could be written more tidily; then the concentrations are worked out from the labels as they then are, the labels of every file are listed (with what was added and the concentration in the chamber), one line says "Event labels saved! Edit labels in the View box above the plot changes them at any time." and the labels are drawn **(plot)**; then **4.1**. |

A label is written more tidily with `u` in front of a unit as µ (`100 uM` as 100 µM), a litre as a capital L, a space between a number and its unit, and `-1` after a unit or anything after `^` raised (`8ug ml-1` as 8 µg mL⁻¹). Only units are changed: a name with numbers in it (`nd-011992`) and a formula (`H2O2`) are left as they are. Under "These labels will be written more tidily:", each is listed by its file, its time and its tidy form ("run1, 15.01 min: 8 µg mL⁻¹"), then:

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.2.1 | *(only when a label could be tidier)* Do you want to continue? `(y/N)` (above it: "Click No to change them yourself in the table.") | every listed label is replaced by its tidy form; the labels are listed, saved and drawn **(plot)**, then **4.1** | **3.2** (the table opens again with the labels as you typed them) |

There is no question to accept the labels: **Edit labels** in the View box opens the labels table again at any later step, and the plot is redrawn after Confirm.

### 3.C Export csv

The quick export is asked only from the **Export csv** button of the trimming step (2.1), the first time and whenever the Trim / Ignore tab is opened again; it is not offered after the labels.

| # | Question | Leads to |
|---|---|---|
| 3.4 | Would you like to export the individual experiment files now? `(1/2/3/4/5)` (above it, in grey: "The summary sheet is a workbook for each file; the raw CSVs are its spectra, which are large and take a while to write."; and, when no file is trimmed: "No file is trimmed, so "trimmed and full" writes the same as "trimmed".") 1) No 2) Summary sheet, trimmed (about *size*) 3) Summary sheet, trimmed and full (about *size*) 4) Summary sheet and raw CSVs, trimmed (about *size*) 5) Summary sheet and raw CSVs, trimmed and full (about *size*). 1 is highlighted the first time, then your last choice. | **1**: nothing is written. **2 to 5**: every file is exported, then a message says where. Either way the trimming step waits again. |

The sizes are worked out for your files, less for a trimmed one: about 0.3 MB of workbook and 1.2 GB of spectra for each 100 MB `.paf` file. Each file is exported to its own folder in the results folder, `<results>/<file>/`:

- `<file>.xlsx`, with every choice but 1: the trimmed data (all of it for a file not trimmed), with the sheets **Measured O2** and **Set O2**, **OCR**, **Events** (the time, the text in the file, your label, the stock (mM) and volume added (µL), what the addition added and the concentration in the chamber (µM), and whether the event is ignored) and **Metadata** (your OD, volume and dilution, the trimmed and ignored edges in minutes, and the spectrometers). The experiment export (**5.9**) later writes this workbook again with its own results added.
- the spectra csv files, with 4 and 5: one per spectrometer and kind (`Cyt_transmiss.csv`, `Cyt_intensity.csv`, `Cyt_attenuation.csv`, and the same for `NADH`), wavelengths down and one column per spectrum; the workbook lists them on a first sheet, **Spectral data**.
- `full/`, with 3 and 5, only for a file you trimmed: the same for the whole recording (its spectra with 5). It does not record the edges, so it stays as it is when they change.

Nothing is scaled by OD, decomposed or averaged, and the ignored parts are included.

---

## 4. Experiment processing

The plot is the standard plot, cut to the limits of section 2, with the event labels of section 3. It is redrawn after each step marked **(plot)**.

### 4.A Haem fit

The haems on the plot are those of the import, worked out with the standard fit, the fit last saved for the dataset, or the fit you picked or built in the Haem decomposition box, with the background in that box. A message names that fit ("The haems are worked out with *fit*.", or "... with Your own haems: *c1_myco, bH_bswitch, ...*"). The section then starts at **4.2**. 4.1 is asked only when the plot shows no haems yet:
- the dataset was last saved without them;
- the fit could not be used (a message in section 1 said why);
- you unticked Haem decomposition.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.1 | *(only when no haems are shown)* Do you want to decompose the haems? `(Y/n)`, or `(y/N)` when Haem decomposition was unticked or the dataset was saved without haems | **4.1.1** | **4.6** (no haems, unless you tick Haem decomposition later) |

If the `fits/` folder holds no preset and no fit file, 4.1 is still asked, and 4.1.1 then offers only *Find the components from the data*.

| # | Question | Leads to |
|---|---|---|
| 4.1.1 | Which fit would you like to use? (a numbered list of the presets of the haem library, then your own fit files in the `fits/` folder, and *Find the components from the data (principal component analysis)* last; the fit in the Haem decomposition box is the default) | **4.1.2** if the files have more than one spectrometer in common and the default one is not among them, otherwise the decomposition is drawn **(plot)**, then **4.2**; the last choice leads to **4.1.1.1** (after 4.1.2 if that is needed). If the fit file cannot be read, a message says so and the haems are not decomposed: **4.6**. |
| 4.1.2 | Which spectrometer holds the haem spectra? | the decomposition is drawn **(plot)**, then **4.2** (or **4.1.1.1** when the components are being found) |

The section starts with a message pointing to the boxes: "Use the Haem decomposition box above the plot to change the fit, the background and the spectrometer (Spectra), and Haems as in the View box for how the haems are shown; the plot is redrawn after each change." (the spectrometer is named only when your files share more than one).

While 4.2 waits, the Haem decomposition box changes the decomposition, and the plot is redrawn after each change:
- **Fit**: another preset or fit file of your own.
- **Spectra** *(only when the files share more than one spectrometer)*: the spectrometer whose spectra hold the haems, Cyt or NADH.
- **Haems as** (in the View box): ΔD (mOD), % oxidised (once a file has both regions, 4.4) or Absorbance (mOD), with **per OD** beside it when OD values were entered.
- **Scatter**: the background fitted under the haems (Rowan scatter, the standard; Valencia; flat + 1/wavelength; flat + 1/wavelength + 1/wavelength²; straight line).
- **Build a fit**: folds out a tick box for each haem of the library, one line each for the a, b and c haems; the boxes start with the haems of the preset in use. Ticking or unticking a box works the haems out with the ones ticked, and the Fit drop-down reads *Your own haems*. Ticking a haem with the same name as one already ticked (c1_myco and c1_037v are both Cyt cc) unticks the other, and the last box cannot be unticked; a note beside the height says so. Under the boxes, type a name and click **Save fit** (or press Enter) to save the haems ticked as a fit file of that name in the fits folder: it becomes the fit in use, is in the Fit list from then on, and the dataset is saved with it. A name already used by a preset or a fit file is refused with one sentence, so nothing is overwritten. Click the button again to fold the boxes away.
- **Keep to compare**: keeps everything as it is on the plot at the click (the fit, the background, the oxidised and reduced regions of every file and the numbers of the Δψ box), and a line in the box says which one is kept. Change the fit, the haems ticked, the background, the regions or a number of the Δψ box, and the kept one is shown on every file in one of two ways, chosen with the switch **Side by side / Overlaid** beside Keep new. **Side by side** (at first): the file worked out with the kept one is a plot of its own on the left, the same size as the plot in use on the right, and each panel has the same y range on both sides; the edges you drag, the arrows and the shading stay on the plot in use. **Overlaid**: the kept haems are drawn as dashed, paler lines in the same colours under the new ones, and the kept Δψ the same way in the Δψ panel (4.D). The choice is kept with the dataset. Under the plot, each haem in both has two numbers, largest / average: the largest and the average distance between its two traces, in the units of the haem panels; Δψ has the same two numbers in mV, over the spectra where both have a value. A file that had no regions when you clicked has no kept Δψ, and one sentence under the plot says so. While one is kept, Keep to compare is greyed and two buttons under it choose between the two, and either one takes the kept one away: **Keep new** carries on with what is on the plot; **Keep old** puts the kept fit, haems, background, spectrometer, Δψ numbers and regions of every file back in use (while you are still choosing the regions in 4.4, the regions stay as they are on the plot, and one line says so). The terminal says which one you carry on with. To compare again, click *Keep to compare* again. Each file takes about twice as long to draw while one is kept.

To leave the haems out, untick Haem decomposition; answering yes then goes on without haems, to **4.6**.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.2 | Do you accept this decomposition? `(Y/n)` (above it: "Click No to find the components from the data.") | **4.4** (**4.6** when Haem decomposition was unticked) | **4.1.1.1** (the questions of 4.A.1, then 4.2 again with the components) |

#### 4.A.1 Components from the data (principal component analysis)

Asked when the last choice of 4.1.1, or No at 4.2, is taken. The boxes are greyed out until they are answered, and the fit list then includes a fit file saved in 4.1.1.9. The numbers keep counting up when a question is asked again, and each component name is a question of its own, so the numbers on screen can be higher than these. The files are read for their spectra (trimmed, without the ignored parts; this can take a moment). Once the components are made, the plot window gets a *PCA components* picture (one panel per component, coloured by the haem type it looks like) and a *PCA examples* picture (the best and worst described spectrum and their residuals) after the files **(plot)**. The **Plotting data …** sign is on the plot while they are made. They go when the decomposition is drawn.

| # | Question | Leads to |
|---|---|---|
| 4.1.1.1 | Where should the spectral window start (nm)? | **4.1.1.2** |
| 4.1.1.2 | Where should the spectral window end (nm)? | **4.1.1.3** (or this question again if the analysis cannot be run, for example the window is too narrow) |
| 4.1.1.3 | How many components should be found? (The data suggest *N*; use as few as describe the data, extra ones only fit noise.) | a whole number; the number used last time, or else the suggestion, is the default; then **4.1.1.4** |
| 4.1.1.4 | Do you want to rotate the components so each is as peak-like as possible (varimax)? `(Y/n)` | **4.1.1.5** |
| 4.1.1.5 | Over how many nm should the components be smoothed to remove their noise (0 for none)? (default 4, or the width used last time; at most a quarter of the window) | the components and the examples are drawn **(plot)**, with one line per component (type, peak, share of the change) and the residual, then **4.1.1.6** |

| # | Question | 1 → | 2 → | 3 → | 4 → |
|---|---|---|---|---|---|
| 4.1.1.6 | Do you accept these components? `(1/2/3/4)` | **4.1.1.7** | **4.1.1.3** (the number of components) | **4.1.1.1** (the window) | *No, choose a fit file instead*: **4.1.1**, or **4.2** when you came from 4.2 (pick the fit in the Haem decomposition box) |

| # | Question | Leads to |
|---|---|---|
| 4.1.1.7 | Do you want to name the components? `(y/N)` | yes: one question for each component, "What is component *N* (*type*, largest peak at *X* nm) called?", suggesting a name from its type such as *a-like* (a name that is empty, has a comma or is used twice is asked again), then **4.1.1.8**; no (PC1, PC2, ...): **4.1.1.8** |
| 4.1.1.8 | Do you want to save these components as a fit file in the fits folder? `(Y/n)` | yes: **4.1.1.9**; no: the decomposition is drawn **(plot)**, then **4.2** |
| 4.1.1.9 | What should the fit file be called (without .csv)? | the name of a preset is refused (one line says so and the question waits); if a fit file of that name exists, it asks "*name*.csv already exists. Do you want to replace it?" `(y/N)` (no asks for a name again); then the decomposition is drawn **(plot)**, then **4.2** |

### 4.B Trim and ignore times again

No question is asked: the trim and ignore edges stay movable with the **Trim / Ignore** tab of the Time regions box, at any step. There is no 4.3: the numbers of the later questions are kept.

### 4.C The oxidised and reduced regions

*(only when the haems are decomposed)* The oxidised region is a stretch of the run where the haems are fully oxidised, the reduced region one where they are fully reduced. Each haem's level in the two (its median there) is what its % oxidised is worked out from. The program never places a region: you pull each out on the plot, in red for oxidised and blue for reduced, or leave it as it is.

- Both regions start **not chosen**: one red handle at the left of the used part of the run reading "oxidised: not chosen", one blue handle at the right reading "reduced: not chosen". **Pull** a handle out, by the handle or its line, and the region opens from that side, shaded in its colour; its second edge then has a handle too, and the times of the region are written beside it. The edges move in steps of 0.1 min, and moving one never draws the plot again.
- **Type** the times under **Ox / Red** in the Time regions box above the plot, on two lines: **Oxidised from** and **to**, then **Reduced from** and **to**, in minutes as on the time axis of the plot. Press Enter or leave the box.
- An edge stays in the used part of the run (not trimmed, not ignored). Moved past the other edge of its region, it pushes that edge along. The two regions never overlap: an edge moved into the other region stops at that region's nearer side, so moved on past its middle it comes out on the far side.
- A region shorter than 10 spectra (5 s when a spectrum is taken every 0.5 s) counts as not chosen: its shading goes and its handle reads "not chosen" again.
- **Apply to every experiment**, ticked when the step opens: an edge set on the file shown is copied to every file at the same distance from the addition nearest to it, counted in order (1.5 min before the 3rd addition of the file shown is 1.5 min before the 3rd addition of every file), then kept within that file's own limits. A file with fewer additions keeps the edge it had. Unticked, only the file shown changes.
- If you press **Ox / Red** at another step, or go back to the processing step later in the run, the regions are where you left them, on the same data even when the trim has changed. Changed there, they are listed when you press another tab or answer the question that waits; 4.4.1 is not asked then.
- The regions are saved with the dataset (in `portimao_settings.json`), so they are on the plot the next time it is opened.
- The regions are optional. A file with both has each haem's oxidised and reduced level, and its haems can be shown in % oxidised (Haems as in the View box, and 7.2.2); a file with none, or with only one, cannot, and nothing else changes for it. Once a file has both, a message says: "The haems can now be shown in % oxidised: choose it under Haems as in the View box above the plot."

| # | Question | Leads to |
|---|---|---|
| 4.4 | Pull the oxidised and the reduced region out on the plot, or type their times under Ox / Red in the Time regions box above it. Click Continue when every file looks right, or straight away for no regions. (above it, in grey: what the regions are, "Red is oxidised, blue is reduced; with "Apply to every experiment" ticked, an edge is copied to every file at the same distance from its nearest addition.", "Leave both as "not chosen" for no regions." and "With no regions the haems cannot be shown in % oxidised; everything else is the same.") | **Continue**: with no region on any file, or both regions on every file, the regions are listed, then **4.5** (**4.6** when Δψ cannot be worked out); with both regions on some files only, **4.4.1**. A warning names the files that kept an edge of their own because they have fewer additions. |

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.4.1 | *(only when some files have both regions and others do not)* Do you want to continue? `(y/N)` (above it, in grey: the files without both an oxidised and a reduced region, and "A file needs both to be shown in % oxidised.") | the regions of every file are listed, then **4.5** (**4.6** when Δψ cannot be worked out) | **4.4** again, with the edges where you left them |

### 4.D Δψ, the membrane potential

Δψ is worked out from how reduced the two b haems, bH and bL, are, at the temperature of 3.1.2 (the maths is in `MATHS.md`). It can be worked out for a file with both regions (4.4), when the fit has one bH and one bL. 4.5 is asked only when at least one file has both regions and the fit has the two haems. Otherwise nothing is asked and the run has no Δψ; for a dataset saved with Δψ switched on, a message says what it needs.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.5 | *(only when Δψ can be worked out)* Do you want to work out Δψ? `(y/N)`, or `(Y/n)` when the Δψ box is already ticked (above it, in grey: "Δψ is the membrane potential, worked out from how reduced bH and bL are.") | the plot is redrawn **(plot)** with a **Δψ (mV)** panel under the haems (or where you moved it to), the **Δψ** box is ticked and shows its numbers, and a message says it has its own panel and ends "Change the numbers of the method in the Δψ box above the plot, and untick it there to leave Δψ out.", with under it "To compare fits, click Keep to compare, change the fit or the scatter, then click Keep new or Keep old."; then **4.6** | **4.6** (no Δψ in the run; the box is unticked) |

The tick of the **Δψ** box switches Δψ on and off at any time while it can be worked out, and the plot is redrawn with or without its panel.

The Δψ panel is the lowest panel of the plot of each file with both regions: one line, with gaps where bH or bL is less than 10 % or more than 90 % reduced, as Δψ cannot be given there. A file without both regions has no Δψ panel. The panel is also in the figure saved for each file (section 5), and Δψ is in the workbook of each file written in the experiment export (5.9). The limits of 10 and 90 % are the ones the program starts with.

The **Δψ** box holds the numbers of the method, and shows them only while Δψ is ticked. No question is asked: type a number, press Enter (or click away), and the Δψ panel is redrawn at once, with one line in the terminal saying what the numbers now are. The numbers are kept with the dataset. To see what a change does, click **Keep to compare** (4.A) first: the Δψ of before the change stays on the plot on the left (side by side) or in the panel as a dashed, paler line (overlaid), with the largest and the average distance between the two under the plot. Then click **Keep new** to carry on with the change, or **Keep old** to undo it.

- ***b*<sub>H</sub>** and ***b*<sub>L</sub>** (written as in the figures): the midpoint potential of each haem while the other is oxidised (mV); 40 and −20. After each arrow, greyed, is its midpoint while the other haem is reduced (−30 and −90): the program fills it in, and it cannot be typed in.
- **shift**: how far each midpoint falls when the other haem is reduced (mV); 70. Typing it refills both greyed numbers (a shift of 60 gives −20 and −80); typing a midpoint refills its own (bH 50 gives −20).
- **Paper's values** puts back 40, −20, 70, the share of 0.5 and the limits of 10 and 90 %. The temperature stays.
- **More options**, unticked, leaves the other numbers as one grey line ("share 0.5 · 37 °C · given between 10 and 90 % reduced"); ticked, they are boxes: the **Share** of the membrane potential that lies between the two haems, the **Temperature** of the runs (°C, the value of 3.1.2) and the two limits (**Given between** ... **and** ... **% reduced**).
- A number that cannot be used turns its box red, with one sentence under the row, and the number in use stays: something that is not a number; a share of 0 or less; a temperature outside 0 to 100 °C (as 3.1.2); a lowest limit that is not above 0 and below the highest; a highest limit that is not above the lowest and below 100.

### 4.E The averaging windows

An averaging window is a stretch around an addition that an average is taken over. There are two kinds, and you can have either or both:

- A **settled window** ends a set time before the next addition (the last one 0.5 min before the end of the recording): the level once things have settled after the addition before.
- A **quick window** starts a set time after its own addition: the quick response to it.

The windows are placed around the events as they were left in 3.B: an event marked `ignore` gets none. Every window of a kind has the same length unless you set one on its own, so each moves with its addition in every file and one setting fits the whole dataset. The window before the first addition is the baseline, which both kinds are compared with; it is there whenever either kind is ticked, with the length and the gap of the settled windows unless it has its own.

- The baseline is **shaded gold** on the plot of every file, with "baseline" and its length by its first edge. It is as long as a settled window and ends the same time before the first addition, so pulling its edges changes the settled windows too.
- The settled windows are **shaded blue** on the plot of every file, 120 s long and ending 30 s before the next addition; the quick windows are **shaded green**, 30 s long and starting 10 s after their addition; or both are as they were saved with the dataset. They are over the plot only in this step; the steps before it show none.
- **Pull the start** of a settled window, by its handle or its line, to change its length; **pull its end** to change the gap before the addition. **Pull the start** of a quick window to change how long after the addition it starts (its length stays); **pull its end** to change its length. Every window of that kind in every file follows, in steps of 5 s, and the plot is not drawn again. **Pull the end of the last settled window** to change how long before the end of the recording it ends (0.5 min unless changed).
- **Type** the numbers in the two rows under **Averaging** in the Time regions box above the plot, in seconds: **Settled window** and **Gap before the next addition** in the first, **Quick window** and **Start after the addition** in the second. Press Enter or leave the box. A window of 0 s is not taken.
- **Adjust each window**, beside **Apply to every experiment** under the two rows: ticked, a drag moves only the window dragged, the boxes of its row show that window (named beside its ticks, for example "settled window 2"), and a number typed there changes it alone; before a window of a kind is dragged, a number typed changes every window of that kind ("every settled window"). Unticked, each window keeps what it was given until the next drag or number of that kind, which puts every window of the kind back to one value.
- **Use**, a numbered tick for each window of the file shown under each row (the baseline has none): untick one to leave that window out. It is shaded grey with no edges, it is not averaged, its row stays in the Averages sheet with empty numbers, and the figures leave a gap.
- **Apply to every experiment**: ticked (as the step opens), a change is made on every file; unticked, on the file shown only, and that file keeps windows of its own. The drop-down marks the files whose windows differ.
- A window that **does not fit** is shaded red with hatching: a settled window that would start before its own addition, a quick window that would end after the next addition (or after the end of the recording), or a baseline shorter than 10 s. After Continue a warning names these windows for each file; they are left out of the averages.
- **Settled windows** and **Quick windows**, the tick boxes of the two rows. Settled windows is ticked and Quick windows unticked when the step first opens on a dataset. Untick both for no windows: the windows go from the plot, nothing is averaged, and the figures of each file show none.
- The windows are saved with the dataset (in `portimao_settings.json`), ticked or not, with each window set on its own or left out and each file fixed by hand.
- When none of the files has an addition, the step is not asked and one line says there are no averaging windows.

| # | Question | Leads to |
|---|---|---|
| 4.6 | Drag an edge of any window on the plot, or type the numbers under Averaging in the Time regions box above it, where each kind of window has its tick box. Click Continue when the windows look right, or untick both kinds for none. (above it, in grey: what the windows are, "The baseline (gold) is the window before the first addition, as long as a settled window; every other window is compared with it.", "A settled window (blue) ends a set time before the next addition, the last one 30 s before the end of the recording (pull its end to change that); a quick window (green) starts a set time after its addition.", which edge to pull for what, and "A change moves every window of its kind; tick Adjust each window to move only the window you drag, and the boxes then show that window. Untick a number under Use to leave that window out (grey). With Apply to every experiment unticked, a change is made on the file shown only.") | **Continue**: one line for each kind says the windows chosen (or one line that there are none), one line names the windows set on their own and those left out, one the files with windows of their own, a warning names those that do not fit (not those left out), the plot is redrawn with the windows **(plot)**, then **5.1**. |

Three later figures need the averaging windows: the 2x2 grid (**6.3**), the time response (**7.1**) and the haem and OCR response (**7.2**). They use the windows chosen here and never ask for a window or a gap of their own. When you say yes to one of them and no windows are set up (both kinds unticked in 4.6, or no file with an addition), one line says "No averaging windows are set up, and this figure needs them.", and 4.6.1 is asked before the figure's own questions. It keeps this number wherever it is asked. The OCR as % of baseline is offered under OCR as only once the windows are set up, so it never asks.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.6.1 | Do you want to add them now? `(Y/n)` | **4.6** opens on the plot of every file, by itself (nothing else of the processing is asked again, and the boxes stay greyed out apart from the rows of the windows), with Settled windows ticked; the guide opens step 13 (Averaging windows) meanwhile, then goes back to the figure. After Continue, with windows set up, the figure's own questions follow; with none still, one line says the figure is not made and the next figure is asked | one line says the figure is not made, and the next figure is asked |

Once windows are added this way they are the dataset's windows: the later figures do not ask, and they are saved with the dataset.

Each of the three figures uses one kind of window, with the baseline. With both kinds set up, 4.6.2 is asked before the figure's own questions (after 4.6.1 when that was asked); it keeps this number wherever it is asked, and each figure remembers its own answer. With one kind set up nothing is asked: one line says the figure uses that kind.

| # | Question | Leads to |
|---|---|---|
| 4.6.2 | Which windows should this figure use? `(1/2)` 1) Settled, before the next addition; 2) Quick, after each addition | the figure's own questions |

The plots and the workbook of each experiment (section 5) show both kinds: the quick windows green, the settled windows blue and the baseline gold with "Baseline" written above it, and a **Kind** column in the Averages sheet.

---

## 5. Experiment export: the figure of each file

The figure saved for each file is drawn at once **(plot)**, at its real size and as it will be saved, with the standard settings or, for a dataset run before, the settings last saved for it. Every panel is in it:

- the set and measured oxygen, always;
- the OCR, always, as **OCR as** in the View box shows it: per OD (µM min⁻¹ OD⁻¹) as standard when you scale by OD (3.1.1.1), otherwise µM min⁻¹;
- while **Haem decomposition** is ticked, every haem of the fit, as **Haems as** in the View box shows them: ΔD, the change from the start, as standard (scaled by OD as well when its per OD box is ticked); unticked, no haem panels;
- Δψ (mV) as the lowest panel while the **Δψ** box is ticked, for a file with both regions;
- the event labels at the **Angle** of the View box (45° as standard);
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
| 5.8 | Do you want to go back to any of these steps? 1) No, continue 2) Set-up: trimming and ignoring 3) Set-up: OD values, temperature and event labels 4) Experiment processing 5) Experiment export: the figure of each file | **1**: **5.9**. **2, 3, 4 or 5**: that section's questions are asked again from its first question, with your answers as the defaults. Your answers to the later sections are kept. Then **5.8** is asked again. |

### 5.G The workbook of each file

The processing and the figure are accepted, so each experiment's workbook is written now, with its plot, and not when the run starts. One line says what it holds: "Every experiment gets a workbook with everything worked out for it: the measured and set oxygen, the OCR, the haems, Δψ, the averages, the events and your OD/volume/dilution entries."

| # | Question | Leads to |
|---|---|---|
| 5.9 | *(only when Export csv did not write the spectra)* Do you want to export the spectra as csv files too (large, and it takes a while)? `(y/N)` | the plot and the workbook of every file are saved, then **6.1** |

If Export csv wrote the raw CSVs (choice 4 or 5), 5.9 is not asked: one line says the spectra are not written again, and the workbook of each experiment still lists them on its **Spectral data** sheet.

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

As in section 6, the **Plotting data …** sign is on the plot while each picture is drawn. Both summary figures need the haem fit. If the haems were not decomposed in section 4 (or Haem decomposition was unticked), the fit questions (**4.1.1**, and **4.1.2** if needed) are asked first; only the fit files are offered here, not the components found from the data. If the `fits/` folder holds no `.csv` file, or the fit cannot be used, a message says so and the figure is skipped. Both figures also average around the events, over the averaging windows of 4.6. With none set up, **4.6.1** is asked after the fit and before the figure's own questions (section 4.E); without windows the figure is not made and the next figure is asked. With both kinds of window set up, **4.6.2** then asks which kind the figure averages over; in the time response, the difference spectrum is the last window of that kind minus the one before it.

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
| 9.1 | Do you want to start? `(Y/n)` | Your answers are saved in the data folder (`portimao_settings.json`) for the next time this dataset is opened, and the run starts. If the data folder cannot be written to, a message says the dataset will start from the standard settings next time. Every file is processed again for the multi-experiment figures and summaries, which are then made; a plot or workbook saved at 5.9 is not written again (unless a summary figure changed the fit), and one not saved then is written now. | The program stops and nothing else is changed: data you exported with Export csv, and the plots and workbooks saved at 5.9, are kept, and the last line says so. |
