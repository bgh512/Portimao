# Albufeira

Reads Espana Scientific Software `.paf` files, plots every experiment and the combined figures, and exports Excel workbooks that can be checked by hand.

## 1. Installation

### 1.1 Using GitHub (recommended)

Git and Python 3.9 or newer must be installed first. If they are not, follow the requirements in section 1.2, then return here.

#### Windows

1. Open a terminal: press the Windows key, type `PowerShell` and press Enter.
2. Go to the folder where the project should be installed:

    ```powershell
    cd C:\Users\<username>\Documents
    ```

3. Download the project and enter its folder:

    ```powershell
    git clone https://github.com/bgh512/DePalencify.git
    cd DePalencify
    ```

4. Create and activate a Python environment, then install the dependencies:

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    ```

    If PowerShell refuses to run the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again. The launcher `run.bat` does this step itself, so it can be skipped if only the launcher is used.

#### macOS

1. Open Terminal: press Cmd + Space, type `Terminal` and press Enter. If git is missing, run `xcode-select --install` first.
2. Go to the folder where the project should be installed:

    ```bash
    cd ~/Documents
    ```

3. Download the project and enter its folder:

    ```bash
    git clone https://github.com/bgh512/DePalencify.git
    cd DePalencify
    ```

4. Create and activate a Python environment, then install the dependencies:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

    The launchers `run.command` and `run.sh` do this step themselves, so it can be skipped if only a launcher is used.

#### Linux

1. Open a terminal (Ctrl + Alt + T on most distributions). On Debian or Ubuntu, install the requirements first:

    ```bash
    sudo apt install git python3 python3-venv python3-pip
    ```

2. Go to the folder where the project should be installed:

    ```bash
    cd ~/Documents
    ```

3. Download the project and enter its folder:

    ```bash
    git clone https://github.com/bgh512/DePalencify.git
    cd DePalencify
    ```

4. Create and activate a Python environment, then install the dependencies:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

### 1.2 Manual install

No git is needed.

#### Requirements

- Python 3.9 or newer: <https://www.python.org/downloads/> (on Windows, tick "Add python.exe to PATH" in the installer).

#### Install from the .zip

1. On the project's GitHub page, click **Code**, then **Download ZIP**.
2. Extract the .zip to the desired location.
3. Open a terminal in the extracted folder:
    - Windows: right-click inside the folder and choose **Open in Terminal**.
    - macOS: right-click the folder and choose **New Terminal at Folder**.
    - Linux: right-click inside the folder and choose **Open in Terminal**.
4. Create and activate a Python environment, then install the dependencies:

    Windows (PowerShell):

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    ```

    macOS and Linux:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

### 1.3 Following the dev branch (optional)

The steps above install `main`, the stable version. `dev` has newer changes that are not yet fully tested.

- Installed with git: from inside the project folder run `git checkout dev`, then `git pull`. To go back to the stable version run `git checkout main`.
- Manual install: on the project's GitHub page choose `dev` in the branch drop-down, click **Code**, then **Download ZIP**, and install as in section 1.2.

## 2. Running

### 2.1 From the terminal

Activate the environment first (see section 1), then run:

```bash
python main.py
```

The program has no command-line options. It asks numbered questions in the terminal (Enter accepts the default in square brackets); the answers are remembered for the next run in `last_answers.json`.

### 2.2 Using the launcher

The launchers open Albufeira without leaving a terminal window open.

- Windows: double-click `Albufeira.pyw` (or `run.bat`, whose window closes at once). The first time it also puts an Albufeira icon on your Desktop and in the Start menu; use that from then on.
- macOS: double-click `Albufeira.app`.
- Linux: run `./run.sh`; the first time it adds Albufeira to the applications menu and the Desktop.

A small "Starting Albufeira" window shows what the launcher is doing. The first run creates the program's own Python environment and installs what is needed (a minute or two, needs internet). Each start checks GitHub for updates when the folder is a git clone (and, if the repository was renamed, points the folder at the new address once it answers). If something goes wrong a message box says what, and `logs/launch.log` has the details. Everything the program prints goes to that file when it is started this way.

Windows and macOS may show a "do you trust this software" warning the first time, because the files were downloaded and are not signed. On Windows right-click the downloaded zip, choose Properties, tick *Unblock* and extract it (once); cloning with git avoids the warning. On macOS right-click `Albufeira.app` and choose Open the first time.

### 2.3 Changing the icon

