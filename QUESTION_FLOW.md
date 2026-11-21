# Portimao question flow (V2.4)

Every question in the order it is asked, with where each answer leads. The question text is the text on screen.

**How to read it**

- The questions are asked in Portimao's window. If the window cannot open, nothing is asked: a message says why and what to do (in the Mac app, with a **Copy details** button to send the details with the Mac problem form).
- `(Y/n)` and `(y/N)` questions: the capital letter is what Enter gives. The letters shown are the standard settings, offered for a dataset you have never run. Once you have started a run, your answers are saved in a small file inside the data folder (`portimao_settings.json`), and that dataset offers them instead, on this computer or on another one the folder is copied to. Press Enter on any question to use the value in `[brackets]`.
- **Yes → / No →** says which question comes next. **Next** means the next question in this list.
- The numbers here are for reference. On screen the numbers are given in the order the questions are asked, so when a branch is skipped the later numbers move up, and every "Do you accept...?" question takes a number of its own.
- Every "Do you accept...?" question starts with **1 (Yes, accept)**, which moves on. Its other answers (**2 (No, ...)**, and **3**, **4** ... where there are more) each say what is asked again, with your last answers as the defaults.
- The plot on the right is redrawn after each step marked **(plot)**. You can flick through the files with the arrows or the drop-down at any time while a question waits. The file shown and the one on each side of it are redrawn at once; any other file is drawn when you go to it, with its last plot under the **Drawing ...** sign meanwhile. From section 6 on, a file you did not look at after your last change says it was not drawn with your final settings.
- The **strip** under the plot shows what the run uses: **Haems** (ticked when the haems are worked out and shown), the **Fit**, the **Journal**, the **Width** and the **Height** of the figure of each file.
    - While your files are on the plot (sections 2 to 5), you can change it whenever a question waits. The plot is redrawn at once, the run uses the change, and the question goes on waiting.
    - Unticking Haems leaves the haems out of the run. Ticking it, or picking a fit, works them out with the fit shown and ticks the box.
    - If a fit cannot be used, one line says why and the strip goes back to what it showed.
    - A new journal, width or height redraws the plot only in section 5, the one plot drawn at the figure's size. Before that the change is kept for section 5.
    - The strip is greyed out while you choose the folder, during the questions of 4.A.1, and from section 6 on.
    - In section 2 the strip has one more row, above the others: the times of the trimmed and ignored edges of the file shown, and **Every file** (see section 2).
- While the program draws a picture of its own (the components found from the data, the figures of sections 6 and 7), a yellow **Drawing ...** sign is on the plot. It goes when the picture is shown or the next question is asked.
- Sections **1** to **3** are the import: your files, the parts of them that are used, and what is known about each run (the OD values and the labels). The processing starts with section **4**.

---

## 1. Your files

| # | Question | Answer leads to |
|---|---|---|
| 1.1 | What is the directory with the .paf files? | The folders in the program folder (in the Mac app, in the Portimao folder in your home folder) that hold `.paf` files are listed first, numbered, with how many files each holds. Answer with a number or a name from that list, or type (or drag in) the path of another folder; Enter gives the folder used last time. An empty answer, a folder that does not exist, or one with no `.paf` files, is refused and the question is asked again. Otherwise every file is read and listed, then **1.2**. |
| 1.2 | To which directory would you like the results to be saved? `[the export folder inside the data folder]` If the dataset was run before, a message says its saved settings are offered as the defaults, and its last results folder is offered here. | the standard plot is drawn **(plot)**, then **2.1** |

The standard plot of every file is then drawn with no question asked: the set and measured oxygen, the OCR and the haems (as the change from the start), with the event labels as written in the file. The haems are worked out with the standard fit (`bswitch_no2_mycobl_b557.csv`), or with the fit last saved for the dataset. If that fit file is not in the `fits/` folder or cannot be read, or the files do not share the spectrometer it is used on, a message says the haems are not shown yet, and only the oxygen and the OCR are drawn. A dataset last saved without haems is drawn without them, and its strip offers the standard fit. The strip then becomes usable: Haems is ticked when the haems are shown.

---

## 2. Trimming and ignoring

TRIM = data that is not imported, plotted or used. IGNORE = data that is plotted but not used for calculations. The plot shows the standard plot of the whole recording of each file (with the haems, when they are shown; the strip turns them on and off and picks their fit), with four edges on it: the trimmed start and end in grey (the parts trimmed away grey and hatched) and the ignored start and end in amber (the parts ignored amber). Each edge has a handle above the plot with its minutes beside it, the trimmed ones in the top row and the ignored ones just under them. Moving an edge never draws the plot again.

