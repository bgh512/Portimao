# Portimao question flow (V2.17)

Every question in the order it is asked, with where each answer leads. The question text is the text on screen.

**How to read it**

- The questions are asked in Portimao's window. If the window cannot open, nothing is asked: a message says why and what to do (in the Mac app, with a **Copy details** button to send the details with the Mac problem form).
- Each question is one line in pink. Explanations and messages are in a quieter grey above it.
- The end of each question says what Enter gives, brighter than the rest:
    - `(Y/n)` and `(y/N)` on a yes or no question: the capital letter is what Enter gives. y, yes, n and no are taken in any capitals.
    - On a numbered list, the numbers you can type: every one up to five, `(1/2/3)`, the one Enter gives brighter; a range beyond, `(1–7)`, the option Enter gives brighter in the list. A question answered by several numbers says on the grey line above it to separate them with commas, and the options Enter gives are brighter in the list.
    - `[value]` on everything else, and `[skip]` when Enter leaves the answer empty. A unit is written once, in brackets after the quantity, in another colour: (s), (nm), (µM).
- The defaults shown here are the standard settings, offered for a dataset you have never run. Once you have started a run, your answers, your OD values and event labels among them, are saved in a small file inside the data folder (`portimao_settings.json`), and that dataset offers them instead, on this computer or on another one the folder is copied to.
- After an answer that cannot be used, one line in red says what to type, and the question waits for the next answer.
- Some answers are typed in a table, which opens on the terminal side under the last few lines of text: one row per file (the OD values, 3.1.1) or per event (the event labels, 3.2). Click a cell and type, or select what is there and type over it; Tab moves across and Enter moves down. A cell that cannot be used turns red. While a table is open, a **Confirm** button takes the place of the answer box: press it when the table is filled in. If a cell is still wrong or empty, one line names it and the table stays open.
- The **Help** button beside the answer box is greyed out for now.
- **Yes → / No →** says which question comes next. **Next** means the next question in this list.
- In sections 1 to 3 the numbers on screen are the numbers here. A question asked again keeps its number, and when a question is skipped the next one keeps its own, so 3.3 follows 3.2 when 3.2.1 is not asked. From section 4 on, the numbers here are for reference: on screen they are given in the order the questions are asked, so when a branch is skipped the later numbers move up, and every "Do you accept...?" question takes a number of its own.
- A "Do you accept...?" question with one way to change is a yes or no question, `(Y/n)`: the grey line just above it says what **n** does ("Type n to change the labels again."). One with more ways to change is a numbered list starting with **1) Yes, accept**, which moves on; its other answers (**2) No, ...**, and **3**, **4** ... where there are more) each say what is asked again, with your last answers as the defaults.
- The plot on the right is redrawn after each step marked **(plot)**. You can flick through the files with the arrows or the drop-down above the plot at any time while a question waits. The file shown and the one on each side of it are redrawn at once; any other file is drawn when you go to it, with its last plot under the **Drawing ...** sign meanwhile. From section 6 on, every file shows the plot saved for it (after **5.8**); a file whose plot could not be saved says so.
- The **strip** under the plot shows what the run uses: **Haems** (ticked when the haems are worked out and shown), the **Fit** and the **Background**; **Spectra** (the spectrometer whose spectra hold the haems), **Haems as** (how the haems are shown) with its **per OD** box, **OCR as** (how the OCR is shown) and **Labels as** (what the event labels show); the **Δψ** row (the numbers of Δψ, only while Δψ is worked out, 4.5); the **Journal**, the **Width** and the **Height** of the figure of each file, the **Export master** button and the **Standard order** button.
    - The **panels** of the plot of a file can be moved: while the strip can be used, a small up and a down arrow sit left of each panel, and a click moves that panel one place (the arrow that cannot be used, up on the top panel, is paler). No question is asked: the plot is redrawn at once and one line in the terminal says the new order. The order holds for every file and for the figure saved for each, and is kept with the dataset. A panel that comes later (a haem ticked since, Δψ switched on) is drawn just above the panel that follows it in the standard order, or at the bottom. **Standard order** puts the panels back: oxygen, OCR, the haems a then b then c, Δψ. The arrows are away while edges are dragged on the plot (trimming, the regions, the averaging windows) and while the plot is being redrawn.
    - **Spectra** is shown only when your files share more than one spectrometer (Cyt and NADH). Picking the other one works the haems out from its spectra.
    - **Haems as** swaps the haems between ΔD (mOD), the change from the start; % oxidised (reduced region = 0 %, oxidised region = 100 %); and Absorbance (mOD). % oxidised is in the list only when at least one file has both regions (4.4); a file without both stays in ΔD, as its axis says. The choice holds for every plot of your files and for the figure saved for each file.
    - **per OD** (beside Haems as) scales the haems by OD. The box is shown only once you have entered OD values (3.1), and a message says so then. It is greyed while the haems are in % oxidised, which has no per OD.
    - **OCR as** swaps the OCR between µM min⁻¹; per OD (µM min⁻¹ OD⁻¹), in the list only once you have entered OD values (3.1); % of the range; and % of baseline (the average in the baseline window = 100 %), in the list only once the averaging windows are set up (4.6). A file without a baseline (less than 10 s of data before its first addition, or no addition) keeps its usual OCR, as its axis says, and one line says so. The choice holds for every plot of your files and for the figure saved for each file.
    - **Labels as** swaps the event labels between **In the chamber** (the concentration in the chamber after the addition, `400 µM KCN`; the standard) and **What was added** (`10 µL of 200 mM KCN`). An event with no stock and volume shows its concentration in the chamber either way, and one with no concentration its label alone. The choice holds for every plot of your files, the figure saved for each file and the labels under the windows of the haem and OCR figure, and is kept with the dataset.
    - While your files are on the plot (sections 2 to 5), you can change it whenever a question waits. The plot is redrawn at once, the run uses the change, and the question goes on waiting.
    - Unticking Haems leaves the haems out of the run. Ticking it, or picking a fit, works them out with the fit shown and ticks the box.
    - If a fit cannot be used, one line says why and the strip goes back to what it showed.
    - A new journal, width or height redraws the plot only in section 5, the one plot drawn at the figure's size. Before that the change is kept for section 5.
    - The **Journal** list holds every journal of the `journals` folder. Choosing one makes the figure follow what it asks: the widths offered, the tallest figure, the text sizes, the panel letters, the font and the thickness of the lines.
    - **Export master** saves one page of the journal as a PDF in the results folder (`<file>_master_<journal>.pdf`): the figure of the file shown at its printed size, a box where its legend goes and grey lines where the text of the paper goes. It works in section 5, where that figure is on the plot; before that, one line says so. With **None** the page is Nature's. A journal whose page size is not known is shown on an A4 page, and the page says so.
    - The strip is greyed out while you choose the folder, during the questions of 4.A.1, and from section 6 on.
    - In section 2 the strip has one more row, above the others: the times of the trimmed and ignored edges of the file shown, and **Every file** (see section 2). While **4.4** waits, that row holds the times of the oxidised and the reduced region instead (see 4.C).