1. Replace `assets/icon.png` with the new icon (a square PNG, ideally 1024 x 1024 pixels).
2. Run `python launchers/make_icons.py` (inside the program's environment, for example `.venv\Scripts\python launchers\make_icons.py` on Windows or `.venv_unix/bin/python launchers/make_icons.py` on Mac and Linux). It makes `assets/icon.ico` (window, taskbar and Windows shortcut) and the Mac icon inside `Albufeira.app`.
3. Delete the file `.shortcut_made_albufeira`, then start Albufeira once, so the Desktop and Start menu shortcuts are made again with the new icon.


### 2.4 The questions

1. **Your files:** the `.paf` folder and the results folder. The plots of the files then appear on the right.
2. **Trimming and ignoring:** TRIM (data that is not imported, plotted or used) and IGNORE (data that is plotted but not used for calculations), each for the start and the end. The four questions (trim start, trim end, ignore start, ignore end) all work the same way: yes/no, how many minutes for ALL the data, then optionally how many minutes for each specific file. Ignore times count from the new 0 after trimming.
3. **Analysis:** decompose the haems (which fit, or components found from your own data, section 2.7), enter the OD values (they are only checked here), average around the events (window, gap), change event labels. Write `ignore` as an event's label to ignore an event that was not an addition.
4. **Individual experiment plots:** how the figure saved for each file looks, one choice at a time: oxygen and OCR, the haems and their order, how the haems are shown and whether they are scaled by OD, the event labels, then the journal and size.
5. **Multi-experiment plots:** two experiments side by side, four experiments in a 2x2 grid.
6. **Experiment summaries:** time response (waterfall time points to skip, two kinetic traces, three decomposition plots), OCR and haem response (OCR, haem form, haems and order).
7. **Data export**, then a summary and the start question.

Every figure asks for its own journal. Answering `None` uses Nature with the default size.

### 2.5 The experiment browser

The program runs in one window. The left side is a text terminal that asks the questions, with a box at the bottom to type your answers in (press Enter to send; the up and down keys recall earlier answers). If you type nothing, the value in [brackets] is used. The right side shows the plots of your files, with **< Prev** and **Next >** buttons and a drop-down list of the files under the plot. The arrows loop round, and Page Up and Page Down do the same from the keyboard. The window and the taskbar show the Albufeira icon (on macOS the Dock icon needs the optional `pyobjc` package).

The plot stays usable while a question waits. You can flick through every file at any time without answering, and the accept questions wait while you look. All files are drawn in the background with the latest answers, so flicking between them is quick. The plot is for looking: it cannot be clicked to change anything.

- **Trimming and ignoring:** the plot shows the raw data, and after every answer the TRIMMED part (grey, hatched) or IGNORED part (amber) is added, so the shading builds up as you answer; for a specific file the plot switches to that file. Answer *Yes, accept* or *No, enter the limits again* (your answers are offered as the defaults).
- **Analysis:** the decomposition, averaging windows and event labels are each drawn for every file and accepted or asked again in the same way. An averaging window that does not fit between two additions (or after the last one) is skipped: it is drawn in red with a warning sign, and the terminal lists the files and windows affected so you can check it is OK. The OD values are listed and checked, but the data is not scaled by OD yet; that is chosen in the individual plots. Questions about one file (OD values, event labels) show that file.
- **Individual experiment plots:** the figure is built up choice by choice. After each of these the plot is redrawn and you accept it or choose again: oxygen and OCR (and which OCR), the haems and their order, how the haems are shown (and whether they are scaled by OD), the event labels, and the journal and size.
- **Multi-experiment plots and summaries:** the drop-down lists the individual experiment plots, marked `[locked]` (with a padlock drawn on the plot) because they are final, followed by the figure being built. The time response is built panel by panel: first which time points the waterfalls skip, with the other panels shown as empty boxes ("Kinetic trace 1", "Decomposition 2" ...), then each kinetic trace and decomposition plot as you choose it, each with its own accept question. The haem and OCR response starts with the OCR and the baseline plots, then adds all the haems when you choose how to show them, then redraws as you choose which haems and in what order. The side by side and 2x2 figures are drawn once their questions are answered. Every figure ends with a final accept question. This reads the files again, so it can take a moment. Nothing is written to the results folder until the run starts.
- **Going back:** after the individual plots you can go back to any earlier step. Its questions are asked again with your answers as the defaults, and your answers to the later steps are kept.

The previews use the same processing as the final run, so what is shown is what is saved. When the browser steps are over the file controls switch off and the last picture stays on show; the rest of the run (processing and saving) writes its progress in the terminal on the left. When the run has finished, close the window.

Closing the window while the program is still running stops it (a file that is being written may be left incomplete).

**If the window cannot open.** The window needs Python's tkinter. It is included with the python.org installers for Windows and macOS. On Linux install it with your package manager (for example `sudo apt install python3-tk`), and a display is needed. When the window cannot open, the program says why and runs in the terminal as before: each preview is saved as a picture (`Albufeira_preview.png` in the temporary folder) and opened in the default picture viewer, and the file is chosen by a question instead of the arrows. To use the terminal on purpose, set the environment variable `ALBUFEIRA_NO_GUI` to any value.

The full list of questions, with where each answer leads, is in [QUESTION_FLOW.md](QUESTION_FLOW.md).

### 2.6 Outputs

Everything goes into the results folder you chose:

| Output | Description |
|---|---|
| `<experiment>/<experiment>.xlsx` and figure files | One workbook and one figure per experiment |
| `2x2_comparison.*` | Four experiments in a 2x2 grid |
| `ocr_and_haem_response.*` | Baseline OCR bars, OCR response and haem response (`.png`, `.svg`) |
| `ocr_and_haem_response.xlsx` | Run values, averages, SEM and every significance test, written so the maths can be checked by hand |
| `time_response.*` | The 3 x 3 time response figure (`.png`, `.svg`) |
| `time_response.xlsx` | Difference spectra, haem percentages and the waterfall baseline, written so the maths can be checked by hand |
| `logs/YYYY_MM_DD-HH_MM_SS.log` | Everything printed during the run, with the version, seed and settings |

Both summary figures need a haem fit in `fits/`. File names must carry the information the figure needs: `knockdown_kcn_then_bd_run1` (strain, addition order, run) for the OCR and haem response, and `control_7hours` (group, hours) for the time response. Files whose names do not fit are listed and left out of that figure only.

### 2.7 Finding the haem components from the data (PCA)

Instead of a fit file, the haem decomposition can use components found from your own spectra with a principal component analysis (PCA). Choose *Find the components from the data (principal component analysis)* in the list of fits. Then:

1. **Spectral window:** the start and end wavelength (nm) the analysis runs over. Choose where the haems you care about absorb (the default is 500 to 630 nm).
2. **The data:** every spectrum of every file is analysed together, after trimming and without the ignored start and end. The offset and scatter terms that the decomposition fits anyway are taken out of each spectrum first, and each file's average spectrum is removed, so the components describe how the spectra change and differences between preparations do not become components.
3. **Number of components:** a table shows how much of the change each principal component explains and how much error (OD) is left with that many; a number is suggested. The suggestion is a rule of thumb (the biggest drop between neighbouring components), not a proof, so check it against the plot. Use as few as describe the data; extra ones only fit noise.
4. **Rotation:** optionally rotated (varimax) so each component is as peak-like as possible. This does not change how well the data is described, only the shapes.
5. **The plot:** the plot window gets a *PCA components* picture after the files in the drop-down: the component spectra, how much each explains, and the error left for each number of components. It goes when the next preview is drawn. Accept, or change the number of components, the window, or choose a fit file instead.
6. **Names and saving:** the components are called PC1, PC2, ... unless you name them. You can save them as a fit file in `fits/`, ready to be chosen like any other fit in later runs; the fit used for this run is the one found whether or not you save it.

What to keep in mind:

- Principal components are abstract shapes that explain the changes in the spectra. Where haem spectra overlap strongly (the c and b type haems do), a component is usually a mixture of haems, and the analysis cannot tell by itself which haem is which. The fit to the data is still good; what the components mean is for you to decide, for example by comparing their peaks with known haem spectra.
- Each component is scaled so its largest peak is 1, with the sign that makes that peak positive. The "concentrations" from a PCA fit are therefore in arbitrary units, not uM. The delta A values (mOD) are in real absorbance units.
- The components describe changes, so the absolute values of the decomposition include a constant offset. The delta A values remove it.
- It needs spectra that change: with files in which a haem never changes, that haem cannot be found.
- This has been tested on synthetic spectra only, not on real `.paf` data.

## 3. Project structure

```
Albufeira/
    make_zip.bat            zips the project for sharing (Windows)
    main.py                 entry point
    config.py               defaults, journal sizes and colours
    Albufeira.pyw, Albufeira.app, run.bat, run.sh   launchers (no terminal window)
    launchers/              the launcher program, shortcut and icon scripts
    assets/                 icons
    fits/                   haem fit CSVs (your own fit goes here)
    utils_shared/           reading, processing, plotting and export of single experiments
        __init__.py
        paf_reader.py       direct .paf reader
        experiment_processing.py   the processing steps shared by the run and the previews
        output_capture.py   per-thread capture of printed output
        pca_fitter.py       principal component analysis of the spectra (components, fit file)
        pca_plotter.py      the figure of the components found
        ...
    utils_viewer/           the experiment browser (window with the questions and the plots)
        __init__.py
        viewer_gui.py       the browser window: terminal, plot, file selector and arrows
        viewer_terminal.py  colour codes and the output streams that feed the terminal
        viewer_renderer.py  the thread that draws the previews of every file
        viewer_window.py    the preview picture used when the window cannot open
        viewer_preview.py   processes and draws one file as a preview
        viewer_stages.py    the trim, analysis and plot steps and going back
        viewer_multi.py     previews of the multi-experiment figures
    utils_custom/           the multi-experiment figures and their workbooks
        __init__.py
        ocr_and_haem_response_plotter.py
        time_response_plotter.py
        ...
    requirements.txt        Python dependencies
    VERSION                 current version
    README.md
    FUNCTION_LIST.md
    DATA_FORMAT.md
    CLAUDE.md               imports the style guide for Claude
    style/                  shared style guide (git submodule, contains CODING_STYLE.md)
```

## 4. Links to other .md files

- [FUNCTION_LIST.md](FUNCTION_LIST.md): every function and class, with its docstring.
- [DATA_FORMAT.md](DATA_FORMAT.md): custom data structures, units and formats.
- [style/CODING_STYLE.md](style/CODING_STYLE.md): the coding and formatting standards used in this project.

## 5. License

No licence file has been added yet.