- **Drag** an edge by its handle or by its line; over an edge the mouse becomes a two-way arrow. The shading follows at once, and the edge moves in steps of 0.1 min. A trimmed edge stops at the first or the last event, so no addition is cut away, and the ignored parts stay inside the kept part without crossing. Where two edges meet, the line takes the ignored one; the trimmed one is still taken by its handle.
- **Type** the minutes in the row of the strip under the plot: **Trim start** and **end** (from the start and the end of the recording), **Ignore first** and **last** (from the trimmed edges). Press Enter or leave the box. A number that cannot be used turns the box red, with what to type beside it; a number beyond a limit is kept at the limit.
- **Every file**, ticked when the step opens: an edge moved or typed on the file shown moves on every file, to the same minutes from its own start or end, within that file's limits. Unticked, only the file shown changes. A file whose times differ from most files is marked **(own times)** in the drop-down.
- The edges start where they were left the last time the dataset was run; for a dataset never run, the first 5 minutes are ignored and nothing else. When this step is opened again (**4.3**, or going back at **5.8**), the limits it had are drawn as red dashed lines, so you can see how far you moved them.

| # | Question | Leads to |
|---|---|---|
| 2.1 | Drag the edges on the plot: grey for the trimmed parts, amber for the ignored parts, or type the times in the strip under the plot. With "Every file" ticked, a change applies to every file; untick it to change only the file shown. Press Enter when every file looks right. | Enter with the answer box empty: the limits of every file are listed, the plot shows the data they keep **(plot)**, then **2.2**. Anything typed in the answer box instead gets one line saying to type the times in the strip, and 2.1 goes on waiting. |

| # | Question | Yes → | No → |
|---|---|---|---|
| 2.2 | Do you want to export all the data now, cut to these limits, so you can plot it yourself? `(y/N)` | **2.2.1** | **3.1** |
| 2.2.1 | Do you want to include the spectra as csv files (large, and it takes a while)? `(y/N)` | the data is exported to `<results>/all_data/<file>/` (a workbook per file with every sheet, plus the spectra csv files if chosen), then **3.1** | |

The export is not scaled by OD, decomposed or averaged; event labels are the ones in the files, and the ignored parts are included.

---

## 3. OD values and event labels

The last part of the import: what is known about each run. Earlier OD and event values found in the files' workbooks are offered as defaults. The plot is the standard plot, cut to the limits of section 2.

### 3.A OD values

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.1 | Do you want to scale by OD (divide by dilution factor x OD x volume)? `(y/N)` | **3.1.1** | **3.2** (no OD scaling anywhere in the run) |

A table opens under the terminal text, above the answer box, with one row per file and a column each for the OD, the volume (mL) and the dilution factor. The values stored for a file are filled in, and the dilution factor is 1 when none is stored. Click a cell and type; Tab moves across and Enter moves down.

| # | Question | Leads to |
|---|---|---|
| 3.1.1 | Fill in the table under this text for each file: the OD of the cells added, the volume of cells (mL) spun down and resuspended in 5 mL, and the dilution factor if the cells were diluted mid run. Then press Enter here. | If a cell is empty or not a number above 0, those cells are named and the question is asked again (with the next number). Otherwise the table closes, the values of every file are listed and the next step is **3.2**. |

The data is **not** scaled by OD here. The values are only checked; the scaling is chosen in section 5.

### 3.B Event labels

If no file has any event, 3.2 to 3.4 are not asked and the next step is **3.5**.

"Current runs with events are:" and the runs with their event labels are listed first. A label whose units could be written more tidily is offered in its tidy form: `u` in front of a unit as µ (`100 uM` as 100 µM), a litre as a capital L, a space between a number and its unit, and `-1` after a unit or anything after `^` raised (`8ug ml-1` as 8 µg mL⁻¹). Only units are changed: a name with numbers in it (`nd-011992`) and a formula (`H2O2`) are left as they are. The **Symbols** row under the answer box types µ, ⁻¹, ₂ and the like by hand.

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.2 | *(only when a label in the list could be tidier; those labels are listed as "label -> tidy form", then)* Do you want to use these tidy forms? `(Y/n)` | every listed label is replaced by its tidy form, then **3.3** | the labels stay as they are (each is offered its tidy form again if you go through it in 3.4.1), then **3.3** |
| 3.3 | Do you want to change any event labels? `(y/N)` | **3.4** | the labels are drawn **(plot)**, then **3.5** |