- While the program draws a picture of its own (the components found from the data, the figures of sections 6 and 7), a yellow **Drawing ...** sign is on the plot. It goes when the picture is shown or the next question is asked.
- Sections **1** to **3** are the import: your files, the parts of them that are used, and what is known about each run (the OD values, the temperature and the labels). The processing starts with section **4**.

---

## 1. Your files

| # | Question | Answer leads to |
|---|---|---|
| 1.1 | What is the directory with the .paf files? | The folders in the program folder (in the Mac app, in the Portimao folder in your home folder) that hold `.paf` files are listed first, numbered, with how many files each holds. Answer with a number or a name from that list, or type (or drag in) the path of another folder; Enter gives the folder used last time. An empty answer, a folder that does not exist, or one with no `.paf` files, is refused: one line says what to type and the question waits. Otherwise every file is read and listed, then **1.2**. |
| 1.2 | To which directory would you like the results to be saved? `[the results folder inside the data folder]` If the dataset was run before, a message says its saved settings are offered as the defaults, and its last results folder is offered here. A name without a path, such as `quadratic_scatter_results`, is made inside the data folder, so a second set of results can sit beside the first. | A file, or a folder that cannot be saved to, is refused: one line says what to type and the question waits. **1.2.1** if the folder already holds results of any of these files; otherwise the standard plot is drawn **(plot)**, then **2.1** |

| # | Question | Yes → | No → |
|---|---|---|---|
| 1.2.1 | *(only when the folder already holds results of these files; above it: "results already holds results of 12 of these 12 files.")* Do you want to write over them? `(y/N)` | the standard plot is drawn **(plot)**, then **2.1**; results written later replace those there | **1.2** again, offering a free name beside it (`results_2`), with the line "Type another folder, or a new name: a name without a path is made inside the data folder." |

The standard plot of every file is then drawn with no question asked: the set and measured oxygen, the OCR and the haems (as the change from the start), with the event labels as written in the file. A dataset saved with Δψ switched on (4.5) also has its Δψ panel (the lowest, unless you moved it) on the files with both regions, and a dataset saved with its panels moved is drawn in that order. The haems are worked out with the standard fit (the preset `bswitch_no2_mycobl_b557.csv`), or with the fit last saved for the dataset. If that fit is not in the `fits/` folder or cannot be read, or the files do not share the spectrometer it is used on, a message says the haems are not shown yet, and only the oxygen and the OCR are drawn. A dataset last saved without haems is drawn without them, and its strip offers the standard fit. The strip then becomes usable: Haems is ticked when the haems are shown.

---

## 2. Trimming and ignoring

TRIM = data that is not imported, plotted or used. IGNORE = data that is plotted but not used for calculations. The plot shows the standard plot of the whole recording of each file (with the haems, when they are shown; the strip turns them on and off and picks their fit), with four edges on it: the trimmed start and end in grey (the parts trimmed away grey and hatched) and the ignored start and end in amber (the parts ignored amber). Each edge has a handle above the plot with its minutes beside it, the trimmed ones in the top row and the ignored ones just under them. Moving an edge never draws the plot again.

- **Drag** an edge by its handle or by its line; over an edge the mouse becomes a two-way arrow. The shading follows at once, and the edge moves in steps of 0.1 min. A trimmed edge stops at the first or the last event, so no addition is cut away, and the ignored parts stay inside the kept part without crossing. Where two edges meet, the line takes the ignored one; the trimmed one is still taken by its handle.
- **Type** the minutes in the row of the strip under the plot: **Trim start** and **end** (from the start and the end of the recording), **Ignore first** and **last** (from the trimmed edges). Press Enter or leave the box. A number that cannot be used turns the box red, with what to type beside it; a number beyond a limit is kept at the limit.
- **Every file**, ticked when the step opens: an edge moved or typed on the file shown moves on every file, to the same minutes from its own start or end, within that file's limits. Unticked, only the file shown changes. A file whose times differ from most files is marked **(own times)** in the drop-down.
- The edges start where they were left the last time the dataset was run; for a dataset never run, the first 5 minutes are ignored and nothing else. When this step is opened again (**4.3**, or going back at **5.8**), the limits it had are drawn as red dashed lines, so you can see how far you moved them.

| # | Question | Leads to |
|---|---|---|
| 2.1 | Drag the edges on the plot, or type the times in the strip under it. Press Enter when every file looks right. (above it, in grey: what TRIM and IGNORE mean, and "Grey edges trim, amber edges ignore; with "Every file" ticked, a change moves every file.") | Enter with the answer box empty: the limits of every file are listed, the plot shows the data they keep **(plot)**, then **3.1**. Anything typed in the answer box instead gets one line saying to type the times in the strip, and 2.1 goes on waiting. |

If you exported the data at 3.4 and this step is asked again (**4.3**, or going back at **5.8**), each file whose edges changed is exported again with the same choice, and a message says how many. With a choice that writes the whole recordings (3 or 5), the whole recording of a file is written only when the file has just become trimmed, and taken away when it is no longer trimmed.

---

## 3. OD values and event labels

The last part of the import: what is known about each run (the OD values, the temperature and the event labels), then the offer to export what was imported. The OD values and event labels saved for the dataset (in `portimao_settings.json`) are offered as defaults. The plot is the standard plot, cut to the limits of section 2.

### 3.A OD values and temperature

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.1 | Do you want to scale by OD? `(y/N)` (above it, in grey: "Scaling by OD divides the OCR and the haems by dilution factor × OD × volume; the strip under the plot then offers per OD for each.") | **3.1.1** | **3.1.2** (no OD scaling anywhere in the run) |

