# Portimao question flow (V2.34)

Every question in the order it is asked, with where each answer leads. The question text is the text on screen.

**How to read it**

- The questions are asked in Portimao's window. If the window cannot open, nothing is asked: a message says why and what to do (in the Mac app, with a **Copy details** button to send the details with the Mac problem form).
- **The guide** on the left of the window lists the steps, numbered, one line each, under the names of the stages: **Import** (steps 1 to 4, sections 1 and 2 here), **Set-up** (5 to 9, section 3), **Experiment processing** (10 to 13, section 4), **Experiment export** (14 Finalise figures and 15 Export, section 5), **Dataset figures** (16 Dataset set-up and 17 Build a figure, section 6) and **Dataset export** (18, section 9). The guide has four levels, largest first: the stage name, the steps under it, then in the open step the explanations and the question. Only the stage of the step open lists its steps, its name large and bold; the others show their name a little smaller and paler, with the numbers of their steps and a tick once they are passed. In the stage shown, a step done has a tick, a step passed without being asked (the previous processing of a dataset never opened, the OD values when you do not give them) stays in the list, greyed, with "· not needed this run", and the steps to come are paler.
- **The step open** sits under its line, marked ▸: what was said since your last answer (the explanations in a light grey, the messages), then the question in pink, larger than the rest, then its answers. The stage name is not repeated there. What was said before your last answer folds away when the next question is asked; all of it stays in the run's log.
- **Answers are clicked**, not typed:
    - something done on the plot or in the boxes above it (2.1, 4.4, 4.6, 5.1): one big **Continue** button (in 2.1 with **Export full + trimmed csv** and **Export trimmed csv** above it, buttons of the same size; in 5.1 named **Export**, for what it opens);
    - a yes or no question: **Yes** and **No**, one above the other;
    - a numbered list: a button for each choice; a long list in two columns;
    - several choices from a list: a tick button for each, then **Continue** (greyed while none is ticked); the choices offered at first are ticked, and where the order matters it is the order you tick them in;
    - a number or a name, the only answers typed: a box that starts with what Continue alone gives (the default, with its unit in the question), then **Continue**, or Enter in the box, with "Type a number, then click Continue or press Enter." under it;
    - a table: **Confirm** under it.

  The answer Enter gives is the highlighted button, which holds the keyboard. In this list, `(Y/n)` and `(y/N)` say which of Yes and No is highlighted (the capital letter), `(1/2/3)` with a number in bold which choice is, and `[value]` what the box starts with (`[skip]`: empty, which leaves the answer out). The answer clicked is written under the question, after an arrow.
