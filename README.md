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
- `journals/`: what each journal asks of a figure, one small file per journal, which you can correct or add to (see "Journals" further down).
- Your data folders: a folder of `.paf` files put here is offered as a button at the first question. Any other folder is chosen under Other folder…: type or drag in its path, or click Browse… to pick it.
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

The program has no command-line options. It opens its window and asks numbered questions in the guide on the left of the window, answered with buttons; if the window cannot open, it says why and what to do, and stops. The answers are saved with each dataset, in `portimao_settings.json` inside its data folder, and offered the next time that dataset is opened (a dataset never run starts from the standard settings in `config.py`); `last_answers.json` remembers only the folder used last.

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

The questions are grouped in stages, which the guide on the left of the window names (section 2.6): **Import** (1), **Set-up** (2 and 3), **Experiment processing** (4), **Experiment export** (5), **Dataset figures** (6 and 7) and **Dataset export** (8).

1. **Import:** the `.paf` folder (the data folders in the Portimao folder are buttons: click one, then Continue; another folder is typed or dragged in under Other folder…, or picked with Browse…) and the results folder (the folders inside the data folder are buttons, with what each holds). For a dataset opened before, you then choose whether to load its previous processing: No starts it fresh, as a dataset never opened (what was saved with it is replaced only when the run starts). A name typed without a path (`quadratic_scatter_results`) is made inside the data folder, and a folder that already holds results of these files is used only once you agree to write over them, so a second set of results can go beside the first. The plots of the files then appear on the right. As the folder is read, the instrument's OCR of each file is checked against our own calculation from its oxygen traces. A file whose numbers do not agree gets a warning naming the part that differs, and its figures still use the instrument's OCR (how the check works is in `DATA_FORMAT.md`, under "Our OCR check").
2. **Import, trimming and ignoring:** TRIM (orange: data not plotted or used for calculations) and IGNORED (grey: data plotted but not used for calculations), each for the start and the end. Drag the four bars on the plot, or type their times under Trim / Ignore in the Time regions box above it, check each experiment, then press Continue. **Export trimmed csv** and **Export full + trimmed csv** are the quick export: the spectra of each file as csv files, of the trimmed data, or of the trimmed data and the whole recording, with their size said first. Continue skips it, and Portimao can be closed once it has written the files. Ignore times count from the trimmed edges, and the edges stay movable at any later step with the Trim / Ignore tab, which keeps both export buttons to write the files again.
3. **Set-up, temperature, OD values and event labels:** type the temperature of the runs, then, if you want to give OD values, fill them in in a table, one row per file (once every value is in, the OCR is shown per OD and the View box offers per OD for the haems and the OCR; with cells left empty, a warning names them and the OD scaling stays off until **Edit ODs** fills them in; **Edit ODs** gives them at any time, even after No), then the volume added (µL), the stock (mM) and the chemical of each event in a second table, one row per event, filled in to start with from the text the instrument saved with the event (`1ul 8mm nd-011992`): the concentration in the chamber (µM) is worked out (the same thing added again adding up), and **Labels as** in the View box shows it on the plot as `400 µM KCN` or `10 µL of 200 mM KCN`. Type `IGNORE` as an event's label to leave out an event that was not an addition. Confirm only confirms; going to another step keeps the table as you left it. The labels are then saved, and **Edit labels** in the View box changes them at any time. This ends the set-up.
4. **Experiment processing:** accept the haems shown, or find components from your own data instead (section 2.8); another fit, or no haems, is chosen in the Haem decomposition box above the plot (section 2.6); then the oxidised and reduced regions, Δψ, and the averaging regions, shaded on the plot before each addition: pull the start of any averaging region to change how long they are, its end to change how long before the next addition they end (the end of the last one, how long before the end of the file it ends), or type both in seconds under Averaging in the Time regions box; untick **Averaging regions** there for none. Tick **Adjust region manually** and pick a region with the buttons beside it to change that region of that file alone, untick a number under **Use** to leave that region out, and change a file with **Apply to all** unticked to give it regions of its own.
5. **Experiment export, finalise figures and export:** the figure saved for each file is drawn with the oxygen, the OCR and, while Haem decomposition is ticked, every haem of the fit. Change it in the boxes above the plot (how the OCR, the haems and the labels are shown, the angle of the labels, the journal and the size; the order of the panels with the arrows beside them), then click **Export**. Choose what to export: the summary (the plot and the workbook of each file), the summary and the trimmed csv files, or the summary and the trimmed and full csv files (the spectra of the whole recording of each trimmed file). They are saved in the results folder.
6. **Dataset figures, set-up:** a table says which experiment is which, one row per experiment: whether it is used, its Group 1 and Group 2 (you name the two columns, for example strain and order of additions), its time point and its replicate number. It is filled in from the file names (`control-bd_then_kcn-run2` is control, BD → KCN, run 2; `knockdown_24hours` is knockdown at 24 h): type over what is wrong, pick a label already used from the list of a cell, or click a cell and Shift-click another of its column to fill the rows between. Cells may stay blank. The replicates are numbered for you, and each Group 1 label has a colour (click its square to change it) that every panel of the dataset figures uses. The table is saved with the dataset.
7. **Dataset figures, build a figure:** the figure of the whole dataset is laid out on a journal page at its printed size: pick a plot type, drag across the grid to place it, and save the layout as a template to load for another dataset. A Standard experiment is the plot of one experiment (you tick its panels and pick how the haems are shown), and the standard plots of a page share their scales unless you untick that. A plot type that is not built yet is a grey box with its name for now, and a Space for a drawing stays empty under its letter. Under the page, what each colour and line style on it means is written out, with a Copy button, to paste into the caption. Three ready-made templates in the `layouts/` folder are in the list beside Load template (**Time response**, **Haem and OCR response**, **Two standard experiments**). A ready-made template puts the plots in their places; a plot of one experiment then says "No experiment is picked for this plot yet", and you pick its experiment in its form (✎).
8. **Dataset export:** a summary and the start question.