The OD table opens on the terminal side, with one row per file and a column each for the OD, the volume (mL) and the dilution factor. The values stored for a file are filled in, and the dilution factor is 1 when none is stored. Clicking a cell of a file shows that file on the plot.

| # | Question | Leads to |
|---|---|---|
| 3.1.1 | Fill in the OD, volume and dilution of each file, then press Confirm. (above it, in grey: "One row per file: the OD of the cells added, the volume of cells (mL) spun down and resuspended in 5 mL, and the dilution factor if the cells were diluted mid run.") | If a cell is empty or not a number above 0, one line names those cells and the table stays open. Otherwise the table closes, the values of every file are listed and the next step is **3.1.2**. |

Once the values are in, the strip under the plot shows the **per OD** box of the haems and has per OD in the **OCR as** list, and a message says so: "The OCR and the haems can now be shown per OD, in the strip under the plot: the per OD box beside Haems as, and per OD under OCR as." The plot follows them from here on, and so does the figure saved for each file.

The temperature is asked of every dataset, whether or not you scale by OD: one value for all its runs, kept with the dataset. Δψ (4.5) is worked out with it; nothing else uses it. It is the same value as the Temperature of the Δψ row of the strip (4.D): changing one changes the other.

| # | Question | Leads to |
|---|---|---|
| 3.1.2 | What was the temperature of the runs (°C)? `[37]` | a number from 0 to 100; then **3.2** |

### 3.B Event labels

If no file has any event, nothing is asked here and the next step is **3.4**.

The labels table opens on the terminal side: one row per event, under the name of its file, with the time of the event (min), the text in the file (grey, not typed in), its label, the **Stock**, the volume **Added (µL)** and the concentration **In the chamber**. Each row starts as saved for the dataset, or else with the label as written in the file; an event left out before reads `ignore`. Clicking a cell of a file shows that file on the plot. The **Symbols** row under the table types µ, ⁻¹, ₂ and the like into the cell last typed in.

- Type the stock with its unit (nM, µM, mM or M, in any capitals; `u` for µ); a number alone is mM. Once a row has both a stock and a volume, its concentration in the chamber fills itself in, in green, and cannot be typed in: stock × volume ÷ 5 mL (the chamber), the same label added again in a file adding up (10 µL of 200 mM KCN gives 400 µM, the next 800 µM). The maths is in `MATHS.md`, section 8.
- A row with no stock and volume takes a concentration in the chamber typed by hand (a number alone is µM), or none.
- Concentrations are written in their most readable unit: 1.2 mM, not 1200 µM.

| # | Question | Leads to |
|---|---|---|
| 3.2 | Fill in the label, the stock and the volume added of each event, then press Confirm. (above it, in grey: "One row per event. Write ignore as the label to leave an event out. Type the stock with its unit (nM, µM, mM or M; a number alone is mM) and the volume added, and the concentration in the chamber (5 mL) is worked out, the same label added again adding up. Or leave them empty and type the concentration in the chamber (a number alone is µM).") | An event labelled `ignore` (in any capitals) is left out, and its other cells are greyed out. If a label is empty, a stock, volume or concentration cannot be used, or a row has a stock without a volume (or a volume without a stock), one line names those cells and the table stays open. Otherwise the table closes: **3.2.1** if a label could be written more tidily; the concentrations are worked out from the labels as they then are, the labels of every file are listed (with what was added and the concentration in the chamber) and drawn **(plot)**, then **3.3**. |

A label is written more tidily with `u` in front of a unit as µ (`100 uM` as 100 µM), a litre as a capital L, a space between a number and its unit, and `-1` after a unit or anything after `^` raised (`8ug ml-1` as 8 µg mL⁻¹). Only units are changed: a name with numbers in it (`nd-011992`) and a formula (`H2O2`) are left as they are. The labels that could be tidier are listed as "label -> tidy form", then:

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.2.1 | *(only when a label could be tidier)* Do you want to use these tidy forms? `(Y/n)` | every listed label is replaced by its tidy form; the labels are listed and drawn **(plot)**, then **3.3** | the labels stay as typed and are not offered again while you go through the labels; the labels are listed and drawn **(plot)**, then **3.3** |

| # | Question | Yes → | No → |
|---|---|---|---|
| 3.3 | Do you accept these event labels? `(Y/n)` (above it: "Type n to change the labels again.") | **3.4** | **3.2** (the table opens again with the labels as you left them) |

### 3.C Export

| # | Question | Leads to |
|---|---|---|
| 3.4 | Would you like to export the individual experiment files now? `(1/2/3/4/5)` (above it, in grey: "The summary sheet is a workbook for each file; the raw CSVs are its spectra, which are large and take a while to write."; and, when no file is trimmed: "No file is trimmed, so "trimmed and full" writes the same as "trimmed".") 1) No 2) Summary sheet, trimmed (about *size*) 3) Summary sheet, trimmed and full (about *size*) 4) Summary sheet and raw CSVs, trimmed (about *size*) 5) Summary sheet and raw CSVs, trimmed and full (about *size*). Enter gives 1, also for a dataset exported before. | **1**: nothing is written, then **4.1**. **2 to 5**: every file is exported, then a message says where, and **4.1** |

The sizes are worked out for your files, less for a trimmed one: about 0.3 MB of workbook and 1.2 GB of spectra for each 100 MB `.paf` file. Each file is exported to its own folder in the results folder, `<results>/<file>/`:

- `<file>.xlsx`, with every choice but 1: the trimmed data (all of it for a file not trimmed), with the sheets **Measured O2** and **Set O2**, **OCR**, **Events** (the time, the text in the file, your label, the stock (mM) and volume added (µL), what the addition added and the concentration in the chamber (µM), and whether the event is ignored) and **Metadata** (your OD, volume and dilution, the trimmed and ignored edges in minutes, and the spectrometers). The run later writes this workbook again with its own results added.
- the spectra csv files, with 4 and 5: one per spectrometer and kind (`Cyt_transmiss.csv`, `Cyt_intensity.csv`, `Cyt_attenuation.csv`, and the same for `NADH`), wavelengths down and one column per spectrum; the workbook lists them on a first sheet, **Spectral data**.
- `full/`, with 3 and 5, only for a file you trimmed: the same for the whole recording (its spectra with 5). It does not record the edges, so it stays as it is when they change.