- The defaults shown here are the standard settings, offered for a dataset you have never run. Once you have started a run, your answers, your OD values and event labels among them, are saved in a small file inside the data folder (`portimao_settings.json`), and the next time that dataset is opened you choose whether to load them (**1.3**), on this computer or on another one the folder is copied to.
- After an answer that cannot be used (a number out of its limits), one line in red says what to type, and the question waits for the next answer.
- Some answers are typed in a table, which opens in the step under the last few lines of its text: one row per file (the OD values, 3.2.1) or per event (the event labels, 3.3). Click a cell and type, or select what is there and type over it; Tab moves across and Enter moves down. A cell that cannot be used turns red. Press **Confirm** under the table when it is filled in. If a cell is still wrong, or a label is empty, one line names it and the table stays open; the OD table can be confirmed with cells left empty (3.2.1). The grey text of a table (its headings, the file names, the text in the file) is light enough to read on the dark card, and what you type is bold in a plain font. A row of **Symbols** (µ, ⁻¹, ₂ ...) is under a table and under a box for a name.
- **Going back to an earlier step.** A change in the boxes above the plot that belongs to an earlier step opens that step in the guide: the tabs of the Time regions box belong to step 4 (Trim / Ignore), 11 (Ox / Red) and 13 (Averaging); Edit ODs to step 7 (OD values) and Edit labels to step 9 (Event labels); the fit, the background, the spectra, the Haem decomposition tick, Build a fit and Keep to compare to step 10 (Haems); the Δψ box to step 12 (Δψ); the journal, the width, the height and Export master to step 14 (Finalise figures). How the haems, the OCR and the labels are shown, the angle of the labels and the order of the panels belong to every step, and open none. The step waited at then reads **→ ... ← you were here**, the step opened says so above its messages with a few words on where to change it, and a **Back to** *step* button takes the place of the answers (the trim step keeps its two export buttons above it): click it to answer the question waiting. A click on the line of a step done opens it in the same way. A change that belongs to a later step ticks that step, as done: the guide is a guide, and the steps can be done in any order.
- The **Help** button under the answers is greyed out for now.
- **Yes → / No →** says which question comes next. **Next** means the next question in this list.
- In sections 1 to 5 and 9 the numbers on screen are the numbers here. A question asked again keeps its number, and when a question is skipped the next one keeps its own, so 3.3 follows 3.2 when the OD values are not asked. A question asked inside another's step shows that step's number: the name of each component shows 4.1.7, replacing a fit file 4.1.9. The step of section 6 shows its number, 6.1.
- A "Do you accept...?" question with one way to change is a yes or no question, `(Y/n)`: the grey line just above it says what **No** does ("Click No to change the labels again."). One with more ways to change is a numbered list starting with **1) Yes, accept**, which moves on; its other answers (**2) No, ...**, and **3**, **4** ... where there are more) each say what is asked again, with your last answers as the defaults.
- The plot on the right is redrawn after each step marked **(plot)**. You can flick through the files with the arrows or the drop-down above the plot at any time while a question waits. The file shown and the one on each side of it are redrawn at once; any other file is drawn when you go to it, with its last plot under the **Plotting data …** sign meanwhile (clicking a cell of a table shows its file in the same way). After **5.9**, every file shows the plot saved for it; a file whose plot could not be saved says so. In section 6 the page of the dataset figure takes the place of the plot.
- The **boxes** above the plot, in one row under the file name and its arrows, show what the run uses. Every question that sets one of them says so, and it can be changed there at any time without typing the answer again:
    - **Time regions**: three tabs, **Trim / Ignore**, **Ox / Red** and **Averaging**, the one pressed having its edges on the plot and its numbers in the box (section 2, 4.C and 4.E). The guide presses the tab of its step (2.1, 4.4, 4.6). A tab can be pressed at any time: its edges come onto the plot (Trim / Ignore on the whole recording, with the edges in use as red dashed lines; the other two on the processing plot), and the change is used when you press another tab, or answer the question that waits. The edges of the step that waits stay as you left them meanwhile. A changed trim keeps the regions and the averaging regions at their minutes; nothing is exported again by itself (press an export button in the trim step).
    - **View**, one line each, in this order: **OCR as** (how the OCR is shown) with its **per OD** box, **Haems as** (how the haems are shown) with its **per OD** box, **Labels as** (what the event labels show), the **Label angle** of the event labels (0 to 90°, 45 at first), then the **Edit ODs** and **Edit labels** buttons side by side. Edit ODs is always there, so OD values can be given later even after answering No at 3.2.
    - **Haem decomposition**, with its tick as the title (ticked when the haems are worked out and shown), in this order: **Spectra** (the spectrometer whose spectra hold the haems), the **Scatter** (the background fitted under the haems) with **ⓘ** for its formula, the **Fit**, **Build a fit** (with **Save fit**) beside **Do PCA**, and **Keep to compare** (with **Keep old** and **Keep new** under it while one is kept, and beside them the switch **Side by side / Overlaid**: side by side shows the kept one as a plot of its own headed Old on the left of the plot in use, headed New; overlaid draws it faint and thin under the plot in use, drawn bold; side by side at first, and the choice is kept with the dataset).
    - **Δψ**, with its tick as the title: the numbers of Δψ, shown while it is ticked (4.D). The tick can be clicked only while Δψ can be worked out.
    - **Figure**: the **Journal**, the **Width** and the **Height** of the figure of each file, the **Export master** button and the **Standard order** button.
    - Under the boxes, on the right, the switch **Standard plot | Difference spectrum** (no question). Difference spectrum shows, in place of the standard plot, the mean spectrum of the reduced region minus that of the oxidised region of the file shown (mOD), with each haem of the fit in its colour, the background dotted, the fit dashed and the residual in a small panel underneath (`MATHS.md` section 9). It can be clicked only while the haems are worked out and the file shown has both regions (4.4); for any other file it is greyed, with a grey note saying to set both regions, and the file keeps its standard plot. The choice is kept with the dataset.
    - The **panels** of the plot of a file can be moved: while the boxes can be used, a small up and a down arrow sit left of each panel, and a click moves that panel one place (the arrow that cannot be used, up on the top panel, is paler). No question is asked: the plot is redrawn at once and one line in the terminal says the new order. The order holds for every file and for the figure saved for each, and is kept with the dataset. A panel that comes later (a haem ticked since, Δψ switched on) is drawn just above the panel that follows it in the standard order, or at the bottom. **Standard order** puts the panels back: oxygen, OCR, the haems a then b then c, Δψ. The arrows are away while edges are dragged on the plot (trimming, the regions, the averaging regions) and while the plot is being redrawn.
    - **Spectra** is shown only when your files share more than one spectrometer (Cyt and NADH). Picking the other one works the haems out from its spectra.
    - **Haems as** swaps the haems between ΔD (mOD), the change from the start; % oxidised (reduced region = 0 %, oxidised region = 100 %); and Absorbance (mOD). % oxidised is in the list only when at least one file has both regions (4.4); a file without both stays in ΔD, as its axis says. The choice holds for every plot of your files and for the figure saved for each file.
    - **per OD** (beside Haems as) scales the haems by OD. The box is shown only once you have entered the OD values of every file (3.2.1). It is greyed while the haems are in % oxidised, which has no per OD.
    - **OCR as** swaps the OCR between µM min⁻¹; % of the range; and % of baseline (the average in the baseline = 100 %), in the list only once the averaging regions are set up (4.6). Its **per OD** box, shown once you have entered the OD values of every file (3.2.1), makes µM min⁻¹ the OCR per OD (µM min⁻¹ OD⁻¹); it is greyed for the two % views, which have no per OD. A file without a baseline (less than 10 s of data before its first addition, or no addition) keeps its usual OCR, as its axis says, and one line says so. The choice holds for every plot of your files and for the figure saved for each file.
    - **Labels as** swaps the event labels between **In the chamber** (the concentration in the chamber after the addition, `400 µM KCN`; the standard) and **What was added** (`10 µL of 200 mM KCN`). An event with no stock and volume shows its concentration in the chamber either way, and one with no concentration its label alone. The choice holds for every plot of your files, the figure saved for each file and the labels under the averaging regions of the haem and OCR figure, and is kept with the dataset.
    - While your files are on the plot (sections 2 to 5), you can change it whenever a question waits. The plot is redrawn at once, the run uses the change, and the question goes on waiting.
    - **Label angle** sets the angle of the event labels on every plot and in the figure saved for each file. A number outside 0 to 90 turns the box red, with what to type under it.
    - **Edit ODs** and **Edit labels** open their step again in the guide (OD values or Event labels, with "you were here" on the step that waits) and its table (3.2.1 or 3.3), with **Confirm** above the **Back to** button; after Confirm the plot is redrawn and the guide goes back to the question that waits.
    - Unticking Haem decomposition leaves the haems out of the run. Ticking it, or picking a fit, works them out with the fit shown and ticks the box.
    - If a fit cannot be used, one line says why and the box goes back to what it showed.
    - A new journal, width or height redraws the plot only in section 5, the one plot drawn at the figure's size. Before that the change is kept for section 5.
    - The **Journal** list holds every journal of the `journals` folder. Choosing one makes the figure follow what it asks: the widths offered, the tallest figure, the text sizes, the panel letters, the font and the thickness of the lines.
    - **Export master** saves one page of the journal as a PDF in the results folder (`<file>_master_<journal>.pdf`): the figure of the file shown at its printed size, a box where its legend goes and grey lines where the text of the paper goes. It works in section 5, where that figure is on the plot; before that, one line says so. With **None** the page is Nature's. A journal whose page size is not known is shown on an A4 page, and the page says so.
    - The boxes are greyed out while you choose the folder, during the questions of 4.A.1, and after section 6; in section 6 the strip of the page takes their place.
- While the program draws a picture of its own (the components found from the data), the **Plotting data …** sign is on the plot: a large spinning wheel on a yellow card in the middle of the plot, with "Plotting data …" under it in large letters. The same sign shows while a file is read or a plot redrawn, and whenever the program is still working on an answer or a Confirm 0.2 s after the click (after an OD value is confirmed, for example). It goes when the picture is shown or the next question is asked.
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
| 1.3 | *(only for a dataset opened before; above it: "Its trim and ignore edges, OD values, labels, fit, regions, Δψ, averaging regions and figure were saved with it. No starts it fresh, as a dataset never opened.")* Do you want to load the previous processing? `(Y/n)` | every answer saved with the dataset is offered as the default from here on; the standard plot is drawn **(plot)** with them, then **2.1** | the dataset starts from the standard settings, as one never opened: the standard edges, no OD values, the labels as written in the files, the standard fit, no regions, no Δψ, the standard averaging regions and figure. A line says what was saved with it is replaced only when you start the run (9.1). The standard plot is drawn **(plot)**, then **2.1** |

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
- The edges start where they were left the last time the dataset was run; for a dataset never run, the first 5 minutes are ignored and nothing else. When the edges are opened again (the **Trim / Ignore** tab of the Time regions box at any later step, or a click on the step in the guide), the limits they had are drawn as red dashed lines, so you can see how far you moved them.
- **Export full + trimmed csv** and **Export trimmed csv**, above Continue: the quick export, the only one before the experiment export. Each writes the spectra as csv files with the edges as they are (section 3.C), without asking: those of the trimmed data, and with **Export full + trimmed csv** those of the whole recording of each trimmed file too; then the step waits again. **Continue** skips it, and Portimao can be closed once it has written the files. No workbook is written here: the summary (the plot and the workbook of each file) is written at **Export** (5.9). Nothing is exported again by itself when the edges change later: the trim step opened again (the Trim / Ignore tab) keeps its two export buttons, to write new files.

