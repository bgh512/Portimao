# Portimao

Reads Espana Scientific Software `.paf` files, plots every experiment and the combined figures, and exports Excel workbooks that can be checked by hand.

Made by Beatrixette.

**Feedback:** to report a problem or ask for a change, open the [Issues page](https://github.com/bgh512/Portimao/issues) and click **New issue** (a free GitHub account is needed). When Portimao does not start on a Mac, choose **Mac problem** and paste the Mac report into it (section 2.3, entry 8).

## 1. Installation

### 1.1 On a Mac: the app

Portimao for the Mac is an app that carries everything it needs (there is no Python to install) and updates itself each time it starts. It needs macOS 14 (Sonoma) or newer.

1. Open Terminal: press Cmd + Space, type `Terminal` and press Enter.
2. Paste this line and press Enter:

    ```bash
    curl -fsSL https://raw.githubusercontent.com/bgh512/Portimao/main/install_mac.sh | bash
    ```

The line picks the app for your Mac's chip (Apple Silicon or Intel), puts Portimao in your own Applications folder and opens it. No password is asked, and macOS shows no warning. From then on, open Portimao from Launchpad, or with Spotlight (Cmd + Space, type `Portimao`); drag it to the Dock to keep it there. Pasting the line again puts the newest version in place of the one there.

**By hand**, without Terminal:

1. Find your Mac's chip: Apple menu > About This Mac. *Chip: Apple M1* (or M2, M3 ...) is Apple Silicon; *Processor: ... Intel* is Intel.
2. On the [Releases page](https://github.com/bgh512/Portimao/releases/latest), download `Portimao-mac-apple-silicon.zip` or `Portimao-mac-intel.zip`.
3. Double-click the zip in Downloads, then drag Portimao into the Applications folder (in Finder: Go > Applications).
4. Open Portimao from the Applications folder. The first time, macOS says it cannot check it: click *Open Anyway* as section 2.3, entry 1, says. This is needed only once.

**Where your things are kept.** The app keeps your own things in the Portimao folder in your home folder (in Finder: Go > Home, then Portimao):

- `fits/`: the haem fits: the haem library in `haems/` (one file per haem), the presets in `presets/` (sets of library haems, such as the standard fit). Your own fit goes in `fits/` itself (its layout is in `DATA_FORMAT.md`, under "fit csv").
- Your data folders: a folder of `.paf` files put here is offered by number at the first question. Any other folder can be typed or dragged in.
- `logs/`: what the app did, which the Mac report shows.
- `last_answers.json`: the folder used last.

**If you used Portimao before it was an app** (installed with git and opened with `Portimao.app` in the Portimao folder), it moves itself to the app at its next start, without asking.

- It installs the app in your Applications folder, takes away the old program files and opens the app.
- From then on, the link on your Desktop opens the app.
- Your fits, data folders, logs and last answers stay in the Portimao folder, which is where the app looks for them. If your folder was somewhere else, its fits and last answers are also copied into the Portimao folder in your home folder.
- A note beside the app says where everything is.

A Mac older than macOS 14 cannot run the app: it goes on starting the old way, from the *Portimao* file on the Desktop (section 2.3, entry 7). A copy installed from a zip file does not update itself: install the app with the line above, then move your own fits and data folders into the Portimao folder in your home folder.

### 1.2 Windows and Linux, using GitHub (recommended)

Git and Python 3.9 or newer must be installed first. If they are not, follow the requirements in section 1.3, then return here.

#### Windows

1. Open a terminal: press the Windows key, type `PowerShell` and press Enter.
2. Go to the folder where the project should be installed:

    ```powershell
    cd C:\Users\<username>\Documents
    ```

3. Download the project and enter its folder:

    ```powershell
    git clone https://github.com/bgh512/Portimao.git
    cd Portimao
    ```

4. Create and activate a Python environment, then install the dependencies:

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    ```

    If PowerShell refuses to run the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again. The launcher `run.bat` does this step itself, so it can be skipped if only the launcher is used.

#### Linux

1. Open a terminal (Ctrl + Alt + T on most distributions). On Debian or Ubuntu, install the requirements first:

    ```bash
    sudo apt install git python3 python3-venv python3-pip python3-tk
    ```

2. Go to the folder where the project should be installed:

    ```bash
    cd ~/Documents
    ```

3. Download the project and enter its folder:

    ```bash
    git clone https://github.com/bgh512/Portimao.git
    cd Portimao
    ```

4. Create and activate a Python environment, then install the dependencies:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

    The launcher `run.sh` sets up its own environment (`.venv_unix`), so this step can be skipped if only the launcher is used.

### 1.3 Windows and Linux, manual install

No git is needed.

#### Requirements

- Python 3.9 or newer: <https://www.python.org/downloads/> (on Windows, tick "Add python.exe to PATH" in the installer).

#### Install from the .zip

A copy installed this way does not update itself (its window title says so): download it again for a newer version, or install with git (section 1.2), which updates at each start.

1. On the project's GitHub page, click **Code**, then **Download ZIP**.
2. Extract the .zip to the desired location.
3. Open a terminal in the extracted folder: right-click inside the folder and choose **Open in Terminal**.
4. Create and activate a Python environment, then install the dependencies:

    Windows (PowerShell):

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    ```

    Linux:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

### 1.4 Following the dev branch (optional)

The steps above install `main`, the stable version. `dev` has newer changes that are not yet fully tested.

- Installed with git: from inside the project folder run `git checkout dev`, then `git pull`. To go back to the stable version run `git checkout main`.
- Manual install: on the project's GitHub page choose `dev` in the branch drop-down, click **Code**, then **Download ZIP**, and install as in section 1.3.

### 1.5 From source on a Mac (developers)

For working on the program; everyone else uses the app (section 1.1). Install Python 3.12 or newer from [python.org](https://www.python.org/downloads/) first: the `python3` that comes with macOS has an old Tk, which draws a blank window. If git is missing, run `xcode-select --install`. Keep the folder out of Documents, Desktop and Downloads, which macOS guards.

```bash
git clone https://github.com/bgh512/Portimao.git
cd Portimao
git checkout dev
sh run.sh
```

`run.sh` sets up its own environment (`.venv_unix`) and starts the launcher; `python main.py` in an environment of your own works too. Use `dev`: a copy on `main` started with `run.sh` is taken for an install of the old launcher, and is moved to the app (section 1.1).

## 2. Running

### 2.1 From the terminal

Activate the environment first (see section 1), then run:

```bash
python main.py
```

The program has no command-line options. It opens its window and asks numbered questions in the window's terminal (Enter accepts the default in square brackets); if the window cannot open, it says why and what to do, and stops. The answers are saved with each dataset, in `portimao_settings.json` inside its data folder, and offered the next time that dataset is opened (a dataset never run starts from the standard settings in `config.py`); `last_answers.json` remembers only the folder used last.

### 2.2 Using the launcher

The launchers open Portimao without leaving a terminal window open.

- Windows: double-click `Portimao.pyw` (or `run.bat`, whose window closes at once). The first time it also puts a Portimao icon on your Desktop and in the Start menu; use that from then on.
- macOS: open the Portimao app from Launchpad, Spotlight (Cmd + Space, type `Portimao`) or the Applications folder. Each start looks for a newer version on the Releases page; when there is one, a small "Updating Portimao" window shows it being downloaded (a few seconds to a minute), then the new version opens. Without internet it starts as it is. If Portimao does not start, see section 2.3.
- Linux: run `./run.sh`; the first time it adds Portimao to the applications menu and the Desktop.

On Windows and Linux, a small "Starting Portimao" window shows what the launcher is doing, and closes as Portimao's own window opens. The first run creates the program's own Python environment and installs what is needed (a minute or two, needs internet); when an update changes the list of packages (`requirements.txt`), the next start installs them again, and if that fails Portimao opens with the ones it has. Each start checks GitHub for updates when the folder is a git clone; without a connection it says so within a few seconds and opens Portimao as it is. When the update cannot be installed (for example because a program file such as `config.py` was changed here), Portimao opens as it is and says why under its version. If something goes wrong, a message box says in one sentence what to do, and `logs/launch.log` has the details. Everything the program prints goes to that file when it is started this way, each start after the ones before (only the newest part is kept once it passes 1 MB); the Mac app writes it to `logs/launch.log` in the Portimao folder in your home folder. Each run also has its own log in the `logs` folder of its results folder, with every answer, started as soon as the results folder is chosen.

Windows may show a "do you trust this software" warning the first time, because the files were downloaded and are not signed. Right-click the downloaded zip, choose Properties, tick *Unblock* and extract it (once); cloning with git avoids the warning. For the Mac, see section 2.3, entry 1.

### 2.3 If Portimao does not start on a Mac

Find what you see below and do what its entry says. If nothing here helps, run the Mac report (entry 8) and send it, as under **Feedback** at the top.

1. **"Portimao" Not Opened, or "Apple could not verify Portimao is free of malware".** Only after installing by hand: the line never asks this. Click Done, open System Settings > Privacy & Security, scroll down to the message about Portimao, click *Open Anyway* and confirm with your password, then open Portimao again. On macOS 14 (Sonoma) you can instead right-click (or Control-click) Portimao in the Applications folder, choose Open, then Open again. Needed only once.
2. **"Portimao is damaged and can't be opened".** The download was cut short, or the zip was unpacked by a program other than Finder. Move Portimao to the Bin and install it with the line (section 1.1).
3. **"Portimao V... is out, but this copy could not update itself".** Portimao starts as it is; the reason is in brackets:
    - *macOS opened it from a temporary copy*: Portimao was opened where it was downloaded. Drag it into the Applications folder and open it from there.
    - *its folder cannot be written to*: Portimao is in a folder you cannot change, often the main Applications folder of a Mac you are not an administrator of. Install it with the line, which puts it in your own Applications folder, then move the old one to the Bin.
    - *the download did not finish*: check the internet connection; the next start tries again.
4. **"Portimao needs macOS 14 or newer", or Portimao does not open on an older Mac.** Apple menu > About This Mac shows the macOS version. Update macOS if the Mac can take it (System Settings > General > Software Update), then install Portimao again. A Mac that cannot have macOS 14 runs Portimao the old way (entry 7).
5. **macOS asks whether Portimao may open Documents, Desktop or Downloads (or a network or external drive).** Click Allow: Portimao reads your `.paf` files and saves the results there. If you clicked Don't Allow, open System Settings > Privacy & Security > Files and Folders, switch the folder on under Portimao, then open Portimao again.
6. **"Portimao could not start", "Portimao's window could not open" or "Portimao stopped because of a problem".** Click *Copy details*: the Mac report is copied and the **Mac problem** form opens on the Issues page. Paste the report there (Cmd + V) and send it.
7. **A Mac older than macOS 14 (the old way).** Portimao starts from its folder, from the *Portimao* file on the Desktop (a Terminal window opens while it starts). It needs Python 3.12 or newer from [python.org](https://www.python.org/downloads/): the Python that comes with macOS draws a blank window. After installing a newer Python, delete the hidden folder `.venv_unix` in the Portimao folder (in Finder, Cmd + Shift + . shows hidden files) and open Portimao again. The first start downloads the packages Portimao needs; when it says they could not be installed, check the internet connection or try another network. A box asking to install the "command line developer tools" can be answered Install (Portimao uses them to update itself) or Not Now.
8. **Nothing happens at all, or nothing above helps: the Mac report.** Open Terminal (Cmd + Space, type `Terminal`, press Enter), paste this line and press Enter:

    ```bash
    sh ~/Applications/Portimao.app/Contents/Resources/launchers/mac_report.sh
    ```

    If you put Portimao in the main Applications folder by hand, leave out the `~` at the start of the line. On a Mac older than macOS 14 the line is `sh ~/Portimao/launchers/mac_report.sh`. The report is printed and copied by itself: paste it (Cmd + V) into the **Mac problem** form on the [Issues page](https://github.com/bgh512/Portimao/issues). The report only reads; it changes nothing on the Mac. It shows where Portimao is, which includes your Mac user name; change it before sending if you prefer.

### 2.4 Changing the icon

1. Replace `assets/icon.png` with the new icon (a square PNG, ideally 1024 x 1024 pixels).
2. Run `python launchers/make_icons.py` (inside the program's environment, for example `.venv\Scripts\python launchers\make_icons.py` on Windows or `.venv_unix/bin/python launchers/make_icons.py` on Linux). It makes `assets/icon.ico` (window, taskbar and Windows shortcut). The Mac app's icon is made from `assets/icon.png` when the app is built.
3. Delete the file `.portimao_shortcut`, then start Portimao once, so the Desktop and Start menu shortcuts are made again with the new icon.


### 2.5 The questions

1. **Your files:** the `.paf` folder and the results folder. A name without a path (`quadratic_scatter_results`) is made inside the data folder, and a folder that already holds results of these files is used only once you agree to write over them, so a second set of results can go beside the first. The plots of the files then appear on the right. As the folder is read, the instrument's OCR of each file is checked against our own calculation from its oxygen traces. A file whose numbers do not agree gets a warning naming the part that differs, and its figures still use the instrument's OCR (how the check works is in `DATA_FORMAT.md`, under "Our OCR check").
2. **Trimming and ignoring:** TRIM (data that is not imported, plotted or used) and IGNORE (data that is plotted but not used for calculations), each for the start and the end. Drag the four edges on the plot, or type their minutes in the strip under it, then press Enter when every file looks right. Ignore times count from the trimmed edges.
3. **OD values and event labels:** fill in the OD values in a table, one row per file (the per OD boxes then show in the strip), then the label and concentration of each event in a second table, one row per event. Write `ignore` as an event's label to leave out an event that was not an addition. When you press Confirm, labels whose units could be written more tidily (`8 ug ml-1` as `8 µg mL⁻¹`) are offered in their tidy forms, once. Last, you can export what was imported, to plot it yourself: the summary (a workbook per file with the oxygen, OCR, your labels, OD values and edges), with the trimmed spectra as csv files, or with the spectra of the whole recordings too, each with its size. This ends the import.
4. **Processing:** accept the haems shown, or find components from your own data instead (section 2.8); another fit, or no haems, is chosen in the strip under the plot (section 2.6); then, now that the haems are seen, change the trim and ignore times if you want; then the averaging windows, shaded on the plot before each addition: pull the start of any window to change how long they are, its end to change how long before the next addition they end, or type both in seconds in the strip under the plot; untick Averaging windows there for none.
5. **Individual experiment plots:** the figure saved for each file is drawn with the standard settings, or with the ones last saved for the dataset, and you change only what you want different: oxygen and OCR, which haems in which order, the angle of the event labels. The haems on or off, how they are shown, the per OD scaling, the journal and the size are in the strip.
6. **Multi-experiment plots:** two experiments side by side, four experiments in a 2x2 grid.
7. **Experiment summaries:** time response (waterfall time points to skip, two kinetic traces, three decomposition plots), OCR and haem response (OCR, haem form, haems and order).
8. **Data export**, then a summary and the start question.

The 2x2 grid, the time response and the OCR and haem response use the averaging windows of the processing and never ask for their own. When none are set up, the figure says so and offers to add them: the averaging windows step opens on the plot by itself, and the figure carries on once they are chosen; without windows it is not made.

The figure of each file takes its journal and size from the strip; every other figure asks for its own. `None` uses Nature with the default size.

### 2.6 The experiment browser

The program runs in one window. The left side is a text terminal that asks the questions, with a box at the bottom to type your answers in (press Enter to send; the up and down keys recall earlier answers) and a **Help** button, greyed out for now. The end of each question says what Enter alone gives, brighter than the rest: the capital letter of (Y/n), the brighter number or option of a list, or the value in [brackets]; after an answer that cannot be used, one red line says what to type and the question waits. The right side shows the plots of your files, with **< Prev** and **Next >** buttons and a drop-down list of the files under the plot. The arrows loop round, and Page Up and Page Down do the same from the keyboard. The window and the taskbar show the Portimao icon (on macOS the Dock icon needs the optional `pyobjc` package).

Above the answer box is a row of **Symbols** (µ, superscript and subscript digits such as ⁻¹ and ₂, ±, °, Δ, Greek letters and more): click one to type it at the cursor, or in the cell of a table last typed in, for example for event labels like `8 µg mL⁻¹`. The plot stays usable while a question waits. You can flick through every file at any time without answering, and the accept questions wait while you look. All files are drawn in the background with the latest answers, so flicking between them is quick. The plot can also answer some questions, and the hint under the answer box says when: the trimmed and ignored parts, the oxidised and reduced regions and the averaging windows are chosen by dragging their edges (an edge of an averaging window moves in whole steps of 5 s). You can always type instead.

Under the plot is the **strip**: **Haems** (ticked when the haems are worked out and shown), the **Fit** and the **Background**; **Spectra** (the spectrometer whose spectra hold the haems, shown when your files share more than one), **Haems as** (ΔD, % oxidised once a file has both regions, or absorbance) and the **per OD** boxes of the haems and the OCR (shown once OD values are entered); the **Journal**, the **Width** and the **Height** of the figure of each file. The terminal says when each of these becomes usable. From the trimming to the individual plots you can change it whenever a question waits: the plot is redrawn at once and the run uses the change. Unticking Haems leaves the haems out of the run; ticking it, or picking a fit, works them out with that fit. The journal and size show in the individual plots, the only plots drawn at the figure's size. The strip is greyed out when it cannot be used: while you choose the folder, while components are found from your data, and from the multi-experiment plots on. While the program makes a picture of its own (the components, the multi-experiment figures and the summaries), a yellow **Drawing ...** sign is on the plot.

- **Trimming and ignoring:** the plot shows the whole recording of each file with four edges: the trimmed start and end (grey; the part trimmed away grey and hatched) and the ignored start and end (amber). Drag an edge by its handle above the plot or by its line; the shading follows at once and the minutes show by the handle. A trimmed edge stops at the first or last event, so no addition is cut away. The strip gets a row with the four times of the file shown (trim start and end, ignore first and last) to type exact minutes, and **Every file**: ticked, a change applies to every file (the same minutes from each file's own start or end); unticked, only to the file shown, which is then marked *(own times)* in the drop-down. Press Enter when every file looks right. When you change them again later, the limits from before stay on the plot as red dashed lines.
- **OD values and event labels:** each is filled in in a table that takes most of the terminal side, with a few lines of text above it: click a cell and type (Tab moves across, Enter moves down), then press **Confirm**, which takes the place of the answer box while a table is open. The OD table has one row per file, with the values stored for each file already in; once they are entered, the per OD boxes of the strip say whether the OCR and the haems are scaled by them. The labels table has one row per event, under its file's name, with the time, the label and the final concentration (µM). A cell that cannot be used turns red, and Confirm then names the cells still wrong or empty and the table stays. Clicking a cell of a file shows that file on the plot. The event labels are then drawn for every file and accepted, or the table opens again.
- **Processing:** the decomposition is drawn for every file with each fit you pick in the strip, and the averaging windows once they are chosen; each is accepted or asked again in the same way. To compare two decompositions, press **Keep to compare** in the strip, then change the fit, the haems, the background, the oxidised and reduced regions or the numbers of Δψ: the kept haems stay on the plot as dashed, paler lines in the same colours, and so does the kept Δψ in its panel; under the plot each haem, and Δψ, has the largest and the average distance between its two traces. Then choose one of the two, which takes them away: **Keep this one** carries on with what is on the plot, **Go back to kept** puts the kept one back in use. Each file takes about twice as long to draw meanwhile. If you change the trim and ignore times here, the plot shows the haems of the fit you chose while you answer. Once a file has an oxidised and a reduced region, and the fit has one bH and one bL, you are asked whether to work out Δψ, the membrane potential: it is drawn as the lowest panel of each such file, at the temperature you gave in the import, with gaps where it cannot be given. An averaging window that does not fit between two additions (or after the last one) is skipped: it is drawn in red with a warning sign, and the terminal lists the files and windows affected so you can check it is OK.
- **Individual experiment plots:** the figure is drawn at once, as it will be saved. One question, *Do you accept this figure?*, either accepts it or names the part to change: oxygen and OCR (and which OCR), which haems in which order, or the angle of the event labels. The haems on or off, how they are shown, the per OD scaling, the journal and the size are changed in the strip, and the figure is redrawn at once. Only that part's questions are asked, then the figure is redrawn and the question asked again.
- **Multi-experiment plots and summaries:** the drop-down lists the individual experiment plots, marked `[locked]` (with a padlock drawn on the plot) because they are final, followed by the figure being built. The time response is built panel by panel: first which time points the waterfalls skip, with the other panels shown as empty boxes ("Kinetic trace 1", "Decomposition 2" ...), then each kinetic trace and decomposition plot as you choose it, each with its own accept question. The haem and OCR response starts with the OCR and the baseline plots, then adds all the haems when you choose how to show them, then redraws as you choose which haems and in what order. The side by side and 2x2 figures are drawn once their questions are answered. Every figure ends with a final accept question. This reads the files again, so it can take a moment. Nothing is written to the results folder until the run starts.
- **Going back:** after the individual plots you can go back to any earlier step. Its questions are asked again with your answers as the defaults, and your answers to the later steps are kept.

The previews use the same processing as the final run, so what is shown is what is saved. When the browser steps are over the file controls switch off and the last picture stays on show; the rest of the run (processing and saving) writes its progress in the terminal on the left. When the run has finished, close the window.

Closing the window while the program is still running stops it (a file that is being written may be left incomplete).

**If the window cannot open.** The window needs Python's tkinter. It is included with the python.org installers for Windows and macOS. On Linux install it with your package manager (for example `sudo apt install python3-tk`), and a display is needed. Portimao needs its window: when it cannot open, the program says why and what to do, and stops without asking anything.

The full list of questions, with where each answer leads, is in [QUESTION_FLOW.md](QUESTION_FLOW.md).

### 2.7 Outputs

Everything goes into the results folder you chose:

| Output | Description |
|---|---|
| `<experiment>/<experiment>.xlsx` and figure files | One workbook and one figure per experiment. If you exported at the end of the import, the workbook is first written then (the trimmed data, your labels, OD values and edges) and the run writes it again with its results added |
| `<experiment>/<spectrometer>_<kind>.csv` | The spectra (transmission, intensity, attenuation), if you chose them at the end of the import or in the data export: wavelengths down, one column per spectrum |
| `<experiment>/full/` | Only for a file you trimmed, if you exported at the end of the import: the same workbook (and spectra, if chosen) for the whole recording |
| `2x2_comparison.*` | Four experiments in a 2x2 grid |
| `ocr_and_haem_response.*` | Baseline OCR bars, OCR response and haem response (`.png`, `.svg`) |
| `ocr_and_haem_response.xlsx` | Run values, averages, SEM and every significance test, written so the maths can be checked by hand |
| `time_response.*` | The 3 x 3 time response figure (`.png`, `.svg`) |
| `time_response.xlsx` | Difference spectra, haem percentages and the waterfall baseline, written so the maths can be checked by hand |
| `logs/YYYY_MM_DD-HH_MM_SS.log` | The version, the questions and your answers (from the results folder question on, kept even if Portimao is closed before the run), the settings, then everything printed during the run |

Both summary figures need a haem fit in `fits/`. File names must carry the information the figure needs: `knockdown_kcn_then_bd_run1` (strain, addition order, run) for the OCR and haem response, and `control_7hours` (group, hours) for the time response. Files whose names do not fit are listed and left out of that figure only.

### 2.8 Finding the haem components from the data (PCA)

Instead of a fit file, the haem decomposition can use components found from your own spectra with a principal component analysis (PCA). In the window, answer *No, find the components from the data* to *Do you accept this decomposition?*; in the fit question (asked when no haems are shown), choose *Find the components from the data (principal component analysis)*, the last in the list of fits. Then:

1. **Spectral window:** the start and end wavelength (nm) the analysis runs over. Choose where the haems you care about absorb (the default is 500 to 630 nm).
2. **The data:** every spectrum of every file is analysed together, after trimming and without the ignored start and end. A flat offset and a 1/wavelength scatter term are taken out of each spectrum first, and each file's average spectrum is removed, so the components describe how the spectra change and differences between preparations do not become components.
3. **Number of components:** you say how many components to find, and exactly that many are made. The question suggests a number (the biggest drop between neighbouring principal components), but this is a rule of thumb, not a proof, so check it against the pictures. Use as few as describe the data; extra ones only fit noise.
4. **Rotation:** optionally rotated (varimax) so each component is as peak-like as possible. This does not change how well the data is described, only the shapes.
5. **Smoothing:** the components carry some of the noise of the data, so they are smoothed (Savitzky-Golay, 4 nm unless you choose another width; 0 for none). This takes out the noise wiggles but keeps the peak positions and real shapes such as shoulders and troughs. Use a width well under the width of the narrowest band.
6. **The pictures:** two pictures are added after the files in the drop-down of the plot window, and go when the next preview is drawn:
    - *PCA components* (shown): each component in a panel of its own, with how much of the change it explains. Each is coloured by the haem type its peaks look like: green for a-like (peaks near 604 or 444 nm), blue for b-like (563 or 430 nm), red for c-like (551 or 418 nm), a darker or lighter shade when a type comes twice, and a colour of its own when a component has peaks of more than one type (*mixed*) or none in a known band. Faint dashed lines mark the usual a, b and c peaks. The type is a guide from the peak positions, not an identification.
    - *PCA examples (smallest and largest residual)*: the spectrum the components describe best and the one they describe worst, each with its file and time, split into what each component and the offset and scatter add, the sum of the fit, and the residual underneath (both residuals on the same scale). This is the same least-squares fit the haem decomposition does with the components.

    Accept, or change the number of components, the window, or choose a fit file instead.
7. **Names and saving:** the components are called PC1, PC2, ... unless you name them; the names suggested follow their type (a-like, b-like, c-like). You can save them as a fit file in `fits/`, ready to be chosen like any other fit in later runs; the fit used for this run is the one found whether or not you save it.

What to keep in mind:

- Principal components are abstract shapes that explain the changes in the spectra. Where haem spectra overlap strongly (the c and b type haems do), a component is usually a mixture of haems, and the analysis cannot tell by itself which haem is which. The fit to the data is still good; what the components mean is for you to decide, for example by comparing their peaks with known haem spectra.
- Each component is scaled so its largest peak is 1, with the sign that makes that peak positive. The "concentrations" from a PCA fit are therefore in arbitrary units, not uM. The delta A values (mOD) are in real absorbance units.
- The components describe changes, so the absolute values of the decomposition include a constant offset. The delta A values remove it.
- It needs spectra that change: with files in which a haem never changes, that haem cannot be found.
- Components found from data carry some of its noise. The haem decomposition fits whole spectra, so a component's noise is multiplied by all the haem in the sample, including the part that never changes; without smoothing that is usually most of the residual in the examples picture. The smoothing removes most of it.
- This has been tested on synthetic spectra only, not on real `.paf` data.

## 3. Project structure

```
Portimao/
    main.py                 entry point
    config.py               defaults, journal sizes and colours
    Portimao.pyw, run.bat, run.sh   launchers (no terminal window)
    install_mac.sh          the Mac install line's script: downloads the Mac app into your own Applications folder
    launchers/              the launcher program, shortcut and icon scripts, the Mac report (mac_report.sh), the Mac app's build recipe (mac_app_builder.py), its start (mac_app_starter.py), its swap for updates (mac_app_swapper.sh) and the move of an old launcher install to the app (mac_app_mover.py)
    .github/ISSUE_TEMPLATE/ the "Mac problem" form of the Issues page
    .github/workflows/      the Mac check: GitHub's Macs run the tests, start Portimao, then build the Mac app and start it; at each release the apps go on the Releases page and the release before is checked to update itself; the newest release is installed as users do (an old launcher install moved, then the install line)
    assets/                 icons
    fits/                   haem fit CSVs (your own fit goes here; layout in DATA_FORMAT.md, "fit csv")
        haems/              the haem library: one haem per file, each the size of one haem
        presets/            the presets, each a list of library files ("preset csv")
    utils_shared/           reading, processing, plotting and export of single experiments
        __init__.py
        paf_reader.py       direct .paf reader
        experiment_processing.py   the processing steps shared by the run and the previews
        output_capture.py   per-thread capture of printed output
        user_places.py      where your own things are kept: the program folder, or ~/Portimao in the Mac app
        app_updater.py      the Mac app's update at each start, from the newest release on GitHub
        app_messages.py     the Mac app's messages: why it could not start (with Copy details), and where to download a newer version
        pca_fitter.py       principal component analysis of the spectra (components, fit file)
        pca_plotter.py      the figures of the components and example decompositions
        ...
    utils_viewer/           the experiment browser (window with the questions and the plots)
        __init__.py
        viewer_gui.py       the browser window: terminal, plot, file selector and arrows
        viewer_strip.py     the settings strip under the plot: haems, fit, background, the decomposition kept to compare, journal, size and the times of the edges
        viewer_edges.py     the edges dragged on the plot (the trimmed and ignored parts)
        viewer_table.py     the tables of the window: OD, volume and dilution per file, label and concentration per event
        viewer_terminal.py  colour codes and the output streams that feed the terminal
        viewer_renderer.py  the thread that draws the previews of every file
        viewer_preview.py   processes and draws one file as a preview
        viewer_stages.py    the trim, processing and plot steps and going back
        viewer_multi.py     previews of the multi-experiment figures
    utils_custom/           the multi-experiment figures and their workbooks
        __init__.py
        ocr_and_haem_response_plotter.py
        time_response_plotter.py
        ...
    tests/                  the tests (test_question_flow.py checks QUESTION_FLOW.md against the code)
    requirements.txt        Python dependencies
    README.md
    FUNCTION_LIST.md
    DATA_FORMAT.md
    QUESTION_FLOW.md        every question the program asks
    MATHS.md                how each haem number is worked out, for checking the maths
    .style/                 this project's style guide settings, its own rules (PROJECT_STYLE.md), the VERSION file,
                            the release hook (release_hook.py) and the make_zip scripts
    .claude/                instructions for Claude (CLAUDE.md imports the style guide)
    style/                  shared style guide (git submodule, see style/rules/CODING_STYLE.md)
```

## 4. Links to other .md files

- [FUNCTION_LIST.md](FUNCTION_LIST.md): every function and class, with its docstring.
- [DATA_FORMAT.md](DATA_FORMAT.md): custom data structures, units and formats.
- [QUESTION_FLOW.md](QUESTION_FLOW.md): every question the program asks, in order, with where each answer leads.
- [MATHS.md](MATHS.md): how each haem number is worked out, with an equation, a worked example and the test that checks it.
- [.style/PROJECT_STYLE.md](.style/PROJECT_STYLE.md): this project's own rules, such as how the question list and the maths document are laid out and kept.
- [style/rules/CODING_STYLE.md](style/rules/CODING_STYLE.md): the coding and formatting standards used in this project.

## 5. License

No licence file has been added yet.