Nothing is scaled by OD, decomposed or averaged, and the ignored parts are included.

---

## 4. Processing

The plot is the standard plot, cut to the limits of section 2, with the event labels of section 3. It is redrawn after each step marked **(plot)**.

### 4.A Haem fit

The haems on the plot are those of the import, worked out with the standard fit, the fit last saved for the dataset, or the fit you picked or built in the strip, with the background in the strip. A message names that fit ("The haems are worked out with *fit*.", or "... with Your own haems: *c1_myco, bH_bswitch, ...*"). The section then starts at **4.2**. 4.1 is asked only when the plot shows no haems yet:
- the dataset was last saved without them;
- the fit could not be used (a message in section 1 said why);
- you unticked Haems in the strip.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.1 | *(only when no haems are shown)* Do you want to decompose the haems? `(Y/n)`, or `(y/N)` when Haems was unticked in the strip or the dataset was saved without haems | **4.1.1** | **4.6** (no haems, unless you tick Haems in the strip later) |

If the `fits/` folder holds no preset and no fit file, 4.1 is still asked, and 4.1.1 then offers only *Find the components from the data*.

| # | Question | Leads to |
|---|---|---|
| 4.1.1 | Which fit would you like to use? (a numbered list of the presets of the haem library, then your own fit files in the `fits/` folder, and *Find the components from the data (principal component analysis)* last; the fit in the strip is the default) | **4.1.2** if the files have more than one spectrometer in common and the default one is not among them, otherwise the decomposition is drawn **(plot)**, then **4.2**; the last choice leads to **4.1.1.1** (after 4.1.2 if that is needed). If the fit file cannot be read, a message says so and the haems are not decomposed: **4.6**. |
| 4.1.2 | Which spectrometer holds the haem spectra? | the decomposition is drawn **(plot)**, then **4.2** (or **4.1.1.1** when the components are being found) |

The section starts with a message pointing to the strip: "Use the strip under the plot to change the fit, the background, the spectrometer (Spectra) and how the haems are shown (Haems as); the plot is redrawn after each change." (the spectrometer is named only when your files share more than one).

While 4.2 waits, the strip under the plot changes the decomposition, and the plot is redrawn after each change:
- **Fit**: another preset or fit file of your own.
- **Spectra** *(only when the files share more than one spectrometer)*: the spectrometer whose spectra hold the haems, Cyt or NADH.
- **Haems as**: ΔD (mOD), % oxidised (once a file has both regions, 4.4) or Absorbance (mOD), with **per OD** beside it when OD values were entered.
- **Background**: the background fitted under the haems (Rowan scatter, the standard; Valencia; flat + 1/wavelength; flat + 1/wavelength + 1/wavelength²; straight line).
- **Build a fit**: folds out a tick box for each haem of the library, one line each for the a, b and c haems; the boxes start with the haems of the preset in use. Ticking or unticking a box works the haems out with the ones ticked, and the Fit drop-down reads *Your own haems*. Ticking a haem with the same name as one already ticked (c1_myco and c1_037v are both Cyt cc) unticks the other, and the last box cannot be unticked; a note beside the height says so. Click the button again to fold the boxes away.
- **Keep to compare**: keeps everything as it is on the plot at the click (the fit, the background, the oxidised and reduced regions of every file and the numbers of the Δψ row), and a line in the strip says which one is kept. Change the fit, the haems ticked, the background, the regions or a number of the Δψ row, and the kept haems are drawn as dashed, paler lines in the same colours under the new ones, on every file; the kept Δψ is drawn the same way in the Δψ panel (4.D). Under the plot, each haem in both has two numbers, largest / average: the largest and the average distance between its two traces, in the units of the haem panels; Δψ has the same two numbers in mV, over the spectra where both have a value. A file that had no regions when you clicked has no kept Δψ, and one sentence under the plot says so. While one is kept, two buttons choose between the two, and either one takes the dashed lines away: **Keep this one** carries on with what is on the plot; **Go back to kept** puts the kept fit, haems, background, spectrometer, Δψ numbers and regions of every file back in use (while you are still choosing the regions in 4.4, the regions stay as they are on the plot, and one line says so). The terminal says which one you carry on with. To compare again, click *Keep to compare* again. Each file takes about twice as long to draw while one is kept.

To leave the haems out, untick Haems in the strip; answering yes then goes on without haems, to **4.6**.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.2 | Do you accept this decomposition? `(Y/n)` (above it: "Type n to find the components from the data.") | **4.3** (**4.6** when Haems was unticked) | **4.1.1.1** (the questions of 4.A.1, then 4.2 again with the components) |

#### 4.A.1 Components from the data (principal component analysis)

Asked when the last choice of 4.1.1, or No at 4.2, is taken. The strip is greyed out until they are answered, and its fit list then includes a fit file saved in 4.1.1.9. The numbers keep counting up when a question is asked again, and each component name is a question of its own, so the numbers on screen can be higher than these. The files are read for their spectra (trimmed, without the ignored parts; this can take a moment). Once the components are made, the plot window gets a *PCA components* picture (one panel per component, coloured by the haem type it looks like) and a *PCA examples* picture (the best and worst described spectrum and their residuals) after the files **(plot)**. The **Drawing ...** sign is on the plot while they are made. They go when the decomposition is drawn.

| # | Question | Leads to |
|---|---|---|
| 4.1.1.1 | Where should the spectral window start (nm)? | **4.1.1.2** |
| 4.1.1.2 | Where should the spectral window end (nm)? | **4.1.1.3** (or this question again if the analysis cannot be run, for example the window is too narrow) |
| 4.1.1.3 | How many components should be found? (The data suggest *N*; use as few as describe the data, extra ones only fit noise.) | a whole number; the number used last time, or else the suggestion, is the default; then **4.1.1.4** |
| 4.1.1.4 | Do you want to rotate the components so each is as peak-like as possible (varimax)? `(Y/n)` | **4.1.1.5** |
| 4.1.1.5 | Over how many nm should the components be smoothed to remove their noise (0 for none)? (default 4, or the width used last time; at most a quarter of the window) | the components and the examples are drawn **(plot)**, with one line per component (type, peak, share of the change) and the residual, then **4.1.1.6** |