| # | Question | Leads to |
|---|---|---|
| 3.4 | Which run(s) do you want to change? (numbers from the list, separated by commas) | **3.4.1** for the first chosen run |
| 3.4.1 | For each event of the run: What was added at *time* min? Write 'ignore' to ignore this event. `[current label]` | If you write `ignore`, the next event. If the label, typed or kept with Enter, could be tidier, **3.4.2**. Otherwise **3.4.3**. |
| 3.4.2 | Do you want to write this as '*tidy form*'? `(Y/n)` | **Yes**: the tidy form is used. **No**: the label stays as it is. Then **3.4.3**. |
| 3.4.3 | What was the final concentration in uM? `[unknown]` | the next event, then the next chosen run, then the labels are drawn **(plot)** and **3.5** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 3.5 | Do you accept these event labels? | **4.1** | **3.4** (change the labels again: the runs are listed again and 3.2 and 3.3 are not asked) |

---

## 4. Processing

The plot is the standard plot, cut to the limits of section 2, with the event labels of section 3. It is redrawn after each step marked **(plot)**.

### 4.A Haem fit

The haems on the plot are those of the import, worked out with the standard fit, the fit last saved for the dataset, or the fit you picked in the strip. A message names that fit ("The haems are worked out with *fit*."). The section then starts at **4.2**. 4.1 is asked only when the plot shows no haems yet:
- the dataset was last saved without them;
- the fit could not be used (a message in section 1 said why);
- you unticked Haems in the strip.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.1 | *(only when no haems are shown)* Do you want to decompose the haems? `(Y/n)`, or `(y/N)` when Haems was unticked in the strip or the dataset was saved without haems | **4.1.1** | **4.4** (no haems, unless you tick Haems in the strip later) |

If the `fits/` folder holds no `.csv` file, 4.1 is still asked, and 4.1.1 then offers only *Find the components from the data*.

| # | Question | Leads to |
|---|---|---|
| 4.1.1 | Which fit would you like to use? (a numbered list of the fit files, and *Find the components from the data (principal component analysis)* last; the fit in the strip is the default) | **4.1.2** if the files have more than one spectrometer in common and the default one is not among them, otherwise the decomposition is drawn **(plot)**, then **4.2**; the last choice leads to **4.1.1.1** (after 4.1.2 if that is needed). If the fit file cannot be read, a message says so and the haems are not decomposed: **4.4**. |
| 4.1.2 | Which spectrometer holds the haem spectra? | the decomposition is drawn **(plot)**, then **4.2** (or **4.1.1.1** when the components are being found) |

To try another fit, pick it in the strip while 4.2 waits: the plot is redrawn with it. To leave the haems out, untick Haems in the strip; answering 1 then goes on without haems, to **4.4**.

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 4.2 | Do you accept this decomposition? | **4.3** (**4.4** when Haems was unticked) | **4.1.1.1** (*No, find the components from the data*: the questions of 4.A.1, then 4.2 again with the components) |

#### 4.A.1 Components from the data (principal component analysis)

Asked when the last choice of 4.1.1, or answer 2 of 4.2, is taken. The strip is greyed out until they are answered, and its fit list then includes a fit file saved in 4.1.1.9. The numbers keep counting up when a question is asked again, and each component name is a question of its own, so the numbers on screen can be higher than these. The files are read for their spectra (trimmed, without the ignored parts; this can take a moment). Once the components are made, the plot window gets a *PCA components* picture (one panel per component, coloured by the haem type it looks like) and a *PCA examples* picture (the best and worst described spectrum and their residuals) after the files **(plot)**. The **Drawing ...** sign is on the plot while they are made. They go when the decomposition is drawn.

| # | Question | Leads to |
|---|---|---|
| 4.1.1.1 | Where should the spectral window start (nm)? | **4.1.1.2** |
| 4.1.1.2 | Where should the spectral window end (nm)? | **4.1.1.3** (or this question again if the analysis cannot be run, for example the window is too narrow) |
| 4.1.1.3 | How many components should be found? (The data suggest *N*; use as few as describe the data, extra ones only fit noise.) | a whole number; the number used last time, or else the suggestion, is the default; then **4.1.1.4** |
| 4.1.1.4 | Do you want to rotate the components so each is as peak-like as possible (varimax)? `(Y/n)` | **4.1.1.5** |
| 4.1.1.5 | Over how many nm should the components be smoothed to remove their noise (0 for none)? (default 4, or the width used last time; at most a quarter of the window) | the components and the examples are drawn **(plot)**, with one line per component (type, peak, share of the change) and the residual, then **4.1.1.6** |