The plots of the dataset figure that show numbers per region use the averaging regions of the processing and never ask for their own.

The figure of each file takes its journal and size from the Figure box, and the dataset figure from the strip above its page. `None` uses Nature with the default size.

**Journals.** Choosing a journal makes the figure follow what that journal asks, with nothing to set by hand: the widths offered, the tallest figure, the size of every text, the panel letters, the font, the thickness of every line (thickened to the journal's thinnest line, thinned to its thickest) and the sharpness of saved pictures. The file type and the colour rules of a journal are not covered.

Each journal is one small file in the `journals/` folder (`nature.json`, `science.json`, `cell.json`, `pnas.json`, `plos_one.json`, `acs.json`), which you can open in Notepad or TextEdit. Each line is the name of a thing and then its value; `read_at`, `confirmed` and `notes` say where the numbers were read and which were confirmed by hand. To correct a journal, change its number and open Portimao again. To add a journal, copy one of the files, give it the journal's name and fill in its numbers (the layout is in `DATA_FORMAT.md`, under "journal file"). A file with a missing or impossible number is left out, and one line says which and why when Portimao starts.

**Export master.** The button beside the Height box saves one page of the chosen journal as a PDF in the results folder (`<file>_master_<journal>.pdf`): the figure of the file shown at its printed size, a box where its legend goes and grey lines where the text of the paper goes, so you can see whether the figure looks sensible in print. It works in the individual experiment plots, where that figure is on the plot. A journal whose page size is not in its file is shown on an A4 page, and the page says so.

### 2.6 The experiment browser

The program runs in one window. The left side is the **guide**: the steps, numbered, one line each, under the names of the stages (Import, Set-up, Experiment processing, Experiment export, Dataset figures, Dataset export). The stage you are in lists its steps; the others show their name only, with a tick once passed. The step open sits under its line: what was said since your last answer, in grey, then the question, larger, then its answers as buttons: one big **Continue** for something done on the plot or in the boxes above it; **Yes** and **No**; a button for each choice; tick buttons and Continue for several choices; a box only for a number or a name (it starts with the default; Enter sends it, and the up and down keys recall earlier answers). Enter gives the highlighted button. What was said before your last answer folds away at the next question, and stays in the run's log. A change in the boxes that belongs to an earlier step (the fit while at Δψ, or the Trim / Ignore tab) opens that step, marks the step you were at with "you were here", and gives a **Back to** button to return to it; a click on the line of a step done does the same. A change that belongs to a later step ticks that step: the steps can be done in any order. Under the answers is a **Help** button, greyed out for now; after an answer that cannot be used, one red line says what to type and the question waits. The right side shows the plots of your files, with **< Prev** and **Next >** buttons and a drop-down list of the files above the plot. The arrows loop round, and Page Up and Page Down do the same from the keyboard. The window and the taskbar show the Portimao icon (on macOS the Dock icon needs the optional `pyobjc` package).

Under a box for a name, and under a table, is a row of **Symbols** (µ, superscript and subscript digits such as ⁻¹ and ₂, ±, °, Δ, Greek letters and more): click one to type it at the cursor, or in the cell of a table last typed in, for example for event labels like `8 µg mL⁻¹`. The plot stays usable while a question waits. You can flick through every file at any time without answering, and the accept questions wait while you look. All files are drawn in the background with the latest answers, so flicking between them is quick. The plot can also answer some questions, and the hint under the answers says when: the trimmed and ignored parts, the oxidised and reduced regions and the averaging regions are chosen by dragging their edges (an edge of an averaging region moves in whole steps of 5 s). You can always type instead.

Above the plot, under the file name and its arrows, are five **boxes** in one row. **Time regions**: the tabs **Trim / Ignore**, **Ox / Red** and **Averaging**, each putting its edges on the plot to drag, with their numbers in the box to type; the guide presses the tab of its step, and you can press any tab at any time (the change is used when you press another tab or answer the question). **View**: **OCR as** (µM min⁻¹, % of the range, or % of baseline once the averaging regions are set up) and **Haems as** (ΔD, % oxidised once a file has both regions, or absorbance), each with its **per OD** box once the OD values of every file are entered, **Labels as**, the **Label angle**, and the **Edit ODs** and **Edit labels** buttons. **Haem decomposition**, ticked when the haems are worked out and shown: the **Fit**, the **Scatter** (the background fitted under the haems), **Spectra** (the spectrometer whose spectra hold the haems, shown when your files share more than one), **Build a fit** (a tick for each haem of the library, on lines a, b and c, and **Save fit** to keep the haems ticked as a fit of your own under the name typed beside it) and **Keep to compare**. **Δψ**, ticked when Δψ is worked out, with its numbers (*b*<sub>H</sub>, *b*<sub>L</sub>, the shift, and **More options**). **Figure**: the **Journal**, the **Width** and the **Height** of the figure of each file, the **Export master** button and the **Standard order** button. Every question that sets one of these says so, and it can be changed there at any time. While the boxes can be used, a small up and a down arrow sit left of each panel of the plot of a file: a click moves that panel one place, on every file and on the figure saved for each, and **Standard order** puts the panels back (oxygen, OCR, the haems a then b then c, Δψ). The order is kept with the dataset. From the trimming to the individual plots you can change it whenever a question waits: the plot is redrawn at once and the run uses the change. Unticking Haem decomposition leaves the haems out of the run; ticking it, or picking a fit, works them out with that fit. The journal and size show in the individual plots, the only plots drawn at the figure's size. The boxes are greyed out when they cannot be used: while you choose the folder, while components are found from your data, and from the dataset figures on. While the program makes a picture of its own (the components), and while a file is read, a plot redrawn or an answer still being worked on, the **Plotting data …** sign is on the plot: a large spinning wheel on a yellow card in its middle.

- **Trimming and ignoring:** the plot shows the whole recording of each file with four edges: the trimmed start and end (orange; the part trimmed away orange and hatched) and the ignored start and end (grey, as the ignored parts are on every later plot). Drag an edge by its handle above the plot or by its line; the shading follows at once and the minutes show by the handle. A trimmed edge stops at the first or last event, so no addition is cut away. The Time regions box shows the four edges of the file shown as times on its whole recording (trim before and after, then ignore before and after, on a line each) to type exact times, and **Apply to all**: unticked at first, so a change applies only to the file shown, which is then marked *(own times)* in the drop-down; ticking it copies the times of the file shown to every file once (the same minutes from each file's own start or end), and it unticks itself when the next file is shown. The Ox / Red and Averaging tabs have the same tick. Press Continue when every experiment looks right. When you change them again later, the limits from before stay on the plot as red dashed lines.
- **OD values and event labels:** each is filled in in a table that takes most of the step open, with a few lines of text above it: click a cell and type (Tab moves across, Enter moves down), then press **Confirm** under it. The OD table has one row per file, with the values stored for each file already in; once they are entered, the per OD boxes of the View box say whether the haems and the OCR are scaled by them, and **Edit ODs** opens the table again later (as **Edit labels** does for the labels). The labels table has one row per event, under its file's name, with the time, the label and the final concentration (µM). A cell that cannot be used turns red, and Confirm then names the cells still wrong or empty and the table stays. Clicking a cell of a file shows that file on the plot. The event labels are then drawn for every file and accepted, or the table opens again.
- **Processing:** the decomposition is drawn for every file with the spectra, scatter and fit set in the Haem decomposition box (the **ⓘ** beside Scatter shows its formula); press Continue when the haems look right. In ΔD and in absorbance the haem panels share one scale, so a haem that hardly changes looks small beside the others. To compare two decompositions, press **Keep to compare** in that box, then change the fit, the haems, the background, the oxidised and reduced regions or the numbers of Δψ: the kept one stays on the screen, either as a plot of its own headed Old on the left of the plot in use, headed New (**Side by side**, at first), or as faint, thin lines in the same colours under the haems and Δψ in use, drawn bold (**Overlaid**), with the switch beside **Keep new** to change between the two; under the plot each haem, and Δψ, has the largest and the average distance between its two traces. Then choose one of the two with the buttons under it, which takes them away: **Keep new** carries on with what is on the plot, **Keep old** puts the kept one back in use. Each file takes about twice as long to draw meanwhile. Once a file has an oxidised and a reduced region, and the fit has one bH and one bL, you are asked whether to work out Δψ (and can tick or untick it in its box later), the membrane potential: it is drawn as a panel of each such file (the lowest, unless you move it), at the temperature you gave in the import, with gaps where it cannot be given. An averaging region that does not fit between two additions (or after the last one) is skipped: it is drawn in red with a warning sign, and the terminal lists the files and regions affected so you can check it is OK.
- **Individual experiment plots:** the figure is drawn at once, as it will be saved, with the oxygen, the OCR and (while Haem decomposition is ticked) every haem of the fit. Change it in the boxes above the plot (the haems on or off, how they and the OCR are shown, the angle of the labels, the journal and the size), and it is redrawn at once; click Continue when it looks right.
- **Going back:** until you choose what to export, click the line of an earlier step in the guide, or change it in the boxes above the plot; **Back to** takes you to the question that waits.

The previews use the same processing as the final run, so what is shown is what is saved. When the browser steps are over the plot of every file is saved in the results folder straight away, and the later steps show each file's saved plot (the plots stay there if you cancel afterwards; the run draws one again only when a later answer changed the haem fit); the rest of the run (processing and saving) writes its progress in the guide on the left. When the run has finished, close the window.

Closing the window while the program is still running stops it (a file that is being written may be left incomplete).

**If the window cannot open.** The window needs Python's tkinter. It is included with the python.org installers for Windows and macOS. On Linux install it with your package manager (for example `sudo apt install python3-tk`), and a display is needed. Portimao needs its window: when it cannot open, the program says why and what to do, and stops without asking anything.

The full list of questions, with where each answer leads, is in [QUESTION_FLOW.md](QUESTION_FLOW.md).

### 2.7 Outputs

Everything goes into the results folder you chose:

| Output | Description |
|---|---|
| `<experiment>/<experiment>.xlsx` and figure files | One workbook and one figure per experiment, written once its processing and figure are accepted (the experiment export). If you used an export button in the trimming step, the workbook is first written then (the trimmed data, your labels, OD values and edges) and the experiment export writes it again with its results added |
| `<experiment>/<spectrometer>_<kind>.csv` | The spectra (transmission, intensity, attenuation), if you chose them with an export button of the trimming step or in the experiment export: wavelengths down, one column per spectrum |
| `<experiment>/full/` | Only for a file you trimmed, if you exported with Export full + trimmed csv: the same workbook (and spectra, if chosen) for the whole recording |
| `dataset_figure_<journal>.pdf` | The dataset figure built on the page in Build a figure, at exactly its printed size, with text you can still change in a drawing program (the fonts are in the file). Written when the page holds at least one plot |
| `dataset_figure_master_<journal>.pdf` | The same figure on one page of the journal, with a box where its legend goes and grey lines where the text of the paper goes, as for Export master |
| `logs/YYYY_MM_DD-HH_MM_SS.log` | The version, the questions and your answers (from the results folder question on, kept even if Portimao is closed before the run), the settings, then everything printed during the run |

### 2.8 Finding the haem components from the data (PCA)

Instead of a fit file, the haem decomposition can use components found from your own spectra with a principal component analysis (PCA). In the window, click **Do PCA** in the Haem decomposition box while the haem step (4.1) waits: all the spectra of all the files are analysed together, so the components are one set for the whole dataset. Then:

1. **Spectral range:** the start and end wavelength (nm) the analysis runs over. Choose where the haems you care about absorb (the default is 500 to 630 nm).
2. **The data:** every spectrum of every file is analysed together, after trimming and without the ignored start and end. A flat offset and a 1/wavelength scatter term are taken out of each spectrum first, and each file's average spectrum is removed, so the components describe how the spectra change and differences between preparations do not become components.
3. **Number of components:** you say how many components to find, and exactly that many are made. The question suggests a number (the biggest drop between neighbouring principal components), but this is a rule of thumb, not a proof, so check it against the pictures. Use as few as describe the data; extra ones only fit noise.
4. **Rotation:** optionally rotated (varimax) so each component is as peak-like as possible. This does not change how well the data is described, only the shapes.
5. **Smoothing:** the components carry some of the noise of the data, so they are smoothed (Savitzky-Golay, 4 nm unless you choose another width; 0 for none). This takes out the noise wiggles but keeps the peak positions and real shapes such as shoulders and troughs. Use a width well under the width of the narrowest band.
6. **The pictures:** two pictures are added after the files in the drop-down of the plot window, and go when the next preview is drawn:
    - *PCA components* (shown): each component in a panel of its own, with how much of the change it explains. Each is coloured by the haem type its peaks look like: green for a-like (peaks near 604 or 444 nm), blue for b-like (563 or 430 nm), red for c-like (551 or 418 nm), a darker or lighter shade when a type comes twice, and a colour of its own when a component has peaks of more than one type (*mixed*) or none in a known band. Faint dashed lines mark the usual a, b and c peaks. The type is a guide from the peak positions, not an identification.
    - *PCA examples (smallest and largest residual)*: the spectrum the components describe best and the one they describe worst, each with its file and time, split into what each component and the offset and scatter add, the sum of the fit, and the residual underneath (both residuals on the same scale). This is the same least-squares fit the haem decomposition does with the components.

    Accept, or change the number of components, the spectral range, or choose a fit file instead.
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
    config.py               defaults and colours; reads the journals folder
    journals/               what each journal asks of a figure, one .json file per journal (layout in DATA_FORMAT.md, "journal file")
    layouts/                the templates of the dataset figures, one .json file each: the three ready-made ones, and those you save
    Portimao.pyw, run.bat, run.sh   launchers (no terminal window)
    install_mac.sh          the Mac install line's script: downloads the Mac app into your own Applications folder
    launchers/              the launcher program, shortcut and icon scripts, the Mac report (mac_report.sh), the Mac app's build recipe (mac_app_builder.py), its start (mac_app_starter.py), its swap for updates (mac_app_swapper.sh) and the move of an old launcher install to the app (mac_app_mover.py)
    .github/ISSUE_TEMPLATE/ the "Mac problem" form of the Issues page
    .github/workflows/      the Mac check: GitHub's Macs run the tests, start Portimao, then build the Mac app and start it; at each release the apps go on the Releases page and the release before is checked to update itself; the newest release is installed as users do (an old launcher install moved, then the install line)
    assets/                 icons
    fits/                   haem fit CSVs (your own fit goes here; layout in DATA_FORMAT.md, "fit csv")
        haems/              the haem library: one haem per file, each the size of one haem
        presets/            the presets, each a list of library files ("preset csv")
    utils_shared/           reading, processing, plotting and export of single experiments, and the dataset figure
        __init__.py
        paf_reader.py       direct .paf reader
        experiment_processing.py   the processing steps shared by the run and the previews
        output_capture.py   per-thread capture of printed output
        user_places.py      where your own things are kept: the program folder, or ~/Portimao in the Mac app
        journal_files.py    reads the journals folder, and fits saved answers to the journals there are
        master_page_exporter.py   the master page: a journal page as a PDF with the figure on it
        app_updater.py      the Mac app's update at each start, from the newest release on GitHub
        app_messages.py     the Mac app's messages: why it could not start (with Copy details), and where to download a newer version
        pca_fitter.py       principal component analysis of the spectra (components, fit file)
        pca_plotter.py      the figures of the components and example decompositions
        ...
    utils_viewer/           the experiment browser (window with the questions and the plots)
        __init__.py
        viewer_gui.py       the browser window: guide, plot, file selector and arrows
        viewer_guide.py     the guide on the left: its steps, the step open, the answer buttons
        viewer_strip.py     the five boxes above the plot: Time regions, View, Haem decomposition, Δψ and Figure
        viewer_edges.py     the edges dragged on the plot (the trimmed and ignored parts)
        viewer_table.py     the tables of the window: OD, volume and dilution per file, label, stock and volume added per event
        viewer_terminal.py  colour codes and the output streams that feed the terminal
        viewer_renderer.py  the thread that draws the previews of every file
        viewer_preview.py   processes and draws one file as a preview
        viewer_stages.py    the trim, processing and plot steps and going back
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