| # | Question | 1 → | 2 → | 3 → | 4 → |
|---|---|---|---|---|---|
| 4.1.1.6 | Do you accept these components? `(1/2/3/4)` | **4.1.1.7** | **4.1.1.3** (the number of components) | **4.1.1.1** (the window) | *No, choose a fit file instead*: **4.1.1**, or **4.2** when you came from 4.2 (pick the fit in the strip) |

| # | Question | Leads to |
|---|---|---|
| 4.1.1.7 | Do you want to name the components? `(y/N)` | yes: one question for each component, "What is component *N* (*type*, largest peak at *X* nm) called?", suggesting a name from its type such as *a-like* (a name that is empty, has a comma or is used twice is asked again), then **4.1.1.8**; no (PC1, PC2, ...): **4.1.1.8** |
| 4.1.1.8 | Do you want to save these components as a fit file in the fits folder? `(Y/n)` | yes: **4.1.1.9**; no: the decomposition is drawn **(plot)**, then **4.2** |
| 4.1.1.9 | What should the fit file be called (without .csv)? | the name of a preset is refused (one line says so and the question waits); if a fit file of that name exists, it asks "*name*.csv already exists. Do you want to replace it?" `(y/N)` (no asks for a name again); then the decomposition is drawn **(plot)**, then **4.2** |

### 4.B Trim and ignore times again

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.3 | *(only when the haems are decomposed)* Do you want to change the trim and ignore times now that the haems are shown? `(y/N)` | section 2 (**2.1**) is asked again with its own number, with the edges where you left them, your limits as red dashed lines and the haems of the chosen fit on the plot; if you exported at 3.4, the files whose edges changed are exported again (see section 2); then the plot is redrawn **(plot)** and **4.4** | **4.4** |

### 4.C The oxidised and reduced regions

*(only when the haems are decomposed)* The oxidised region is a stretch of the run where the haems are fully oxidised, the reduced region one where they are fully reduced. Each haem's level in the two (its median there) is what its % oxidised is worked out from. The program never places a region: you pull each out on the plot, in red for oxidised and blue for reduced, or leave it as it is.

- Both regions start **not chosen**: one red handle at the left of the used part of the run reading "oxidised: not chosen", one blue handle at the right reading "reduced: not chosen". **Pull** a handle out, by the handle or its line, and the region opens from that side, shaded in its colour; its second edge then has a handle too, and the times of the region are written beside it. The edges move in steps of 0.1 min, and moving one never draws the plot again.
- **Type** the times in the row of the strip under the plot: **Oxidised from** and **to**, **Reduced from** and **to**, in minutes as on the time axis of the plot. Press Enter or leave the box.
- An edge stays in the used part of the run (not trimmed, not ignored). Moved past the other edge of its region, it pushes that edge along. The two regions never overlap: an edge moved into the other region stops at that region's nearer side, so moved on past its middle it comes out on the far side.
- A region shorter than 10 spectra (5 s when a spectrum is taken every 0.5 s) counts as not chosen: its shading goes and its handle reads "not chosen" again.
- **Every file**, ticked when the step opens: an edge set on the file shown is copied to every file at the same distance from the addition nearest to it, counted in order (1.5 min before the 3rd addition of the file shown is 1.5 min before the 3rd addition of every file), then kept within that file's own limits. A file with fewer additions keeps the edge it had. Unticked, only the file shown changes.
- If you go back to the processing step later in the run, the regions are where you left them, on the same data even when the trim has changed.
- The regions are saved with the dataset (in `portimao_settings.json`), so they are on the plot the next time it is opened.
- The regions are optional. A file with both has each haem's oxidised and reduced level, and its haems can be shown in % oxidised (Haems as in the strip, and 7.2.2); a file with none, or with only one, cannot, and nothing else changes for it. Once a file has both, a message says: "The haems can now be shown in % oxidised: choose it under Haems as in the strip under the plot."

| # | Question | Leads to |
|---|---|---|
| 4.4 | Pull the oxidised and the reduced region out on the plot, or type their times in the strip under it. Press Enter when every file looks right, or straight away for no regions. (above it, in grey: what the regions are, "Red is oxidised, blue is reduced; with "Every file" ticked, an edge is copied to every file at the same distance from its nearest addition.", "Leave both as "not chosen" for no regions." and "With no regions the haems cannot be shown in % oxidised; everything else is the same.") | Enter with the answer box empty: with no region on any file, or both regions on every file, the regions are listed, then **4.5** (**4.6** when Δψ cannot be worked out); with both regions on some files only, **4.4.1**. A warning names the files that kept an edge of their own because they have fewer additions. Anything typed in the answer box instead gets one line saying to type the times in the strip, and 4.4 goes on waiting. |

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.4.1 | *(only when some files have both regions and others do not)* Do you want to continue without them? `(y/N)` (above it, in grey: the files without both an oxidised and a reduced region, and "A file needs both to be shown in % oxidised.") | the regions of every file are listed, then **4.5** (**4.6** when Δψ cannot be worked out) | **4.4** again, with the edges where you left them |

### 4.D Δψ, the membrane potential

Δψ is worked out from how reduced the two b haems, bH and bL, are, at the temperature of 3.1.2 (the maths is in `MATHS.md`). It can be worked out for a file with both regions (4.4), when the fit has one bH and one bL. 4.5 is asked only when at least one file has both regions and the fit has the two haems. Otherwise nothing is asked and the run has no Δψ; for a dataset saved with Δψ switched on, a message says what it needs.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.5 | *(only when Δψ can be worked out)* Do you want to work out Δψ? `(y/N)` (above it, in grey: "Δψ is the membrane potential, worked out from how reduced bH and bL are.") | the plot is redrawn **(plot)** with a **Δψ (mV)** panel under the haems (or where you moved it to), the **Δψ** row shows in the strip, and a message says it has its own panel and ends "Change the numbers of the method in the Δψ row of the strip under the plot.", with under it "To compare fits, click Keep to compare, change the fit or the background, then click Keep this one or Go back to kept."; then **4.6** | **4.6** (no Δψ in the run) |

The Δψ panel is the lowest panel of the plot of each file with both regions: one line, with gaps where bH or bL is less than 10 % or more than 90 % reduced, as Δψ cannot be given there. A file without both regions has no Δψ panel. The panel is also in the figure saved for each file (section 5), and Δψ is in the workbook of each file when every table is exported (8.1). The limits of 10 and 90 % are the ones the program starts with.

