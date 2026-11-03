# Albufeira question flow (V2.8)

Every question in the order it is asked, with where each answer leads. The question text is the text on screen.

**How to read it**

- `(Y/n)` and `(y/N)` questions: the capital letter is what Enter gives. The letters shown are the first-run defaults; after a run, the answers you gave are offered instead. Press Enter on any question to use the value in `[brackets]`.
- **Yes → / No →** says which question comes next. **Next** means the next question in this list.
- The numbers here are for reference. On screen the numbers are given in the order the questions are asked, so when a branch is skipped the later numbers move up, and every "Do you accept...?" question takes a number of its own.
- Every "Do you accept...?" question has the same two answers. **1 (Yes, accept)** moves on. **2 (No, ...)** asks the questions of that step again, with your last answers as the defaults.
- The plot on the right is redrawn after each step marked **(plot)**. You can flick through the files with the arrows or the drop-down at any time while a question waits.

---

## 1. Your files

| # | Question | Answer leads to |
|---|---|---|
| 1.1 | What is the directory with the .paf files? | A folder that does not exist, or has no `.paf` files, is refused and the question is asked again. Otherwise every file is read and listed, then **1.2**. |
| 1.2 | To which directory would you like the results to be saved? | **2.1** |

---

## 2. Trimming and ignoring

TRIM = data that is not imported, plotted or used. IGNORE = data that is plotted but not used for calculations. Ignore times count from the new 0 after trimming. All four edges are asked in the same way, in this order: TRIM + START, TRIM + END, IGNORE + START, IGNORE + END. The plot shows the raw data first, and **after every answer in this section the shaded regions are added to the plot**: trimmed parts grey and hatched, ignored parts amber. An answer for ALL the data shades every file; an answer for one file shades just that file, and the plot switches to the file being asked about.

| # | Question | Yes → | No → |
|---|---|---|---|
| 2.1 | Do you want to TRIM the START of any of the data? `(y/N)` | **2.1.1** | **2.2** (nothing trimmed at the start) |
| 2.1.1 | How many minutes should be TRIMMED from the START of ALL the data? `[0]` Every file is shaded **(plot)**. | **2.1.2** | |
| 2.1.2 | Do you want to adjust this for any specific file? `(y/N)` | **2.1.3** | **2.2** (every file uses 2.1.1) |
| 2.1.3 | How many minutes should be TRIMMED from the START of *file*? Asked once for each file; the plot switches to that file and its shading is updated **(plot)**. | the next file, then **2.2** | |
| 2.2 | Do you want to TRIM the END of any of the data? `(y/N)` | **2.2.1** | **2.3** (nothing trimmed at the end) |
| 2.2.1 | How many minutes should be TRIMMED from the END of ALL the data? `[0]` Every file is shaded **(plot)**. | **2.2.2** | |
| 2.2.2 | Do you want to adjust this for any specific file? `(y/N)` | **2.2.3** | **2.3** (every file uses 2.2.1) |
| 2.2.3 | How many minutes should be TRIMMED from the END of *file*? Asked once for each file; the plot switches to that file and its shading is updated **(plot)**. | the next file, then **2.3** | |
| 2.3 | Do you want to IGNORE the START of any of the data? `(y/N)` | **2.3.1** | **2.4** (nothing ignored at the start) |
| 2.3.1 | How many minutes should be IGNORED from the START of ALL the data? `[5]` Every file is shaded **(plot)**. | **2.3.2** | |
| 2.3.2 | Do you want to adjust this for any specific file? `(y/N)` | **2.3.3** | **2.4** (every file uses 2.3.1) |
| 2.3.3 | How many minutes should be IGNORED from the START of *file*? Asked once for each file; the plot switches to that file and its shading is updated **(plot)**. | the next file, then **2.4** | |
| 2.4 | Do you want to IGNORE the END of any of the data? `(y/N)` | **2.4.1** | **2.5** (nothing ignored at the end) |
| 2.4.1 | How many minutes should be IGNORED from the END of ALL the data? `[0]` Every file is shaded **(plot)**. | **2.4.2** | |
| 2.4.2 | Do you want to adjust this for any specific file? `(y/N)` | **2.4.3** | **2.5** (every file uses 2.4.1) |
| 2.4.3 | How many minutes should be IGNORED from the END of *file*? Asked once for each file; the plot switches to that file and its shading is updated **(plot)**. | the next file, then **2.5** | |