| # | Question | Leads to |
|---|---|---|
| 2.1 | Drag the bars on the plot, or type the times in the Time regions box. Check each experiment, then press Continue. (above it, in grey: the key, "Ticking Apply to all copies the times of the experiment shown to every experiment; it unticks itself when the next one is shown." and "The export buttons write the spectra of every experiment as csv files with these times; Continue skips them.") | **Export full + trimmed csv** or **Export trimmed csv**: the csv files are written (3.C), then 2.1 waits again. **Continue**: the limits of every file are listed, the plot shows the data they keep **(plot)**, then **3.1**. |

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

The quick export comes only from the two export buttons of the trimming step (2.1), the first time and whenever the Trim / Ignore tab is opened again; it is not offered after the labels. It asks nothing: one grey line gives the size ("Writing the spectra of each file as csv files (the trimmed about *size*, the full about *size*); this takes a while."; and, after **Export full + trimmed csv** when no file is trimmed, first "No file is trimmed, so this writes the same as Export trimmed csv."), the files are written, a message says where, and the trimming step waits again. **Export trimmed csv** writes the spectra of the trimmed data; **Export full + trimmed csv** those and the whole recording's of each trimmed file.

The sizes are worked out for your files, less for a trimmed one: about 1.2 GB of spectra for each 100 MB `.paf` file. Each file is exported to its own folder in the results folder, `<results>/<file>/`:

- the spectra csv files: one per spectrometer and kind (`Cyt_transmiss.csv`, `Cyt_intensity.csv`, `Cyt_attenuation.csv`, and the same for `NADH`), wavelengths down and one column per spectrum headed by its time (min), the time 0 where the file is trimmed. The workbook written at **Export** (5.9) lists them on a first sheet, **Spectral data**.
- `full/`, with **Export full + trimmed csv**, only for a file you trimmed: the same for the whole recording. It does not depend on the edges, so it stays as it is when they change.

No workbook is written, nothing is scaled by OD, decomposed or averaged, and the ignored parts are included.

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
| 4.1.1 | Where should the spectral range start (nm)? | **4.1.2** |
| 4.1.2 | Where should the spectral range end (nm)? | **4.1.3** (or this question again if the analysis cannot be run, for example the range is too narrow) |
| 4.1.3 | How many components should be found? (The data suggest *N*; use as few as describe the data, extra ones only fit noise.) | a whole number; the number used last time, or else the suggestion, is the default; then **4.1.4** |
| 4.1.4 | Do you want to rotate the components so each is as peak-like as possible (varimax)? `(Y/n)` | **4.1.5** |
| 4.1.5 | Over how many nm should the components be smoothed to remove their noise (0 for none)? (default 4, or the width used last time; at most a quarter of the spectral range) | the components and the examples are drawn **(plot)**, with one line per component (type, peak, share of the change) and the residual, then **4.1.6** |

| # | Question | 1 → | 2 → | 3 → | 4 → |
|---|---|---|---|---|---|
| 4.1.6 | Do you accept these components? `(1/2/3/4)` | **4.1.7** | **4.1.3** (the number of components) | **4.1.1** (the spectral range) | *No, keep the fit in the box instead*: back to **4.1**, the fit as it was |

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

### 4.E The averaging regions

An averaging region is a stretch before an addition that an average is taken over: it ends a set time before the next addition (the last one 0.5 min before the end of the recording), the level once things have settled after the addition before. The quick regions, which start a set time after their own addition, are hidden for now: they are not offered, and a dataset saved with them has them switched off.

The regions are placed around the events as they were left in 3.B: an event marked `IGNORE` gets none. Every region has the same length unless you set one on its own, so each moves with its addition in every file and one setting fits the whole dataset. The region before the first addition is the baseline, which every other region is compared with; it has the length and the time before the addition of the other regions unless it has its own.

The Averaging tab of the Time regions box holds, from the top:

- **Averaging regions**, a tick box: ticked when the step first opens on a dataset. Untick it for no averaging regions: the regions go from the plot, the rest of the tab is greyed, nothing is averaged, and the figures of each file show none.
- **Use**, a numbered tick for each region of the file shown (the baseline has none): untick one to leave that region out. It is shaded grey with no edges, it is not averaged, its row stays in the Averages sheet with empty numbers, and the figures leave a gap.
- **Adjust region manually**, with a button for each region beside it (**Baseline**, **1**, **2** ...): ticked, it picks region 1, and you pick another with its button. Only the region picked (its button bold and pressed in) changes, on the file shown only, by dragging its edges or typing its numbers; the other regions are grey with no edges until picked, and **Apply to all** is greyed. With the last region picked, a note says its time is before the end of the file, and the second box sets that. Unticked, each region keeps what it was given until the next change of that number, which puts every region back to one value.
- **Region length (s)** and **Time before next addition (s)**: type the numbers in seconds, then press Enter or leave the box. They change every region, or the region picked while Adjust region manually is ticked. A region of 0 s is not taken.
- **Apply to all**: unticked as the step opens, so a change is made on the file shown only, and that file keeps regions of its own. Ticking it copies the regions of the file shown to every file once, and a change is made on every file while that file stays shown; it unticks itself when the next file is shown. The drop-down marks the files whose regions differ.

On the plot:

- The baseline is **shaded gold** on the plot of every file, with "baseline" and its length by its first edge; the other regions are **shaded blue**, with "region" and their length by the first one's edge, 120 s long and ending 30 s before the next addition, or as they were saved with the dataset. They are over the plot only in this step; the steps before it show none.
- **Pull the start** of a region, by its handle or its line, to change its length; **pull its end** to change the time before the addition. Every region in the file follows (only the region picked while Adjust region manually is ticked), in steps of 5 s, and the plot is not drawn again. **Pull the end of the last region** to change how long before the end of the recording it ends (0.5 min unless changed).
- A region that **does not fit** is shaded red with hatching: a region that would start before its own addition, or a baseline shorter than 10 s. After Continue a warning names these regions for each file; they are left out of the averages.
- The averaging regions are saved with the dataset (in `portimao_settings.json`, under their older name `window`, so a dataset saved before still opens), ticked or not, with each region set on its own or left out and each file fixed by hand.
- When none of the files has an addition, the step is not asked and one line says there are no averaging regions.