The **Δψ** row of the strip holds the numbers of the method, and shows only while Δψ is worked out. No question is asked: type a number, press Enter (or click away), and the Δψ panel is redrawn at once, with one line in the terminal saying what the numbers now are. The numbers are kept with the dataset. To see what a change does, click **Keep to compare** (4.A) first: the Δψ of before the change stays in the panel as a dashed, paler line, with the largest and the average distance between the two under the plot. Then click **Keep this one** to carry on with the change, or **Go back to kept** to undo it.

- **bH** and **bL**: the midpoint potential of each haem while the other is oxidised (mV); 40 and −20. After each arrow, greyed, is its midpoint while the other haem is reduced (−30 and −90): the program fills it in, and it cannot be typed in.
- **fall**: how far each midpoint falls when the other haem is reduced (mV); 70. Typing it refills both greyed numbers (a fall of 60 gives −20 and −80); typing a midpoint refills its own (bH 50 gives −20).
- **Paper's values** puts back 40, −20, 70, the share of 0.5 and the limits of 10 and 90 %. The temperature stays.
- **More**, unticked, leaves the other numbers as one grey line ("share 0.5 · 37 °C · given between 10 and 90 % reduced"); ticked, they are boxes: the **Share** of the membrane potential that lies between the two haems, the **Temperature** of the runs (°C, the value of 3.1.2) and the two limits (**Given between** ... **and** ... **% reduced**).
- A number that cannot be used turns its box red, with one sentence under the row, and the number in use stays: something that is not a number; a share of 0 or less; a temperature outside 0 to 100 °C (as 3.1.2); a lowest limit that is not above 0 and below the highest; a highest limit that is not above the lowest and below 100.

### 4.E The averaging windows

An averaging window is a stretch around an addition that an average is taken over. There are two kinds, and you can have either or both:

- A **settled window** ends a set time before the next addition (the last one 0.5 min before the end of the recording): the level once things have settled after the addition before.
- A **quick window** starts a set time after its own addition: the quick response to it.

The windows are placed around the events as they were left in 3.B: an event marked `ignore` gets none. Every window of a kind has the same length, so each moves with its addition in every file and one setting fits the whole dataset. The window before the first addition is the baseline, which both kinds are compared with; it is there whenever either kind is ticked, with the length and the gap of the settled windows.

- The baseline is **shaded gold** on the plot of every file, with "baseline" and its length by its first edge. It is as long as a settled window and ends the same time before the first addition, so pulling its edges changes the settled windows too.
- The settled windows are **shaded blue** on the plot of every file, 120 s long and ending 30 s before the next addition; the quick windows are **shaded green**, 30 s long and starting 10 s after their addition; or both are as they were saved with the dataset. They are over the plot only in this step; the steps before it show none.
- **Pull the start** of a settled window, by its handle or its line, to change its length; **pull its end** to change the gap before the addition. **Pull the start** of a quick window to change how long after the addition it starts (its length stays); **pull its end** to change its length. Every window of that kind in every file follows, in steps of 5 s, and the plot is not drawn again. The end of the last settled window cannot be pulled: it stays 0.5 min before the end of the recording.
- **Type** the numbers in the two rows of the strip under the plot, in seconds: **Settled window** and **Gap before the next addition** in the first, **Quick window** and **Start after the addition** in the second. Press Enter or leave the box. A window of 0 s is not taken.
- A window that **does not fit** is shaded red with hatching: a settled window that would start before its own addition, a quick window that would end after the next addition (or after the end of the recording), or a baseline shorter than 10 s. After Enter a warning names these windows for each file; they are left out of the averages.
- **Settled windows** and **Quick windows**, the tick boxes of the two rows. Settled windows is ticked and Quick windows unticked when the step first opens on a dataset. Untick both for no windows: the windows go from the plot, nothing is averaged, and the figures of each file show none.
- The windows are saved with the dataset (in `portimao_settings.json`), ticked or not.
- When none of the files has an addition, the step is not asked and one line says there are no averaging windows.

| # | Question | Leads to |
|---|---|---|
| 4.6 | Drag an edge of any window on the plot, or type the numbers in the strip under it, where each kind of window has its tick box. Press Enter when the windows look right, or untick both kinds for none. (above it, in grey: what the windows are, "The baseline (gold) is the window before the first addition, as long as a settled window; every other window is compared with it.", "A settled window (blue) ends a set time before the next addition, the last one 0.5 min before the end of the recording; a quick window (green) starts a set time after its addition. Each kind has one length, in every file." and which edge to pull for what) | Enter with the answer box empty: one line for each kind says the windows chosen (or one line that there are none), a warning names those that do not fit, the plot is redrawn with the windows **(plot)**, then **5.1**. Anything typed in the answer box instead gets one line saying to type the numbers in the strip, and 4.6 goes on waiting. |

Three later figures need the averaging windows: the 2x2 grid (**6.3**), the time response (**7.1**) and the haem and OCR response (**7.2**). They use the windows chosen here and never ask for a window or a gap of their own. When you say yes to one of them and no windows are set up (both kinds unticked in 4.6, or no file with an addition), one line says "No averaging windows are set up, and this figure needs them.", and 4.6.1 is asked before the figure's own questions. It keeps this number wherever it is asked. The OCR as % of baseline (**5.3.1**) needs them in the same way: there, without windows, the OCR stays as it was and the figure of each file is drawn again.

| # | Question | Yes → | No → |
|---|---|---|---|
| 4.6.1 | Do you want to add them now? `(Y/n)` | **4.6** opens on the plot of every file, by itself (nothing else of the processing is asked again, and the strip stays greyed out apart from the rows of the windows), with Settled windows ticked. After Enter, with windows set up, the figure's own questions follow; with none still, one line says the figure is not made and the next figure is asked | one line says the figure is not made, and the next figure is asked |

Once windows are added this way they are the dataset's windows: the later figures do not ask, and they are saved with the dataset.

Each of the three figures uses one kind of window, with the baseline. With both kinds set up, 4.6.2 is asked before the figure's own questions (after 4.6.1 when that was asked); it keeps this number wherever it is asked, and each figure remembers its own answer. With one kind set up nothing is asked: one line says the figure uses that kind.