The limits of every file are then listed and drawn **(plot)** one last time.

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 2.5 | Do you accept these limits? | **3.1** | **2.1** |

---

## 3. Analysis

Earlier OD and event values found in the files' workbooks are offered as defaults.

### 3.A Haem decomposition

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.1 | Do you want to decompose the haems? `(y/N)` | **3.1.1** | **3.3** (no haems anywhere in the run) |

If the `fits/` folder holds no `.csv` file, 3.1 is not asked, a message says so, and the run carries on as for No.

| # | Question | Leads to |
|---|---|---|
| 3.1.1 | Which fit would you like to use? (a numbered list of the fit files, and *Find the components from the data (principal component analysis)* last) | **3.1.2** if the files have more than one spectrometer in common and the default one is not among them, otherwise the decomposition is drawn **(plot)**, then **3.2**; the last choice leads to **3.1.1.1** (after 3.1.2 if that is needed) |
| 3.1.2 | Which spectrometer holds the haem spectra? | the decomposition is drawn **(plot)**, then **3.2** (or **3.1.1.1** when the components are being found) |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 3.2 | Do you accept this decomposition? | **3.3** | **3.1** (choose the fit again) |

#### 3.A.1 Components from the data (principal component analysis)

Asked when the last choice of 3.1.1 is taken. The numbers keep counting up when a question is asked again, and each component name is a question of its own, so the numbers on screen can be higher than these. The files are read for their spectra (trimmed, without the ignored parts; this can take a moment) and a table shows how much each principal component explains and the error left. The plot window gets a *PCA components* picture after the files **(plot)**. It goes when the decomposition is drawn.

| # | Question | Leads to |
|---|---|---|
| 3.1.1.1 | Where should the spectral window start (nm)? | **3.1.1.2** |
| 3.1.1.2 | Where should the spectral window end (nm)? | the table, then **3.1.1.3** (or this question again if the analysis cannot be run, for example the window is too narrow) |
| 3.1.1.3 | How many components should be used? (a whole number; the suggestion is the default) | **3.1.1.4** |
| 3.1.1.4 | Do you want to rotate the components so each is as peak-like as possible (varimax)? `(Y/n)` | the components are drawn **(plot)**, then **3.1.1.5** |

| # | Question | 1 → | 2 → | 3 → | 4 → |
|---|---|---|---|---|---|
| 3.1.1.5 | Do you accept these components? | **3.1.1.6** | **3.1.1.3** (the number of components) | **3.1.1.1** (the window) | **3.1.1** (choose a fit file instead) |

| # | Question | Leads to |
|---|---|---|
| 3.1.1.6 | Do you want to name the components? `(y/N)` | yes: one question for each component (a name that is empty, has a comma or is used twice is asked again), then **3.1.1.7**; no (PC1, PC2, ...): **3.1.1.7** |
| 3.1.1.7 | Do you want to save these components as a fit file in the fits folder? `(Y/n)` | yes: **3.1.1.8**; no: the decomposition is drawn **(plot)**, then **3.2** |
| 3.1.1.8 | What should the fit file be called (without .csv)? | if the name exists, it asks whether to replace it (no asks for a name again); then the decomposition is drawn **(plot)**, then **3.2** |

### 3.B OD values

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.3 | Do you want to scale by OD (divide by dilution factor x OD x volume)? `(y/N)` | **3.3.1** | **3.5** (no OD scaling anywhere in the run) |

| # | Question | Leads to |
|---|---|---|
| 3.3.1 | *(only when some files already have OD values stored)* The stored values are listed, then: Do you want to change any of these? `(y/N)` | **Yes**: all files are asked **3.3.2**. **No**: only the files without stored values are asked **3.3.2**. If every file has stored values and you say No, no OD questions are asked and the next step is **3.4**. |
| 3.3.2 | For each file in turn: What was the OD of the cells added? | **3.3.3** |
| 3.3.3 | What volume of cells (mL) were spun down and resuspended in 5 mL? | **3.3.4** |
| 3.3.4 | What is the dilution factor, if the cells were diluted mid run? `[1]` | the next file, then the values of every file are listed and **3.4** |

The data is **not** scaled by OD here. The values are only checked; the scaling is chosen in section 4.

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 3.4 | Do you accept these OD values? | **3.5** | **3.3** (asked again, then the OD values) |