| # | Question | 1 → | 2 → | 3 → | 4 → |
|---|---|---|---|---|---|
| 4.1.1.6 | Do you accept these components? | **4.1.1.7** | **4.1.1.3** (the number of components) | **4.1.1.1** (the window) | *No, choose a fit file instead*: **4.1.1**, or **4.2** when you came from 4.2 (pick the fit in the strip) |

| # | Question | Leads to |
|---|---|---|
| 4.1.1.7 | Do you want to name the components? `(y/N)` | yes: one question for each component, "What is component *N* (*type*, largest peak at *X* nm) called?", suggesting a name from its type such as *a-like* (a name that is empty, has a comma or is used twice is asked again), then **4.1.1.8**; no (PC1, PC2, ...): **4.1.1.8** |
| 4.1.1.8 | Do you want to save these components as a fit file in the fits folder? `(Y/n)` | yes: **4.1.1.9**; no: the decomposition is drawn **(plot)**, then **4.2** |
| 4.1.1.9 | What should the fit file be called (without .csv)? | if a fit file of that name exists, it asks "*name*.csv already exists. Do you want to replace it?" `(y/N)` (no asks for a name again); then the decomposition is drawn **(plot)**, then **4.2** |

### 4.B Trim and ignore times again

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.3 | *(only when the haems are decomposed)* Do you want to change the trim and ignore times now that the haems are shown? `(y/N)` | section 2 (**2.1** to **2.2.1**, the offer to export all the data included) is asked again, numbered on from here, with the edges where you left them, your limits as red dashed lines and the haems of the chosen fit on the plot; then the plot is redrawn **(plot)** and **4.4** | **4.4** |

### 4.C Averaging around the events

The windows are placed around the events as they were left in 3.B: an event marked `ignore` gets none. Each window ends a set time before the next addition (the last one 0.5 min before the end of the recording), so it moves with that addition in every file and one setting fits the whole dataset. The window and the gap are given in seconds.

You can set both with the mouse: while 4.4.1 waits, drag across one window on the plot of any file, just before an addition. A band follows the mouse, with its length above it. When you let go, the length goes into the answer box and the gap is offered in 4.4.2, both rounded to whole 5 s, so you can tidy them (to exactly 30 s, say) before pressing Enter.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.4 | Do you want to average around the events? `(y/N)` | **4.4.1** | **5.1** (no averaging in the run) |

| # | Question | Leads to |
|---|---|---|
| 4.4.1 | How long a window (s) should the average be taken over? `[120]` | **4.4.2** |
| 4.4.2 | How long before the next addition should the averaging window end (s)? `[30]`, or, after a drag in 4.4.1, the time from where you let go to the next addition (no default from a drag after the last addition). A drag here gives the gap alone. | the windows are drawn **(plot)**, then **4.5** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 4.5 | Do you accept these averaging windows? Windows that do not fit are skipped; they are drawn red with a warning sign and listed in red in the terminal first. | **5.1** | **4.4** |

---

## 5. Individual experiment plots

The figure saved for each file is drawn at once **(plot)**, at its real size and as it will be saved, with the standard settings or, for a dataset run before, the settings last saved for it. You change only what you want different. The standard figure has:

- the set and measured oxygen;
- the OCR per OD (µM min⁻¹ OD⁻¹) if you said yes to OD scaling in 3.1, otherwise the OCR in µM min⁻¹;
- when the haems were decomposed in 4.A, every haem of the fit as ΔA, the change from the start (scaled by OD as well if you said yes in 3.1);
- the event labels at 45°;
- Nature, 1 column wide and 0.5 of a page tall.

The haems are in the figure when Haems is ticked in the strip. The journal, width and height are set in the strip too: each change redraws the figure at once.

| # | Question | Leads to |
|---|---|---|
| 5.1 | Do you accept this figure? | **1) Yes, accept**: **5.8**. **2) No, change the oxygen and OCR**: **5.2**. **3) No, change which haems are shown** *(only when the haems are plotted)*: **5.4.1**. **4) No, change how the haems are shown** *(only when the haems are plotted)*: **5.5**. **5) No, change the angle of the event labels** *(only when something is plotted)*: **5.6**. |