| # | Question | Leads to |
|---|---|---|
| 4.6.2 | Which windows should this figure use? `(1/2)` 1) Settled, before the next addition; 2) Quick, after each addition | the figure's own questions |

The plots and the workbook of each experiment (section 5) show both kinds: the quick windows green, the settled windows blue and the baseline gold with "Baseline" written above it, and a **Kind** column in the Averages sheet.

---

## 5. Individual experiment plots

The figure saved for each file is drawn at once **(plot)**, at its real size and as it will be saved, with the standard settings or, for a dataset run before, the settings last saved for it. You change only what you want different. The standard figure has:

- the set and measured oxygen;
- the OCR per OD (µM min⁻¹ OD⁻¹) if you said yes to OD scaling in 3.1, otherwise the OCR in µM min⁻¹;
- when the haems were decomposed in 4.A, every haem of the fit as ΔD, the change from the start (scaled by OD as well if you said yes in 3.1);
- Δψ (mV) as the lowest panel, if you said yes in 4.5, for a file with both regions;
- the event labels at 45°;
- Nature, 1 column wide and 0.5 of a page tall.

The haems are in the figure when Haems is ticked in the strip. How the haems are shown (Haems as, with its per OD box), how the OCR is shown (OCR as), the journal, the width and the height are set in the strip too, as you left them in the earlier sections: each change redraws the figure at once. A message under the first one says so.

| # | Question | Leads to |
|---|---|---|
| 5.1 | Do you accept this figure? `(1/2/3/4)` | **1) Yes, accept**: **5.8**. **2) No, change the oxygen and OCR**: **5.2**. **3) No, change which haems are shown** *(only when the haems are plotted)*: **5.4.1**. **4) No, change the angle of the event labels** *(only when something is plotted)*: **5.6**. When nothing is plotted, the oxygen and OCR are the only change, so it is a yes or no question `(Y/n)`: **No** leads to **5.2**. |

Each part's questions offer your current choices as the defaults. After them the figure is drawn again **(plot)** and **5.1** is asked again; the numbers on screen keep counting up. If nothing is plotted (5.2 and 5.3 No, and Haems unticked), a message says no individual figures will be made, nothing is drawn, and 5.1 is asked again so you can turn a panel back on; accepting then makes no individual figures.

### 5.A Oxygen and OCR

| # | Question | Leads to |
|---|---|---|
| 5.2 | Do you want to plot the set and measured [O2] (CsO2 and CcO2)? `(Y/n)` | **5.3** |
| 5.3 | Do you want to plot the OCR? `(Y/n)` | **Yes**: **5.3.1**. **No**: the figure is drawn **(plot)**, then **5.1**. |
| 5.3.1 | Which OCR would you like to plot? 1) OCR (µM min⁻¹) 2) OCR / OD (µM min⁻¹ OD⁻¹), *only offered if you said yes to OD scaling in 3.1*. 3) OCR (% of the range) 4) OCR (% of baseline) | the figure is drawn **(plot)**, then **5.1** |

These are the choices of **OCR as** in the strip, which shows the one picked. The % of baseline is the OCR divided by its average in the baseline window (the window before the first addition, 4.6) × 100, so the baseline is 100 %. It needs the averaging windows: when none are set up, one line says "No averaging windows are set up, and the % of baseline needs them." and **4.6.1** is asked; without windows the OCR stays as it was, and one line says so. A file without a baseline keeps its usual OCR (per OD if you entered OD values, otherwise µM min⁻¹), as its axis says, and one line says so.

### 5.B Which haems

Whether the haems are plotted at all is the Haems box in the strip; this question picks which of them, and their order.

| # | Question | Leads to |
|---|---|---|
| 5.4.1 | Which haems would you like to plot? (the numbers of the haems; the grey line above says to separate them with commas, and the haems shown are brighter in the list and are what Enter gives; their panels are moved with the arrows beside them) | the figure is drawn **(plot)**, then **5.1** |

### 5.C How the haems are shown

No question is asked: **Haems as** in the strip under the plot swaps the haems between ΔD (mOD), the change from the start; % oxidised (reduced region = 0 %, oxidised region = 100 %), *only offered when at least one file has both regions (4.4)*; and Absorbance (mOD). The **per OD** box beside it scales them by OD as well *(shown only if you said yes to OD scaling in 3.1; greyed for % oxidised)*. Each change redraws the figure at once. There is no 5.5: the numbers of the later questions are kept.

- A file without both regions stays in ΔD, as its axis says, while the files with both are in %.
- A dataset saved with % oxidised opens with ΔD when no file has both regions any more.
- No concentration: only cells are measured, and a haem amount depends on the size of its shape; a dataset saved with concentration opens with ΔD.

### 5.D Event labels

| # | Question | Leads to |
|---|---|---|
| 5.6 | At what angle should the event labels be plotted (0 = horizontal, 90 = vertical)? `[45]` | the figure is drawn **(plot)**, then **5.1** |

### 5.E Journal and size

The strip sets the journal, width and height of this figure, so these questions are not asked here. They are listed because the figures of sections 6 and 7 ask their own size with them, each with its own default size; each of those sections says what comes next.

| # | Question | Leads to |
|---|---|---|
| 5.7 | Which journal format would you like? 1) None (use the default: Nature, *the figure's default width and height*) 2) Nature 3) Science 4) Cell 5) PNAS 6) ACS journals 7) PLOS ONE (every journal of the `journals` folder) | **None**: the default size is used. **A journal**: **5.7.1** |
| 5.7.1 | How wide should the figure be? (the widths that journal allows: 1, 1.5 or 2 columns for most, 1, 2 or 3 columns for Science) | **5.7.2** |
| 5.7.2 | How tall should the figure be, as a fraction of the page height (1 = a full page = *X* mm)? | the figure is drawn at its real size **(plot)** |

### 5.F Going back

| # | Question | Leads to |
|---|---|---|
| 5.8 | Do you want to go back to any of these steps? 1) No, continue 2) Trimming and ignoring 3) OD values and event labels 4) Processing 5) Individual experiment plots | **1**: the plot of every file is saved, then **6.1**. **2, 3, 4 or 5**: that section's questions are asked again from its first question, with your answers as the defaults. Your answers to the later sections are kept. Then **5.8** is asked again. |