### 3.C Averaging around the events

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.5 | Do you want to average around the events? `(y/N)` | **3.5.1** | **3.7** (no averaging in the run) |

| # | Question | Leads to |
|---|---|---|
| 3.5.1 | How long a window (minutes) should the average be taken over? | **3.5.2** |
| 3.5.2 | How long before the next addition should the averaging window end (minutes)? | the windows are drawn **(plot)**, then **3.6** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 3.6 | Do you accept these averaging windows? Windows that do not fit are skipped; they are drawn red with a warning sign and listed in red in the terminal first. | **3.7** | **3.5** |

### 3.D Event labels

If no file has any event, 3.7 and 3.8 are not asked and the next step is **3.9**.

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.7 | *(the runs and their event labels are listed, then)* Do you want to change any event labels? `(y/N)` | **3.8** | the labels are drawn **(plot)**, then **3.9** |

| # | Question | Leads to |
|---|---|---|
| 3.8 | Which run(s) do you want to change? (numbers from the list, separated by commas) | **3.8.1** for the first chosen run |
| 3.8.1 | For each event of the run: What was added at *time* min? Write 'ignore' to ignore this event. `[current label]` | If you write `ignore`, the next event. Otherwise **3.8.2**. |
| 3.8.2 | What was the final concentration in uM? `[unknown]` | the next event, then the next chosen run, then the labels are drawn **(plot)** and **3.9** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 3.9 | Do you accept these event labels? | **4.1** | **3.7** (change the labels again) |

---

## 4. Individual experiment plots

You now choose how the figure saved for each file will look. The plot is redrawn after each choice.

### 4.A Oxygen and OCR

| # | Question | Leads to |
|---|---|---|
| 4.1 | Do you want to plot the set and measured [O2] (CsO2 and CcO2)? `(Y/n)` | **4.2** |
| 4.2 | Do you want to plot the OCR? `(Y/n)` | **Yes**: **4.2.1**. **No**: if 4.1 was also No, nothing is drawn and the next step is **4.4**; otherwise the plot is drawn **(plot)** and **4.3**. |
| 4.2.1 | Which OCR would you like to plot? 1) OCR (µM min⁻¹) 2) OCR / OD (µM min⁻¹ OD⁻¹), *only offered if you said yes to OD scaling in 3.3*. 3) OCR (% of the range) | the plot is drawn **(plot)**, then **4.3** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 4.3 | Do you accept the oxygen and OCR plots? | **4.4** | **4.1** |

### 4.B Haems

4.4 is only asked if the haems were decomposed in 3.1. Otherwise go straight to **4.8**.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.4 | Do you want to plot the haems? `(y/N)` | **4.4.1** | **4.8** |

| # | Question | Leads to |
|---|---|---|
| 4.4.1 | Which haems would you like to plot, and in which order? (numbers separated by commas; Enter = all) | the haems are drawn **(plot)**, then **4.5** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 4.5 | Do you accept these haems and their order? | **4.6** | **4.4** |

| # | Question | Leads to |
|---|---|---|
| 4.6 | How would you like to plot the haems? Options: absorbance (mOD), ΔA (mOD) the change from the start, concentration, % oxidised | the plot is drawn **(plot)**, then **4.6.1** if you said yes to OD scaling in 3.3 and did not choose % oxidised, otherwise **4.7** |
| 4.6.1 | Do you want to scale the haems by OD as well? `(Y/n)` | the plot is drawn **(plot)**, then **4.7** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 4.7 | Do you accept this haem presentation? | **4.8** | **4.6** |

### 4.C Event labels

If nothing at all is plotted (4.1 No, 4.2 No, 4.4 No or skipped), a message says no individual figures will be made, 4.8 and 4.9 are skipped and the next step is **4.10**.

| # | Question | Leads to |
|---|---|---|
| 4.8 | At what angle should the event labels be plotted (0 = horizontal, 90 = vertical)? | the plot is drawn **(plot)**, then **4.9** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 4.9 | Do you accept the event labels? | **4.10** | **4.8** |

### 4.D Journal and size

| # | Question | Leads to |
|---|---|---|
| 4.10 | Which journal format would you like? 1) None (use the default: Nature, 1 column wide, 0.5 of a page tall) 2) Nature 3) Science 4) Cell 5) PNAS | **None**: the default size is used, then **4.11** (or **4.12** if nothing is plotted). **A journal**: **4.10.1** |
| 4.10.1 | How wide should the figure be? (the widths that journal allows) | **4.10.2** |
| 4.10.2 | How tall should the figure be, as a fraction of the page height (1 = a full page)? | the figure is drawn at its real size **(plot)**, then **4.11** (or **4.12** if nothing is plotted) |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 4.11 | Do you accept this figure? | **4.12** | **4.10** |