Each part's questions offer your current choices as the defaults. After them the figure is drawn again **(plot)** and **5.1** is asked again; the numbers on screen keep counting up. If nothing is plotted (5.2 and 5.3 No, and Haems unticked), a message says no individual figures will be made, nothing is drawn, and 5.1 is asked again so you can turn a panel back on; accepting then makes no individual figures.

### 5.A Oxygen and OCR

| # | Question | Leads to |
|---|---|---|
| 5.2 | Do you want to plot the set and measured [O2] (CsO2 and CcO2)? `(Y/n)` | **5.3** |
| 5.3 | Do you want to plot the OCR? `(Y/n)` | **Yes**: **5.3.1**. **No**: the figure is drawn **(plot)**, then **5.1**. |
| 5.3.1 | Which OCR would you like to plot? 1) OCR (µM min⁻¹) 2) OCR / OD (µM min⁻¹ OD⁻¹), *only offered if you said yes to OD scaling in 3.1*. 3) OCR (% of the range) | the figure is drawn **(plot)**, then **5.1** |

### 5.B Which haems

Whether the haems are plotted at all is the Haems box in the strip; this question picks which of them, and their order.

| # | Question | Leads to |
|---|---|---|
| 5.4.1 | Which haems would you like to plot, and in which order? (numbers separated by commas; Enter = the haems shown) | the figure is drawn **(plot)**, then **5.1** |

### 5.C How the haems are shown

| # | Question | Leads to |
|---|---|---|
| 5.5 | How would you like to plot the haems? Options: absorbance (mOD), ΔA (mOD) the change from the start, concentration, % oxidised | **5.5.1** if you said yes to OD scaling in 3.1 and did not choose % oxidised, otherwise the figure is drawn **(plot)**, then **5.1** |
| 5.5.1 | Do you want to scale the haems by OD as well? `(Y/n)` | the figure is drawn **(plot)**, then **5.1** |

### 5.D Event labels

| # | Question | Leads to |
|---|---|---|
| 5.6 | At what angle should the event labels be plotted (0 = horizontal, 90 = vertical)? `[45]` | the figure is drawn **(plot)**, then **5.1** |

### 5.E Journal and size

The strip sets the journal, width and height of this figure, so these questions are not asked here. They are listed because the figures of sections 6 and 7 ask their own size with them, each with its own default size; each of those sections says what comes next.

| # | Question | Leads to |
|---|---|---|
| 5.7 | Which journal format would you like? 1) None (use the default: Nature, *the figure's default width and height*) 2) Nature 3) Science 4) Cell 5) PNAS | **None**: the default size is used. **A journal**: **5.7.1** |
| 5.7.1 | How wide should the figure be? (the widths that journal allows) | **5.7.2** |
| 5.7.2 | How tall should the figure be, as a fraction of the page height (1 = a full page = *X* mm)? | the figure is drawn at its real size **(plot)** |

### 5.F Going back

| # | Question | Leads to |
|---|---|---|
| 5.8 | Do you want to go back to any of these steps? 1) No, continue 2) Trimming and ignoring 3) OD values and event labels 4) Processing 5) Individual experiment plots | **1**: **6.1**. **2, 3, 4 or 5**: that section's questions are asked again from its first question, with your answers as the defaults. Your answers to the later sections are kept. Then **5.8** is asked again. |

---

## 6. Multi-experiment plots

If nothing is plotted in section 5, a message says these figures reuse the panels chosen for the individual experiment plots and are skipped, and the next step is **7.1**.

From here on the strip is greyed out: these figures ask their own journal and size.

Each figure is drawn from your data once its questions are answered (this reads the files again, so it takes a moment, and the **Drawing ...** sign is on the plot meanwhile) and shown in the plot area. Nothing is saved to the results folder until the run starts.

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

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 6.2 | Do you accept this figure? | **6.3** | **6.1** |

If the figure cannot be previewed, a message says so and the figure is kept as it is.

### 6.B Four experiments in a 2x2 grid

6.3 is only asked when there are at least 4 files.

| # | Question | Yes → | No → |
|---|---|---|---|
| 6.3 | Do you want to plot four experiments in a 2x2 grid (knockdown and control, two addition orders)? `(y/N)` | **6.3.1** | **7.1** |

File names are read as `<strain>_<order>_run<N>`, for example `knockdown_kcn_then_bd_run1`. If no file name fits, the figure is skipped and the next step is **7.1**.