| # | Question | Leads to |
|---|---|---|
| 4.6 | Drag the averaging regions on the plot, or type their numbers in the Time regions box, press Continue when ready. (above it, in grey: what the averaging regions are, "The baseline (gold) is the region before the first addition; every other region (blue) is compared with it.", which edge to pull for what, "A change moves every region, on the file shown; ticking Apply to all copies its regions to every file, and it unticks itself when the next file is shown. Untick a number under Use to leave that region out (grey), or untick Averaging regions for none." and "Tick Adjust region manually to change one region of one file: pick it with the buttons beside it, then drag its edges or type its numbers; the other regions are grey until picked.") | **Continue**: one line says the regions chosen (or one line that there are none), one line names the regions set on their own and those left out, one the files with regions of their own, a warning names those that do not fit (not those left out), the plot is redrawn with the regions **(plot)**, then **5.1**. |

Three later figures need the averaging regions: the 2x2 grid (**old 6.3**), the time response (**old 7.1**) and the haem and OCR response (**old 7.2**). They use the regions chosen here and never ask for a region or a gap of their own. When you say yes to one of them and no averaging regions are set up (Averaging regions unticked in 4.6, or no file with an addition), one line says "No averaging regions are set up, and this figure needs them.", and 4.6.1 is asked before the figure's own questions. It keeps this number wherever it is asked. The OCR as % of baseline is offered under OCR as only once the averaging regions are set up, so it never asks.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.6.1 | Do you want to add them now? `(Y/n)` | **4.6** opens on the plot of every file, by itself (nothing else of the processing is asked again, and the boxes stay greyed out apart from the rows of the averaging regions), with Averaging regions ticked; the guide opens step 13 (Averaging regions) meanwhile, then goes back to the figure. After Continue, with averaging regions set up, the figure's own questions follow; with none still, one line says the figure is not made and the next figure is asked | one line says the figure is not made, and the next figure is asked |

Once averaging regions are added this way they are the dataset's: the later figures do not ask, and they are saved with the dataset.

Each of the three figures uses one kind of averaging region, with the baseline. While the quick regions are hidden only the settled regions can be set up, so 4.6.2 is not asked. With both kinds set up (once the quick regions come back), 4.6.2 is asked before the figure's own questions (after 4.6.1 when that was asked); it keeps this number wherever it is asked, and each figure remembers its own answer. With one kind set up nothing is asked: one line says the figure uses that kind.

| # | Question | Leads to |
|---|---|---|
| 4.6.2 | Which averaging regions should this figure use? `(1/2)` 1) Settled, before the next addition; 2) Quick, after each addition | the figure's own questions |

The plots and the workbook of each experiment (section 5) show both kinds: the quick regions green, the settled regions blue and the baseline gold with "Baseline" written above it, and a **Kind** column in the Averages sheet.

---

## 5. Experiment export: finalise figures and export

Two steps in the guide: **Finalise figures** (5.1) and **Export** (5.9). Both are asked while the boxes above the plot still work, so an earlier step can be changed from the boxes, or opened with a click on its line in the guide, while either waits.

The figure saved for each file is drawn at once **(plot)**, at its real size and as it will be saved, with the standard settings or, for a dataset run before, the settings last saved for it. Every panel is in it:

- the set and measured oxygen, always;
- the OCR, always, as **OCR as** in the View box shows it: per OD (µM min⁻¹ OD⁻¹) as standard once every OD value is in (3.2.2), otherwise µM min⁻¹;
- while **Haem decomposition** is ticked, every haem of the fit, as **Haems as** in the View box shows them: ΔD, the change from the start, as standard (scaled by OD as well when its per OD box is ticked); unticked, no haem panels;
- Δψ (mV) as the lowest panel while the **Δψ** box is ticked, for a file with both regions;
- the event labels at the **Label angle** of the View box (45° as standard);
- the journal, the width and the height of the **Figure** box: Nature, 1 column wide and 0.5 of a page tall as standard.

Every change in the boxes, and every click on the arrows beside the panels, redraws the figure at once.

| # | Question | Leads to |
|---|---|---|
| 5.1 | Use the arrows to change the order of the panels, or change earlier settings. When ready, click Export to choose which files to export. (above it, in grey: "Use the Figure box above the plot to set the figure to a journal's standard.") One button, **Export**. | **Export**: **5.9**. |

The % of baseline (OCR as) is the OCR divided by its average in the baseline (the averaging region before the first addition, 4.6) × 100, so the baseline is 100 %; it is offered once the averaging regions are set up. A file without a baseline keeps its usual OCR (per OD if you entered OD values, otherwise µM min⁻¹), as its axis says, and one line says so.

How the haems are shown (**Haems as**): ΔD (mOD), the change from the start; % oxidised (reduced region = 0 %, oxidised region = 100 %), *only offered when at least one file has both regions (4.4)*; and Absorbance (mOD). There are no 5.2 to 5.6: the numbers of the later questions are kept.

- A file without both regions stays in ΔD, as its axis says, while the files with both are in %.
- A dataset saved with % oxidised opens with ΔD when no file has both regions any more.
- No concentration: only cells are measured, and a haem amount depends on the size of its shape; a dataset saved with concentration opens with ΔD.

### 5.E Journal and size

The Figure box sets the journal, width and height of this figure, so these questions are not asked here. They are listed because the fixed figures of section 7 ask their own size with them, each with its own default size.

| # | Question | Leads to |
|---|---|---|
| 5.7 | Which journal format would you like? 1) None (use the default: Nature, *the figure's default width and height*) 2) Nature 3) Science 4) Cell 5) PNAS 6) ACS journals 7) PLOS ONE (every journal of the `journals` folder) | **None**: the default size is used. **A journal**: **5.7.1** |
| 5.7.1 | How wide should the figure be? (the widths that journal allows: 1, 1.5 or 2 columns for most, 1, 2 or 3 columns for Science) | **5.7.2** |
| 5.7.2 | How tall should the figure be, as a fraction of the page height (1 = a full page = *X* mm)? | the figure is drawn at its real size **(plot)** |

There is no 5.8: going back is done from the guide. The number 5.9 is kept.

### 5.G Export

The figures are finalised, so each experiment's summary is written now, and not when the run starts. The summary is the plot and the workbook of each file; the workbook always holds the trimmed data, with the times trimmed on its **Metadata** sheet. The csv files are the spectra (as in 3.C).

| # | Question | Leads to |
|---|---|---|
| 5.9 | What do you want to export? `(1/2/3)` 1) Export the summary 2) Export the summary and the trimmed csv 3) Export the summary and the trimmed and full csv (3 only when a file is trimmed) (above it, in grey: "The summary is the plot and the workbook of each file (about *size*). The csv files are the spectra: large (the trimmed about *size*, the full about *size*), and they take a while to write.") Your last answer is highlighted, or 1 the first time. | **3**: the csv files of the whole recording of each trimmed file are written in its `full/` folder. Then, for every answer, the plot and the workbook of every file are saved (with the trimmed csv files at **2** and **3**), then **6.1** |

Csv files the quick export of the trim step wrote are not written again: the trimmed ones while the trim edges are still those they were written with (one line says so, and the workbook still lists them on its **Spectral data** sheet), and the full ones of a file still trimmed.