### 4.E Going back

| # | Question | Leads to |
|---|---|---|
| 4.12 | Do you want to go back to any of these steps? 1) No, continue 2) Trimming and ignoring 3) Analysis 4) Individual experiment plots | **1**: **5.1**. **2, 3 or 4**: that section's questions are asked again from its first question, with your answers as the defaults. Your answers to the later sections are kept. Then **4.12** is asked again. |

---

## 5. Multi-experiment plots

If nothing is plotted in section 4, a message says these figures reuse the section 4 choices and are skipped, and the next step is **6.1**.

Each figure is drawn from your data once its questions are answered (this reads the files again, so it takes a moment) and shown in the plot area. Nothing is saved to the results folder until the run starts.

### 5.A Two experiments side by side

5.1 is only asked when there are at least 2 files.

| # | Question | Yes → | No → |
|---|---|---|---|
| 5.1 | Do you want to plot two experiments side by side? `(y/N)` | **5.1.1** | **5.3** |

| # | Question | Leads to |
|---|---|---|
| 5.1.1 | Which experiment goes on the left? | **5.1.2** |
| 5.1.2 | Which experiment goes on the right? | **5.1.3** |
| 5.1.3 | Which journal format would you like? (then, for a journal, how wide and how tall, as in 4.10) | the figure is drawn **(plot)**, then **5.2** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 5.2 | Do you accept this figure? | **5.3** | **5.1** |

If the figure cannot be previewed, a message says so and the figure is kept as it is.

### 5.B Four experiments in a 2x2 grid

5.3 is only asked when there are at least 4 files.

| # | Question | Yes → | No → |
|---|---|---|---|
| 5.3 | Do you want to plot four experiments in a 2x2 grid (knockdown and control, two addition orders)? `(y/N)` | **5.3.1** | **6.1** |

File names are read as `<strain>_<order>_run<N>`, for example `knockdown_kcn_then_bd_run1`. If no file name fits, the figure is skipped and the next step is **6.1**.

| # | Question | Leads to |
|---|---|---|
| 5.3.1 | Which run number should be shown? | **5.3.2** if you said No to averaging in 3.5, otherwise **5.3.4** |
| 5.3.2 | *(a message says the figure starts at the baseline averaging window)* How long a window (minutes) should the average be taken over? | **5.3.3** |
| 5.3.3 | How long before the next addition should the averaging window end (minutes)? | **5.3.4** |
| 5.3.4 | Do you want the run name written faintly on each plot? `(Y/n)` | **5.3.5** |
| 5.3.5 | Which journal format would you like? (then width and height, as in 4.10) | the figure is drawn **(plot)**, then **5.4** |

| # | Question | 1 → | 2 → |
|---|---|---|---|
| 5.4 | Do you accept this figure? | **6.1** | **5.3** |

---

## 6. Experiment summaries

Both summary figures need the haem fit. If no fit was chosen in 3.1, the fit questions (**3.1.1**, and **3.1.2** if needed) are asked first. If there is no usable fit file the figure is skipped. Both figures also average around the events, so if you said No in 3.5 (and have not been asked since), the averaging window and gap questions (**3.5.1**, **3.5.2**) are asked first.

### 6.A Time response

| # | Question | Yes → | No → |
|---|---|---|---|
| 6.1 | Do you want to plot a time response? `(y/N)` | **6.1.1** | **6.2** |

File names need a group word and the hours, for example `control_7hours`.

The figure is built up in the plot window: the drop-down lists the individual experiment plots (marked locked, final) and the time response being built. Panels not chosen yet are empty boxes ("Kinetic trace 1", "Decomposition 1" ...). After every choice below the figure is redrawn **(plot)** and an accept question is asked (shown in the second table).