After **1**, the plot of every file is saved in the results folder straight away (svg and png, in the file's own folder), unless nothing is plotted. Each file is read again for it, so this takes a moment: the terminal counts the files ("Saving the plot of file 3 of 12: *name*") and the window shows each plot as it is saved **(plot)**. A file whose plot could not be saved says so in one line, and is tried again when the run starts.

- The run does not draw these plots a second time. They are saved again only when a later answer changes them: at once when a later figure adds the averaging windows (**4.6.1**), and in the run when a summary figure changes the haem fit.
- If you cancel after this, the plots stay in the results folder, and the closing line says so.

---

## 6. Multi-experiment plots

If nothing is plotted in section 5, a message says these figures reuse the panels chosen for the individual experiment plots and are skipped, and the next step is **7.1**.

From here on the strip is greyed out: these figures ask their own journal and size.

Each figure is drawn from your data once its questions are answered (this reads the files again, so it takes a moment, and the **Drawing ...** sign is on the plot meanwhile) and shown in the plot area. None of these figures is saved to the results folder until the run starts.

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
| 6.2 | Do you accept this figure? `(Y/n)` (above it: "Type n to change its settings.") | **6.3** | **6.1** |

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
| 6.4 | Do you accept this figure? `(Y/n)` (above it: "Type n to change its settings.") | **7.1** | **6.3** |

---

## 7. Experiment summaries

As in section 6, the **Drawing ...** sign is on the plot while each picture is drawn. Both summary figures need the haem fit. If the haems were not decomposed in section 4 (or Haems was unticked), the fit questions (**4.1.1**, and **4.1.2** if needed) are asked first; only the fit files are offered here, not the components found from the data. If the `fits/` folder holds no `.csv` file, or the fit cannot be used, a message says so and the figure is skipped. Both figures also average around the events, over the averaging windows of 4.6. With none set up, **4.6.1** is asked after the fit and before the figure's own questions (section 4.E); without windows the figure is not made and the next figure is asked. With both kinds of window set up, **4.6.2** then asks which kind the figure averages over; in the time response, the difference spectrum is the last window of that kind minus the one before it.

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
| Do you accept these waterfall plots? | the next question | **7.1.2** again ("Type n to choose the time points again.") |
| Do you accept this plot? (after each kinetic trace and decomposition plot) | the next question | the same choice again ("Type n to choose another experiment.") |
| Do you accept this figure? (final) | **7.2** | **7.1** ("Type n to change its settings.") |

### 7.B Haem and OCR response

| # | Question | Yes → | No → |
|---|---|---|---|
| 7.2 | Do you want to plot a haem and OCR response? `(y/N)` | **7.2.1** | **8.1** |

File names need the strain, the addition order and the run number, for example `knockdown_kcn_then_bd_run1`. The files found are listed. If no file name fits, the figure is skipped and the next step is **8.1**.

The figure is built up in the plot window in stages. First only the baseline OCR and the OCR response are drawn, then all the haems are added, then they are redrawn with the haems and order you chose. Each stage has its own accept question (second table).

| # | Question | Leads to |
|---|---|---|
| 7.2.1 | Which OCR would you like to use? (the first three options of 5.3.1; this figure has a % of baseline of its own) | the OCR plots are drawn **(plot)**, accept question, then **7.2.2** |
| 7.2.2 | How would you like to show the haems? (the same options as Haems as in the strip, but % oxidised is offered only when every file of the figure has both regions, as the figure averages the files together) | **7.2.3** if you said yes to OD scaling in 3.1 and did not choose % oxidised, otherwise all the haems are drawn **(plot)**, accept question, then **7.2.4** |
| 7.2.3 | Do you want to scale the haems by OD as well? `(Y/n)` | all the haems are drawn **(plot)**, accept question, then **7.2.4** |
| 7.2.4 | Which haems should get a row, and in which order? | drawn **(plot)**, accept question, then **7.2.5** |
| 7.2.5 | Which journal format would you like? (then width and height, as in 5.7) | the figure is drawn **(plot)**, then the final accept question |

Each is a yes or no question, `(Y/n)`, with what **n** does on the grey line above it.

| Question | Yes → | No → |
|---|---|---|
| Do you accept the OCR plots? | **7.2.2** | **7.2.1** again ("Type n to choose the OCR again.") |
| Do you accept these haem plots? | **7.2.4** | **7.2.2** again ("Type n to choose how to show the haems again.") |
| Do you accept these haem rows? | **7.2.5** | **7.2.4** again ("Type n to choose the haems again.") |
| Do you accept this figure? (final) | **8.1** | **7.2** ("Type n to change its settings.") |

---

## 8. Data export

Every experiment always gets a workbook with everything worked out for it, each sheet named in plain words with the unit in its headings: **Measured O2**, **Set O2**, **OCR** and, when they were worked out, **OCR per OD**, **OCR % of range**, **OCR % of baseline** (every file with a baseline window, whichever way the OCR is plotted), the haems in every view (**Haems ΔD**, **Haems absorbance**, **Haems % oxidised**, and the first two **per OD**), **Δψ** and **Averages**; then **Events**, **How it was worked out** (the fit and the background, where ΔD starts, the oxidised and reduced regions and each haem's level in them, the numbers Δψ was worked out with, the OD scaling, the baseline window and the average OCR in it that is 100 % of baseline) and **Metadata**.

| # | Question | Leads to |
|---|---|---|
| 8.1 | *(only when the spectra were not exported at 3.4)* Do you want to export the spectra as csv files (large, and it takes a while)? `(y/N)` | **9** |

If you exported the raw CSVs at 3.4 (choice 4 or 5), 8.1 is not asked: one line says the spectra are not written again, and the workbook of each experiment still lists them on its **Spectral data** sheet.

---

## 9. Summary

A summary of all your answers is printed (files, results folder, trimming, ignoring, decomposition, OD scaling, temperature, Δψ, averaging, plots, figure sizes, workbooks).

| # | Question | Yes → | No → |
|---|---|---|---|
| 9.1 | Do you want to start? `(Y/n)` | Your answers are saved in the data folder (`portimao_settings.json`) for the next time this dataset is opened, and the run starts. If the data folder cannot be written to, a message says the dataset will start from the standard settings next time. Every file is processed, plotted and exported, then the multi-experiment figures and summaries are made. | The program stops and nothing else is changed: data you exported at 3.4 is kept, and the last line says so. |