One line says what the workbook holds: "Every experiment gets a workbook with everything worked out for it: the measured and set oxygen, the OCR, the haems, Δψ, the averages, the events and your OD/volume/dilution entries." Each file is then read once more, so this takes a moment: the terminal counts the files ("Saving file 3 of 12: *name*"), and for each the plot is saved in the results folder (svg and png, in the file's own folder; unless nothing is plotted) and shown in the window **(plot)**, and its workbook is written beside it, with the trimmed csv files at **2** and **3**. A plot or a workbook that could not be saved (a workbook open in Excel) says so in one line, and is tried again when the run starts.

Every workbook has each sheet named in plain words with the unit in its headings: **Measured O2**, **Set O2**, **OCR** and, when they were worked out, **OCR per OD**, **OCR % of range**, **OCR % of baseline** (every file with a baseline, whichever way the OCR is plotted), the haems in every view (**Haems ΔD**, **Haems absorbance**, **Haems % oxidised**, and the first two **per OD**), **Δψ** and **Averages**; then **Events**, **How it was worked out** (the fit and the background, where ΔD starts, the oxidised and reduced regions and each haem's level in them, the numbers Δψ was worked out with, the OD scaling, the baseline region and the average OCR in it that is 100 % of baseline) and **Metadata**.

- The run does not write these plots and workbooks a second time.
- If you cancel after this, the plots and workbooks stay in the results folder, and the closing line says so.

---

## 6. Dataset figures: set-up, then build a figure

Two steps in the guide: **Dataset set-up**, then **Build a figure**.

### 6.A Dataset set-up

A table says which experiment is which, so the plots of the dataset figure can split the experiments into sets. It takes the place of the file arrows, the boxes and the plot while the step is open, one row per experiment:

- **Use**: a tick. An experiment unticked is greyed, has no replicate number and is left out of the dataset figures.
- **File**: the name of the file.
- **Group 1**, **Group 2** and **Time point**: a label each. Type one, or pick one already used in that column from the list of the cell. Any cell may stay blank.
- **Replicate**: numbered by the program, never typed. The experiments in use with the same Group 1, Group 2 and time point count 1, 2, 3, in the order of their run numbers (an experiment whose name has none comes after those that have one), and otherwise in the order of the table.

Above the table, **Group 1 is:** and **Group 2 is:** name the two group columns (for example "strain" and "order of additions"); the name shows in the heading of the column, as "Group 1 (strain)". They may be left empty.

- **Filled in from the file names** the first time: `run<N>` at the end of a name, or a lone number at its end (`wt_2`), is the run number; a number of hours (`7hours`, `24h`) is the time point, written "7 h"; what is left is split at a hyphen if it has one, otherwise at its first underscore, into Group 1 and Group 2. `bd_then_kcn` and `kcn_then_bd` are written BD → KCN and KCN → BD. The same label in another case (`wt`, `WT`) is one label, spelt as first seen. So `control-bd_then_kcn-run2` is control, BD → KCN, run 2, and `knockdown_24hours` is knockdown at 24 h.
- **To fill several rows**, click a cell, then Shift-click another cell of the same column: every row between gets the label of the first.
- **Colours**: each Group 1 label has a colour, shown as a square beside it, the same on every row and used on every panel of the dataset figures. Click the square: a row of colours opens above the table, with **Cancel**; click one to give it to the label.
- **Under the table**, the sets as they stand, each with its colour and its number of experiments ("■ control · BD → KCN (n = 3)").
- The table is saved with the dataset's settings when the run starts, and opens as it was left next time; a file new to the folder is filled in from its name.
- Nothing here opens a window of its own.

| # | Question | Leads to |
|---|---|---|
| 6.1 | Check which experiment is which in the table. When it is right, click Continue. (above it, in grey: "The table on the right says which experiment is which, filled in from the file names: check it, and type over what is wrong. The dataset figures split the experiments into sets by Group 1, Group 2 and the time point, and untick Use to leave an experiment out." and "The replicates are numbered for you: the experiments with the same Group 1, Group 2 and time point count 1, 2, 3.") One button, **Continue**. | **Continue**: the file arrows, the boxes and the plot come back, then **6.2**. |

### 6.B Build a figure

The figure of the whole dataset is laid out on a page, which takes the place of the file arrows, the boxes and the plot while the step is open.

- **The page** on the right is the journal page at its printed size, drawn as large as it fits, with a faint grid of 6 × 6 cells. It starts empty: Nature, 2 columns wide and 0.8 of a page tall.
- **The strip** above the page holds the **Journal**, the **Width** and the **Height** of the page (as in the Figure box: every journal of the `journals` folder, the widths it allows, the height as a share of its page), then **Template** with **Load template** and **Save template**, and under them a button for each **plot type** that can be used now: Standard experiment, Difference spectrum, Waterfall, Single trace, Mean trace, Bar chart, Before and after, Response by region, Time points and Space for a drawing. There is no legend to place: each plot has its own small legend.
- **To place a plot**, drag across the cells it should take: the rectangle is green where it can go and red over another plot. It is always a rectangle of whole cells, and never over another plot (one red line under the strip says which plot is in the way). The plot is of the plot type last clicked in the strip, or a Standard experiment.
- **The form** of the plot then takes the place of the text on the left: its **Plot type**, in a list, and the **Cells** it takes, then what its plot type asks (a list or a tick for each choice; a Space for a drawing asks nothing), with **Done** and **Cancel**. While it is open, the plot is outlined in blue, a new drag changes its cells and a plot-type button changes its type, which starts its choices afresh. Done keeps the plot with its choices and draws it in its cells; Cancel takes it away. The text comes back after either. A choice is kept as a role (the first label of Group 1, replicate 2), never as a file name, so a template fits another dataset.
- The form of a **Standard experiment** asks: the **Experiment**, in a list of every experiment in use by its file name (it starts at the first); a tick for each panel, all ticked to start with (**Panel: oxygen**, **Panel: OCR**, one for each haem of the fit while the haems are shown, and **Panel: Δψ** when the run works it out); **Haems shown as** ΔD (to start with), Absorbance or % oxidised; and the ticks **Labels of the additions** (ticked), **Averaging regions shaded** (not ticked) and **Same scales as the other standard plots** (ticked). The plot is the plot of that experiment as in the earlier steps (the OCR as chosen in the View box, the order of the panels, the colours), at the page's journal. With the last tick on, the standard plots of the page share their scales, so their sizes can be compared: one range for the oxygen, one for the OCR, one for Δψ, and for the haems one range in ΔD and one height of range in absorbance; in % oxidised each haem keeps its own. In place of a plot that cannot be drawn, one sentence in its cells says why: its experiment is not in this dataset (a template made for another), the file could not be read, no panel is ticked, or the file has no haems in the view picked.
- The form of a **Difference spectrum** asks: the **Experiment**, in the same list; and the ticks **The part of each haem** (ticked), **Background** (not ticked), **Overall fit** (ticked), **Residual underneath** (ticked) and **Haem bands** (not ticked). The plot is the difference spectrum of that experiment, reduced minus oxidised, in mOD: the measured difference in black, each haem's part in its colour, the background dotted, the fit dashed, the residual in a small panel underneath, and behind them a shaded band in each haem's colour where that haem appears (MATHS.md section 9). In place of a plot that cannot be drawn, one sentence says why: its experiment is not in this dataset, the file could not be read, or the file has no difference spectrum (it needs an oxidised and a reduced region, and the haems worked out).
- The form of a **Waterfall** asks: **One line for** Each time point (the mean of its replicates; to start with) or Each experiment, only when the set-up has time points; the group, in a list of the Group 1 labels under the name of that column (it starts at the first); **Stacked**: The difference spectrum (to start with) or one trace (O₂, OCR, a haem, Δψ), with the same **OCR shown as**, **Haems shown as**, **Δψ shown as** and **Time 0 at** as a Mean trace, used only when a trace is stacked; **Spectra lined up on**, in a list of the haems of the fit (it starts at the first b haem) and the tick **Haem bands** (ticked), these two only in a run that works out the haems; and the tick **Labels of the additions** (ticked), used when a trace is stacked. With a trace stacked, the traces are lined up on their additions as in a Mean trace (each time point the mean of its replicates), then stacked from the top down, each moved so its highest point sits on its line; an experiment with nothing to show for that trace, or with another number of additions than the others, is left out and named in one warning when the figure is saved. With the difference spectrum, the plot stacks the difference spectra of the group from the top down, each lined up on its highest point inside the band of the haem picked, in the colour of the group and lighter for each later line; its y axis has no numbers, as each spectrum is only moved to sit clear of the others (MATHS.md section 9.2). A time point is named with how many experiments its mean is of ("2 h (n = 3)"). An experiment without a difference spectrum is left out, and named in one warning when the figure is saved; with none to show, one sentence in the cells says so.
- The form of a **Single trace** asks: the **Experiment**, in the same list; the **Trace**: O₂, OCR (to start with), each haem of the fit while the haems are worked out, and Δψ when the run works it out; **OCR shown as** % of baseline (to start with), As measured, Change from baseline or Per OD (only in a run with OD values); **Haems shown as** ΔD (to start with), Absorbance or % oxidised; **Δψ shown as** mV (to start with) or Change from baseline; **Time 0 at** The start of the recording or Addition 1 (to start with) to Addition 10; and the ticks **Labels of the additions** (ticked) and **Averaging regions shaded** (not ticked). **Haems shown as** is in the form only in a run that works out the haems, and **Δψ shown as** only in one that works out Δψ. Of the "shown as" lists, only the one that fits the trace picked is used. The plot is that one trace against time, counted from the addition picked (from its last addition when the file has fewer), in the colour it has in the earlier steps, with a dashed line at each addition. In place of a plot that cannot be drawn, one sentence says why: its experiment is not in this dataset, the file could not be read, or the file has nothing for the trace and value picked (a file without a baseline has no % of baseline).
- The form of a **Mean trace** asks: the same **Trace** and **shown as** lists; a list for each group column of the set-up that has labels (Split: each label on its own, Only one label, or All together; Group 1 starts split, the others together); the same **Time 0 at**; the **Band**: SEM (to start with), SD or None; and the tick **Labels of the additions** (ticked). The plot has one line per set, the mean of its experiments, named with how many they are ("control (n = 3)"), in the colour of its Group 1 label, with the band in a paler shade of that colour. The experiments are lined up on their additions, so each addition is at the same place for all of them; where the gap between two additions was longer in one experiment than in another, the spare middle of the longer gap is left out and the lines and the time axis have a break mark (//) there (MATHS.md section 10). With Time 0 at the start of the recording, each experiment keeps its own clock. An experiment with nothing to show for the trace and value picked, or with another number of additions than most of the others, is left out, and named in one warning when the figure is saved; with none to show, one sentence in the cells says so.
- The four plots of numbers per region (Bar chart, Before and after, Response by region, Time points) share this: the number of an experiment in a region is the mean of its trace over that averaging region, **Baseline** or **After addition 1** to **After addition 10**; **Regions**: Settled (to start with) or Quick, is in the form only in a run with both kinds of averaging region; every experiment is drawn as a dot (or a line) behind the mean of its set, always; **Bars**: SEM (to start with) or SD; **Test**: Student's t-test (to start with) or Welch's t-test, between each pair of sets; **Marks**: Stars (to start with), p values or None. Every p value is Holm-corrected across all the tests of its plot, and a mark is drawn over a bracket only where the corrected p is under 0.05, never "ns" (MATHS.md section 11). A set of one experiment has its dot, no bar and no test. Of the "shown as" lists, only the one that fits the measurement picked is used; an experiment with no number in the region is left out of its set.
- The form of a **Bar chart** asks: the **Measurement**: OCR (to start with), each haem of the fit while the haems are worked out, and Δψ when the run works it out; **OCR shown as** % of baseline (to start with), As measured, Change from baseline or Per OD (only in a run with OD values); **Haems shown as** and **Δψ shown as**, as in a Single trace; the **Region** (it starts at After addition 1); **Regions**; the list for each group column, as in a Mean trace; **Bars**; **Test**; **Marks**. The plot has one bar per set, the mean, in a light shade of the set's colour, with its SEM or SD and a dot per experiment on top, a bracket with its mark between two sets that differ, and the name of the region under the axis. With no number to show, one sentence in the cells says so.
- The form of a **Before and after** asks: the same **Measurement** and **shown as** lists (the OCR starts As measured: as % of baseline the baseline of every experiment is 100); **From** (it starts at Baseline) and **To** (After addition 1); **Regions**; the list for each group column; **Marks**. The plot has the sets side by side, each experiment a thin line from its first region to its second, and the mean of each set a thick line with diamonds; inside each set the two regions are compared with a paired t-test, on the experiments that have both numbers, and a bracket with its mark sits over a set whose regions differ. With no number in either region, one sentence in the cells says so.
- The form of a **Response by region** asks: the **Measurement**: OCR (to start with) or Haems (only in a run that works out the haems); a tick for each haem of the fit (**Haem: …**, all ticked), used when Haems is picked; **OCR shown as** and **Haems shown as**; **Regions**; the list for each group column; **Bars**; **Test**; **Marks**. The plot has every region along the bottom, Baseline then one per addition, named by the addition as it is written on the plot of the first experiment: at each region the sets sit side by side, each with the pale dots of its experiments, its mean and its bar, a line joining the means of a set, and a bracket with its mark between two sets that differ at that region. With Haems, each haem ticked is a row of its own with one legend under the last, and the correction runs across the tests of every row. An experiment with another number of additions than most of the plot is left out, and named in one warning when the figure is saved; another warning names the experiments whose additions are not the ones written under the regions. With no number in any region, one sentence in the cells says so.
- The form of a **Time points** asks what the form of a Bar chart asks, without the list of the time point, which is the bottom axis: one **Region** against the time point of each experiment in the set-up table. The plot has a line per set (by Group 1 and Group 2) through its means, with the dots, the bars and the brackets at each time point as in a Response by region. Time points that are all different numbers with the same unit, or none ("2 h", "24 h"), sit at their number, with the unit in the title of the axis; otherwise they are evenly spaced in the order of the table. An experiment without a time point is not drawn. With no experiment that has both a time point and a number, one sentence in the cells says so.
- A plot is drawn from the experiments as they were saved at Export, inside its cells: its numbers, axis titles and its own small legend never run into the cells of another plot, and the legend sits where it covers no line. A plot type that is not built yet is a grey box with its name. A **Space for a drawing** is empty: on screen it has a faint dashed outline and its name, and the saved figure has only its letter there. Each plot's **letter** is in bold at its top left: a, b, c… from left to right along a row of the grid, then the next row down, by the top left cell of each plot.
- **Under the page**, for the caption: what each colour (the Group 1 labels), line style (the Group 2 labels) and shade (the time points, from dark to light) on the page means, then one line for each Difference spectrum with its letter and the times of its two regions ("b: reduced, 12.0 to 14.0 min, minus oxidised, 2.0 to 4.0 min.") and one for each Mean trace ("c: each line is the mean of its experiments, the band ± SEM; lined up on addition 1."), and one for each plot of numbers per region with a number to show, written to be copied into the legend of the paper: what its dots and bars are, how many experiments each set has, which set has only one, and the test and the correction its marks come from ("d: Each dot is one experiment, and the bars are the mean ± SEM of each set (control n = 3, knockdown n = 3). The sets were compared with Student's t-test (two-tailed, unpaired), with the Holm correction across the 3 tests of the plot: * p < 0.05, ** p < 0.01, *** p < 0.001; a comparison without a mark gave p ≥ 0.05."); that of a Before and after says each line is one experiment and names the paired t-test, and that of a Time points starts with its region ("Region: after addition 1."). All with **Copy** to put them on the clipboard. While no plot on the page uses them, one line says so and Copy is greyed out.
- **✎** and **✕** sit in the top right corner of each plot. ✕ removes the plot. ✎ takes it off the page, with its old cells in grey dashes and free again, and opens its form: drag a new rectangle anywhere, its old cells included, to move it or change its size, or change its type; Done keeps it, Cancel puts it back as it was.
- **Save template** asks, on the left, for a name (**Save**, **Cancel**) and writes the page size and each plot's type, cells and choices in the `layouts` folder, so the layout can be loaded for any dataset. With a template of that name already there it asks first: **Replace it** or **Choose another name**. A page with no plot is not saved.
- **Load template** puts the template picked in the list beside it on the page. With plots already on the page it asks first: **Replace them** or **Cancel**. A journal or a width of the template that the `journals` folder does not have becomes Nature or 2 columns, and one line says so. A file that is not a template of Portimao, or one that still holds a Legend, is refused in one line, and the page stays as it was.
- Nothing here opens a window of its own.

| # | Question | Leads to |
|---|---|---|
| 6.2 | Drag across the grid to place each plot. When the page is ready, click Continue. (above it, in grey: "The page on the right is the journal page at its printed size, with a grid of 6 × 6 cells. Pick a plot type in the strip above it, then drag across the cells it should take; its form opens here." and "Load template puts a layout saved before on the page; Save template keeps this one for later.") One button, **Continue**. | **Continue**: a form still open is cancelled, the file arrows, the boxes and the plot come back. A page with at least one plot that has changed since it was last saved as a template or loaded from one → **6.3**; otherwise **9.1**. |
| 6.3 | Do you want to save this page as a template, to load it for another dataset? `(y/N)` | **Yes** → **6.4**. **No** → **9.1**. |
| 6.4 | What should the template be called? (an empty answer is refused: "Type a name for the template.") | A template of that name already there → **6.5**. Otherwise the template is written in the `layouts` folder, one line says so ("Saved the template … It is in the list beside Load template from now on."), then **9.1**. A template that cannot be written says why in one line, then **9.1**. |
| 6.5 | A template called *name* is already there. Do you want to replace it? `(y/N)` | **Yes**: it is written over, then **9.1**. **No** → **6.4** again. |

When the run starts, a page with at least one plot is saved in the results folder as `dataset_figure_<journal>.pdf`: the figure at exactly its printed size, drawn as lines and text with its fonts in the file, so the text can still be changed in a drawing program. A character the journal's font does not have (a subscript, a raised minus) is drawn in the next font that has it, as on the plot of one file. Its master page, `dataset_figure_master_<journal>.pdf`, is the same figure on one page of the journal, as **Export master** makes for one experiment. An empty page saves neither. A PDF that cannot be written (open in another program) is said in one sentence and the run goes on.

---

## 7. The fixed dataset figures (not asked)

These questions are not asked: the figure builder of section 6 takes the place of the four fixed figures, which are to come back as templates to load there. They are listed, with **old** before the numbers they had, because the program still holds them.

If nothing is plotted in section 5, a message says these figures reuse the panels chosen for the individual experiment plots and are skipped, and the next step is **old 7.1**.

The boxes are greyed out: these figures ask their own journal and size.

Each figure is drawn from your data once its questions are answered (this reads the files again, so it takes a moment, and the **Plotting data …** sign is on the plot meanwhile) and shown in the plot area. None of these figures is saved to the results folder until the run starts.

### 7.A Two experiments side by side

Old 6.1 is only asked when there are at least 2 files.

| # | Question | Yes → | No → |
|---|---|---|---|
| old 6.1 | Do you want to plot two experiments side by side? `(y/N)` | **old 6.1.1** | **old 6.3** |

| # | Question | Leads to |
|---|---|---|
| old 6.1.1 | Which experiment goes on the left? | **old 6.1.2** |
| old 6.1.2 | Which experiment goes on the right? | **old 6.1.3** |
| old 6.1.3 | Which journal format would you like? (then, for a journal, how wide and how tall, as in 5.7) | the figure is drawn **(plot)**, then **old 6.2** |

| # | Question | Yes → | No → |
|---|---|---|---|
| old 6.2 | Do you accept this figure? `(Y/n)` (above it: "Click No to change its settings.") | **old 6.3** | **old 6.1** |

If the figure cannot be previewed, a message says so and the figure is kept as it is.

### 7.B Four experiments in a 2x2 grid

Old 6.3 is only asked when there are at least 4 files.

| # | Question | Yes → | No → |
|---|---|---|---|
| old 6.3 | Do you want to plot four experiments in a 2x2 grid (knockdown and control, two addition orders)? `(y/N)` | **old 6.3.1** | **old 7.1** |

File names are read as `<strain>_<order>_run<N>`, for example `knockdown_kcn_then_bd_run1`. If no file name fits, the figure is skipped and the next step is **old 7.1**.

The figure starts at the baseline, so it needs the averaging regions of 4.6. With none set up, **4.6.1** is asked first (section 4.E); without them the figure is not made and the next step is **old 7.1**. With both kinds of averaging region set up, **4.6.2** then asks which kind the figure shows.

| # | Question | Leads to |
|---|---|---|
| old 6.3.1 | Which run number should be shown? | **old 6.3.2** |
| old 6.3.2 | Do you want the run name written faintly on each plot? `(Y/n)` | **old 6.3.3** |
| old 6.3.3 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then **old 6.4** |

| # | Question | Yes → | No → |
|---|---|---|---|
| old 6.4 | Do you accept this figure? `(Y/n)` (above it: "Click No to change its settings.") | **old 7.1** | **old 6.3** |

### 7.C The summary figures

As for the two figures above, the **Plotting data …** sign is on the plot while each picture is drawn. Both summary figures need the haem fit. If the haems were not decomposed in section 4 (or Haem decomposition was unticked), the fit is asked first, without a number of its own: *Which fit would you like to use?* (a numbered list of the presets of the haem library, then your own fit files in the `fits/` folder; the fit in the Haem decomposition box is the default), then, when the files have more than one spectrometer in common and the one saved is not among them, *Which spectrometer holds the haem spectra?*. Only the fit files are offered here, not the components found from the data. If the `fits/` folder holds no `.csv` file, or the fit cannot be used, a message says so and the figure is skipped. Both figures also average around the events, over the averaging regions of 4.6. With none set up, **4.6.1** is asked after the fit and before the figure's own questions (section 4.E); without them the figure is not made and the next figure is asked. With both kinds of averaging region set up, **4.6.2** then asks which kind the figure averages over; in the time response, the difference spectrum is the last region of that kind minus the one before it.

### 7.D Time response

| # | Question | Yes → | No → |
|---|---|---|---|
| old 7.1 | Do you want to plot a time response? `(y/N)` | **old 7.1.1** | **old 7.2** |

File names need a group word and the hours, for example `control_7hours`.

The figure is built up in the plot window: the drop-down lists the individual experiment plots (marked locked, final) and the time response being built. Panels not chosen yet are empty boxes ("Kinetic trace 1", "Decomposition 1" ...). After every choice below the figure is redrawn **(plot)** and an accept question is asked (shown in the second table).

| # | Question | Leads to |
|---|---|---|
| old 7.1.1 | What are the two group words, separated by a comma? | **old 7.1.2**. If there are not exactly two words, if either group has no file, or if fewer than two files have hours in their name, the time response is skipped and the next step is **old 7.2** |
| old 7.1.2 | Which time points (hours) should be skipped in the waterfall plots? Separate them with commas, or type none. | the waterfalls are drawn **(plot)**, then the accept question, then **old 7.1.3** |
| old 7.1.3 | Which experiment should the first kinetic trace show? | drawn **(plot)**, accept question, then **old 7.1.4** |
| old 7.1.4 | Which experiment should the second kinetic trace show? | drawn **(plot)**, accept question, then **old 7.1.5** |
| old 7.1.5 | Which experiment should decomposition plot 1 show? | drawn **(plot)**, accept question, then **old 7.1.6** |
| old 7.1.6 | Which experiment should decomposition plot 2 show? | drawn **(plot)**, accept question, then **old 7.1.7** |
| old 7.1.7 | Which experiment should decomposition plot 3 show? | drawn **(plot)**, accept question, then **old 7.1.8** |
| old 7.1.8 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then the final accept question |

Each is a yes or no question, `(Y/n)`, with what **n** does on the grey line above it.

| Question | Yes → | No → |
|---|---|---|
| Do you accept these waterfall plots? | the next question | **old 7.1.2** again ("Click No to choose the time points again.") |
| Do you accept this plot? (after each kinetic trace and decomposition plot) | the next question | the same choice again ("Click No to choose another experiment.") |
| Do you accept this figure? (final) | **old 7.2** | **old 7.1** ("Click No to change its settings.") |

### 7.E Haem and OCR response

| # | Question | Yes → | No → |
|---|---|---|---|
| old 7.2 | Do you want to plot a haem and OCR response? `(y/N)` | **old 7.2.1** | **9.1** |

File names need the strain, the addition order and the run number, for example `knockdown_kcn_then_bd_run1`. The files found are listed. If no file name fits, the figure is skipped and the next step is **9.1**.

The figure is built up in the plot window in stages. First only the baseline OCR and the OCR response are drawn, then all the haems are added, then they are redrawn with the haems and order you chose. Each stage has its own accept question (second table).

| # | Question | Leads to |
|---|---|---|
| old 7.2.1 | Which OCR would you like to use? 1) OCR (µM min⁻¹) 2) OCR / OD (µM min⁻¹ OD⁻¹), *only offered if you said yes to OD scaling in 3.1* 3) OCR (% of the range) (this figure has a % of baseline of its own) | the OCR plots are drawn **(plot)**, accept question, then **old 7.2.2** |
| old 7.2.2 | How would you like to show the haems? (the same options as Haems as in the View box, but % oxidised is offered only when every file of the figure has both regions, as the figure averages the files together) | **old 7.2.3** if you said yes to OD scaling in 3.1 and did not choose % oxidised, otherwise all the haems are drawn **(plot)**, accept question, then **old 7.2.4** |
| old 7.2.3 | Do you want to scale the haems by OD as well? `(Y/n)` | all the haems are drawn **(plot)**, accept question, then **old 7.2.4** |
| old 7.2.4 | Which haems should get a row, and in which order? | drawn **(plot)**, accept question, then **old 7.2.5** |
| old 7.2.5 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then the final accept question |