| # | Question | Leads to |
|---|---|---|
| 6.3.1 | Which run number should be shown? | **6.3.2** if you said No to averaging in 4.4, otherwise **6.3.4** |
| 6.3.2 | *(a message says the figure starts at the baseline averaging window, so the events are averaged as in the processing)* How long a window (s) should the average be taken over? `[120]` (typed; the plot shows figures here, so there is nothing to drag across) | **6.3.3** |
| 6.3.3 | How long before the next addition should the averaging window end (s)? `[30]` | **6.3.4** |
| 6.3.4 | Do you want the run name written faintly on each plot? `(Y/n)` | **6.3.5** |
| 6.3.5 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then **6.4** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 6.4 | Do you accept this figure? | **7.1** | **6.3** |

---

## 7. Experiment summaries

As in section 6, the **Drawing ...** sign is on the plot while each picture is drawn. Both summary figures need the haem fit. If the haems were not decomposed in section 4 (or Haems was unticked), the fit questions (**4.1.1**, and **4.1.2** if needed) are asked first; only the fit files are offered here, not the components found from the data. If the `fits/` folder holds no `.csv` file, or the fit cannot be used, a message says so and the figure is skipped. Both figures also average around the events, so if you said No in 4.4 (and have not been asked since), a message says the averaging window is asked here, and the window and gap questions (**4.4.1**, **4.4.2**) are asked first.

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

| Question | 1 → | 2 → |
|---|---|---|
| Do you accept these waterfall plots? | the next question | **7.1.2** again |
| Do you accept this plot? (after each kinetic trace and decomposition plot) | the next question | the same choice again |
| Do you accept this figure? (final) | **7.2** | **7.1** |

### 7.B Haem and OCR response

| # | Question | Yes → | No → |
|---|---|---|---|
| 7.2 | Do you want to plot a haem and OCR response? `(y/N)` | **7.2.1** | **8.1** |

File names need the strain, the addition order and the run number, for example `knockdown_kcn_then_bd_run1`. The files found are listed. If no file name fits, the figure is skipped and the next step is **8.1**.

The figure is built up in the plot window in stages. First only the baseline OCR and the OCR response are drawn, then all the haems are added, then they are redrawn with the haems and order you chose. Each stage has its own accept question (second table).

| # | Question | Leads to |
|---|---|---|
| 7.2.1 | Which OCR would you like to use? (the same options as 5.3.1) | the OCR plots are drawn **(plot)**, accept question, then **7.2.2** |
| 7.2.2 | How would you like to show the haems? (the same options as 5.5) | **7.2.3** if you said yes to OD scaling in 3.1 and did not choose % oxidised, otherwise all the haems are drawn **(plot)**, accept question, then **7.2.4** |
| 7.2.3 | Do you want to scale the haems by OD as well? `(Y/n)` | all the haems are drawn **(plot)**, accept question, then **7.2.4** |
| 7.2.4 | Which haems should get a row, and in which order? | drawn **(plot)**, accept question, then **7.2.5** |
| 7.2.5 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then the final accept question |

| Question | 1 → | 2 → |
|---|---|---|
| Do you accept the OCR plots? | **7.2.2** | **7.2.1** again |
| Do you accept these haem plots? | **7.2.4** | **7.2.2** again |
| Do you accept these haem rows? | **7.2.5** | **7.2.4** again |
| Do you accept this figure? (final) | **8.1** | **7.2** |

---

## 8. Data export

Every experiment always gets a workbook with CcO2, CsO2, VoO2, the events and your OD, volume and dilution entries.

| # | Question | Leads to |
|---|---|---|
| 8.1 | Do you want to put every processed table in the workbook (OD-scaled, haems, percent, ...)? `(y/N)` | **8.2** |
| 8.2 | Do you want to export the spectra as csv files (large, and it takes a while)? `(y/N)` | **9** |

---

## 9. Summary

A summary of all your answers is printed (files, results folder, trimming, ignoring, decomposition, OD scaling, averaging, plots, figure sizes, workbooks).

| # | Question | Yes → | No → |
|---|---|---|---|
| 9.1 | Do you want to start? `(Y/n)` | Your answers are saved in the data folder (`portimao_settings.json`) for the next time this dataset is opened, and the run starts. If the data folder cannot be written to, a message says the dataset will start from the standard settings next time. Every file is processed, plotted and exported, then the multi-experiment figures and summaries are made. | The program stops and nothing is changed. |