| # | Question | Leads to |
|---|---|---|
| 6.1.1 | What are the two group words, separated by a comma? | **6.1.2**. If there are not exactly two words, if either group has no file, or if fewer than two files have hours in their name, the time response is skipped and the next step is **6.2** |
| 6.1.2 | Which time points (hours) should be skipped in the waterfall plots? Separate them with commas, or type none. | the waterfalls are drawn **(plot)**, then the accept question, then **6.1.3** |
| 6.1.3 | Which experiment should the first kinetic trace show? | drawn **(plot)**, accept question, then **6.1.4** |
| 6.1.4 | Which experiment should the second kinetic trace show? | drawn **(plot)**, accept question, then **6.1.5** |
| 6.1.5 | Which experiment should decomposition plot 1 show? | drawn **(plot)**, accept question, then **6.1.6** |
| 6.1.6 | Which experiment should decomposition plot 2 show? | drawn **(plot)**, accept question, then **6.1.7** |
| 6.1.7 | Which experiment should decomposition plot 3 show? | drawn **(plot)**, accept question, then **6.1.8** |
| 6.1.8 | Which journal format would you like? (then width and height, as in 4.10) | the figure is drawn **(plot)**, then the final accept question |

| Question | 1 → | 2 → |
|---|---|---|
| Do you accept these waterfall plots? | the next question | **6.1.2** again |
| Do you accept this plot? (after each kinetic trace and decomposition plot) | the next question | the same choice again |
| Do you accept this figure? (final) | **6.2** | **6.1** |

### 6.B Haem and OCR response

| # | Question | Yes → | No → |
|---|---|---|---|
| 6.2 | Do you want to plot a haem and OCR response? `(y/N)` | **6.2.1** | **7.1** |

File names need the strain, the addition order and the run number, for example `knockdown_kcn_then_bd_run1`. The files found are listed. If no file name fits, the figure is skipped and the next step is **7.1**.

The figure is built up in the plot window in stages. First only the baseline OCR and the OCR response are drawn, then all the haems are added, then they are redrawn with the haems and order you chose. Each stage has its own accept question (second table).

| # | Question | Leads to |
|---|---|---|
| 6.2.1 | Which OCR would you like to use? (the same options as 4.2.1) | the OCR plots are drawn **(plot)**, accept question, then **6.2.2** |
| 6.2.2 | How would you like to show the haems? (the same options as 4.6) | **6.2.3** if you said yes to OD scaling in 3.3 and did not choose % oxidised, otherwise all the haems are drawn **(plot)**, accept question, then **6.2.4** |
| 6.2.3 | Do you want to scale the haems by OD as well? `(Y/n)` | all the haems are drawn **(plot)**, accept question, then **6.2.4** |
| 6.2.4 | Which haems should get a row, and in which order? | drawn **(plot)**, accept question, then **6.2.5** |
| 6.2.5 | Which journal format would you like? (then width and height, as in 4.10) | the figure is drawn **(plot)**, then the final accept question |

| Question | 1 → | 2 → |
|---|---|---|
| Do you accept the OCR plots? | **6.2.2** | **6.2.1** again |
| Do you accept these haem plots? | **6.2.4** | **6.2.2** again |
| Do you accept these haem rows? | **6.2.5** | **6.2.4** again |
| Do you accept this figure? (final) | **7.1** | **6.2** |

---

## 7. Data export

Every experiment always gets a workbook with CcO2, CsO2, VoO2, the events and your OD, volume and dilution entries.

| # | Question | Leads to |
|---|---|---|
| 7.1 | Do you want to put every processed table in the workbook (OD-scaled, haems, percent, ...)? `(y/N)` | **7.2** |
| 7.2 | Do you want to export the spectra as csv files (large, and it takes a while)? `(y/N)` | **8** |

---

## 8. Summary

A summary of all your answers is printed (files, results folder, trimming, ignoring, decomposition, OD scaling, averaging, plots, figure sizes, workbooks).

| # | Question | Yes → | No → |
|---|---|---|---|
| 8.1 | Do you want to start? `(Y/n)` | Your answers are remembered for next time and the run starts. Every file is processed, plotted and exported, then the multi-experiment figures and summaries are made. | The program stops and nothing is changed. |

---

## If the window cannot open (terminal mode)

The questions and their order are the same. These differ:

- In **2** and **3** the picture of the current file is saved to `Albufeira_preview.png` and opened in your picture viewer.
- Before **2.1** a small menu steps through the files: "What would you like to do?" 1) Next file 2) Previous file 3) Go to a specific file 4) Continue to trimming and ignoring.
- Every "Do you accept...?" question has a third answer, **3) Look at another file in the plot window first**, which asks "Which file would you like to look at?" and redraws the picture, then asks the accept question again.