Each is a yes or no question, `(Y/n)`, with what **n** does on the grey line above it.

| Question | Yes → | No → |
|---|---|---|
| Do you accept the OCR plots? | **old 7.2.2** | **old 7.2.1** again ("Click No to choose the OCR again.") |
| Do you accept these haem plots? | **old 7.2.4** | **old 7.2.2** again ("Click No to choose how to show the haems again.") |
| Do you accept these haem rows? | **old 7.2.5** | **old 7.2.4** again ("Click No to choose the haems again.") |
| Do you accept this figure? (final) | **9.1** | **old 7.2** ("Click No to change its settings.") |

---

## 8. Dataset export

Nothing is asked here: the workbook of each experiment, and its spectra, are written in the experiment export (**5.9**). The number 8 is kept for the dataset workbook still to come.

---

## 9. Dataset export: summary

A summary of all your answers is printed (files, results folder, trimming, ignoring, decomposition, OD scaling, temperature, Δψ, averaging, plots, figure sizes, how many workbooks were written at 5.9, and the dataset figure when its page holds a plot).

| # | Question | Yes → | No → |
|---|---|---|---|
| 9.1 | Do you want to start? `(Y/n)` | Your answers are saved in the data folder (`portimao_settings.json`) for the next time this dataset is opened, and the run starts. If the data folder cannot be written to, a message says the dataset will start from the standard settings next time. Every file is processed again; a plot or workbook saved at 5.9 is not written again, and one not saved then is written now. | The program stops and nothing else is changed: data you exported with the export buttons of the trim step, and the plots and workbooks saved at 5.9, are kept, and the last line says so. |
