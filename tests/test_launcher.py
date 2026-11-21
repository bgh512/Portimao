"""
Tests the launcher: a changed package list installs the packages again, a failed install
never breaks a working one, and a copy that cannot update says why.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import importlib.machinery
import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = ROOT / 'launchers' / 'bootstrap.pyw'
PACKAGES = 'numpy\npandas\n'
NEWER_PACKAGES = 'numpy\npandas\nscipy>=1.10\n'
PIP_TEXT = 'ERROR: No matching distribution found for scipy>=1.10'
# what git answers, by its command, when GitHub has a newer commit and it installs
GIT_ANSWERS = {'rev-parse': (0, 'origin/main\n'),
               'ls-remote': (0, 'abc123\trefs/heads/main\n'),
               'merge-base': (1, ''),
               'fetch': (0, ''),
               'rev-list': (0, '2\n'),
               'pull': (0, ''),
               'status': (0, ''),
               }


# ---- HELPERS -------------------------------------------------------------------------


# ---- _git_stand_in_maker -------------------------------------------------------------
def _git_stand_in_maker(tmp_path: Path,
                        monkeypatch: pytest.MonkeyPatch,
                        changes: Dict[str, Tuple[int, str]],
                        ) -> ModuleType:
    """
    ---- Summary ----
    Helper function to load the launcher in a made-up git copy, with GitHub reachable
    and git stood in: it answers as GIT_ANSWERS says, except where changes says
    otherwise.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest; it becomes the git copy.
    monkeypatch : pytest.MonkeyPatch
        Says git is installed, and that this start is not the one after an update.
    changes : Dict[str, Tuple[int, str]]
        {git command: (return code, output)} in place of GIT_ANSWERS.

    ---- Globals read ----
    GIT_ANSWERS (module constant).

    ---- Outputs ----
    ModuleType
        The launcher.

    ---- Globals mutated ----
    None. Makes the .git folder (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _launcher_loader
    """

    launcher = _launcher_loader()
    (tmp_path / '.git').mkdir(parents=True)
    launcher.ROOT = tmp_path
    launcher._github_knocker = lambda: True
    monkeypatch.setattr(launcher.shutil, 'which', lambda name: f'/usr/bin/{name}')
    monkeypatch.delenv('PORTIMAO_UPDATED', raising=False)
    answers = dict(GIT_ANSWERS, **changes)

    def runner(command: List[str],
               timeout: Optional[float] = None,
               ) -> subprocess.CompletedProcess:
        code, text = answers[command[1]]
        return subprocess.CompletedProcess(command, code, text, '')

    launcher._command_runner = runner
    return launcher


# ---- _launcher_loader ----------------------------------------------------------------
def _launcher_loader() -> ModuleType:
    """
    ---- Summary ----
    Helper function to load a fresh copy of the launcher from its file, which Python
    does not import by name (it ends in .pyw).

    ---- Inputs ----
    None.

    ---- Globals read ----
    LAUNCHER (module constant).

    ---- Outputs ----
    ModuleType
        The launcher; its start (main) is not run.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    loader = importlib.machinery.SourceFileLoader('launcher_under_test', str(LAUNCHER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    launcher = importlib.util.module_from_spec(spec)
    loader.exec_module(launcher)
    return launcher


# ---- _stand_in_maker -----------------------------------------------------------------
def _stand_in_maker(tmp_path: Path) -> Tuple[ModuleType, List[str], Dict[str, bool]]:
    """
    ---- Summary ----
    Helper function to load the launcher with its environment and package list in an
    empty folder, and with pip and the check that the packages load stood in.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    PACKAGES, PIP_TEXT (module constants).

    ---- Outputs ----
    Tuple[ModuleType, List[str], Dict[str, bool]]
        (the launcher; the stand-ins run, in order, each 'pip' or 'imports'; whether
        each stand-in works, {'pip': ..., 'imports': ...}, which a test may change).

    ---- Globals mutated ----
    None. Writes the made-up environment and package list (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _launcher_loader
    """

    launcher = _launcher_loader()
    environment = tmp_path / 'environment'
    python = environment / 'python'
    python.parent.mkdir(parents=True)
    python.write_text('', encoding='utf-8')
    requirements = tmp_path / 'requirements.txt'
    requirements.write_text(PACKAGES, encoding='utf-8')
    launcher.ENVIRONMENT = environment
    launcher.ENVIRONMENT_PYTHON = python
    launcher.PACKAGE_STAMP = environment / '.complete'
    launcher.REQUIREMENTS = requirements
    launcher.LOG_FILE = tmp_path / 'launch.log'
    launcher._tk_version_getter = lambda python: 8.6
    run: List[str] = []
    works = {'pip': True, 'imports': True}

    def runner(command: List[str],
               timeout: Optional[float] = None,
               ) -> subprocess.CompletedProcess:
        kind = 'pip' if 'pip' in command else 'imports'
        run.append(kind)
        return subprocess.CompletedProcess(command,
                                           0 if works[kind] else 1,
                                           '',
                                           PIP_TEXT if kind == 'pip' else '',
                                           )

    launcher._command_runner = runner
    return launcher, run, works


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_changed_package_list_is_installed ------------------------------------------
def test_changed_package_list_is_installed(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the packages are installed the first time, only
    checked at a start with the same list, and installed again when the list changes,
    as after an update; an environment made before the fingerprint was kept gets them
    installed once.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    NEWER_PACKAGES (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _stand_in_maker
    environment_builder
    """

    launcher, run, _ = _stand_in_maker(tmp_path)
    stamp = launcher.PACKAGE_STAMP
    launcher.environment_builder(lambda text: None)
    assert run == ['pip']
    first = stamp.read_text(encoding='utf-8')
    assert first == launcher._package_list_stamper(launcher.REQUIREMENTS)
    launcher.environment_builder(lambda text: None)
    assert run == ['pip', 'imports']
    launcher.REQUIREMENTS.write_text(NEWER_PACKAGES, encoding='utf-8')
    launcher.environment_builder(lambda text: None)
    assert run == ['pip', 'imports', 'pip']
    assert stamp.read_text(encoding='utf-8') not in ('', first)
    stamp.write_text('ok', encoding='utf-8')
    launcher.environment_builder(lambda text: None)
    assert run[-1] == 'pip'


# ---- test_failed_install_stops_with_a_plain_message ----------------------------------
def test_failed_install_stops_with_a_plain_message(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that when the packages cannot be installed and none load,
    the launcher stops with one plain sentence and keeps pip's text for the log; a
    first install that failed leaves no half-made environment.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    PIP_TEXT (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _stand_in_maker
    environment_builder
    """

    launcher, _, works = _stand_in_maker(tmp_path)
    works['pip'] = False
    works['imports'] = False
    with pytest.raises(launcher.LaunchProblemError) as problem:
        launcher.environment_builder(lambda text: None)
    assert 'could not download the packages it needs' in str(problem.value)
    assert PIP_TEXT not in str(problem.value)
    assert PIP_TEXT in launcher.LOG_FILE.read_text(encoding='utf-8')
    assert not launcher.ENVIRONMENT.exists()


# ---- test_failed_update_keeps_working_packages ---------------------------------------
def test_failed_update_keeps_working_packages(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that when the list has changed but the packages cannot be
    installed (no internet), Portimao opens with the packages it has, and the next
    start tries again.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    NEWER_PACKAGES (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _stand_in_maker
    environment_builder
    """

    launcher, run, works = _stand_in_maker(tmp_path)
    stamp = launcher.PACKAGE_STAMP
    launcher.environment_builder(lambda text: None)
    first = stamp.read_text(encoding='utf-8')
    launcher.REQUIREMENTS.write_text(NEWER_PACKAGES, encoding='utf-8')
    works['pip'] = False
    shown: List[str] = []
    launcher.environment_builder(shown.append)
    assert 'could not be updated' in shown[-1]
    assert stamp.read_text(encoding='utf-8') == first
    assert launcher.ENVIRONMENT.exists()
    works['pip'] = True
    launcher.environment_builder(lambda text: None)
    assert run[-1] == 'pip'
    assert stamp.read_text(encoding='utf-8') != first


# ---- test_package_fingerprint_ignores_line_endings -----------------------------------
def test_package_fingerprint_ignores_line_endings(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the package list gives the same fingerprint with
    Windows line endings, a different one when a package changes, and none when it
    cannot be read.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    NEWER_PACKAGES, PACKAGES (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _launcher_loader
    _package_list_stamper
    """

    launcher = _launcher_loader()
    plain = tmp_path / 'plain.txt'
    plain.write_bytes(PACKAGES.encode('utf-8'))
    windows = tmp_path / 'windows.txt'
    windows.write_bytes(PACKAGES.replace('\n', '\r\n').encode('utf-8'))
    newer = tmp_path / 'newer.txt'
    newer.write_bytes(NEWER_PACKAGES.encode('utf-8'))
    fingerprint = launcher._package_list_stamper(plain)
    assert len(fingerprint) == 64
    assert launcher._package_list_stamper(windows) == fingerprint
    assert launcher._package_list_stamper(newer) != fingerprint
    assert launcher._package_list_stamper(tmp_path / 'missing.txt') == ''


# ---- test_update_note_reaches_portimao -----------------------------------------------
def test_update_note_reaches_portimao(tmp_path: Path,
                                      monkeypatch: pytest.MonkeyPatch,
                                      ) -> None:
    """
    ---- Summary ----
    Main function to check that Portimao is told why its copy cannot update, and told
    nothing when it can, and that its output goes to the launch log after the start
    before.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Stands in for starting Portimao, and sets a note left from before.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _launcher_loader
    program_starter
    """

    launcher = _launcher_loader()
    launcher.LOG_FILE = tmp_path / 'logs' / 'launch.log'
    launcher.OPENED_FILE = tmp_path / 'logs' / 'window_opened'
    started: List[Dict[str, Any]] = []

    def starter(command: List[str], **options: Any) -> None:
        options['stdout'].close()
        started.append(options['env'])

    monkeypatch.setattr(launcher.subprocess, 'Popen', starter)
    monkeypatch.setenv(launcher.UPDATE_NOTE_SWITCH, 'a note left from before')
    launcher.program_starter('This copy cannot update itself.')
    launcher.program_starter()
    switch = launcher.UPDATE_NOTE_SWITCH
    assert started[0][switch] == 'This copy cannot update itself.'
    assert switch not in started[1]
    log = launcher.LOG_FILE.read_text(encoding='utf-8')
    assert log.count('==== Portimao started') == 2


# ---- test_update_reasons_are_given ---------------------------------------------------
@pytest.mark.parametrize(('changes', 'expected'),
                         [({}, (True, [])),
                          ({'merge-base': (0, '')}, (False, [])),
                          ({'rev-parse': (128, '')},
                           (False, ['follows no branch on GitHub']),
                           ),
                          ({'pull': (1, ''), 'status': (0, ' M config.py\n')},
                           (False,
                            ['(changed here: config.py)',
                             'put that file back as it was',
                             ],
                            ),
                           ),
                          ({'pull': (1, ''),
                            'status': (0, ' M a.py\n M b.py\n M c.py\n M d.py\n'),
                            },
                           (False,
                            ['a.py, b.py, c.py and 1 more',
                             'put those files back as they were',
                             ],
                            ),
                           ),
                          ({'pull': (1, '')}, (False, ['changes of its own'])),
                          ],
                         )
def test_update_reasons_are_given(tmp_path: Path,
                                  monkeypatch: pytest.MonkeyPatch,
                                  changes: Dict[str, Tuple[int, str]],
                                  expected: Tuple[bool, List[str]],
                                  ) -> None:
    """
    ---- Summary ----
    Main function to check what the update check gives in a git copy: an update
    installed, nothing newer, or no update with the reason and what to do.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Stands in for git.
    changes : Dict[str, Tuple[int, str]]
        What git answers differently from an update that installs.
    expected : Tuple[bool, List[str]]
        (whether the update was installed, the words the reason must hold; none for
        no reason).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _git_stand_in_maker
    update_checker
    """

    launcher = _git_stand_in_maker(tmp_path, monkeypatch, changes)
    is_updated, note = launcher.update_checker()
    assert is_updated is expected[0]
    assert all(words in note for words in expected[1])
    assert bool(note) == bool(expected[1])


# ---- test_update_reasons_without_git -------------------------------------------------
def test_update_reasons_without_git(tmp_path: Path,
                                    monkeypatch: pytest.MonkeyPatch,
                                    ) -> None:
    """
    ---- Summary ----
    Main function to check that a git copy on a computer without git says so, and that
    a copy from a zip gives no reason here (Portimao says it itself).

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Says git is not installed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _git_stand_in_maker
    _launcher_loader
    update_checker
    """

    launcher = _git_stand_in_maker(tmp_path / 'git copy', monkeypatch, {})
    monkeypatch.setattr(launcher.shutil, 'which', lambda name: None)
    assert launcher.update_checker() == (False, launcher.NO_GIT_NOTE)
    from_zip = _launcher_loader()
    from_zip.ROOT = tmp_path / 'zip copy'
    assert from_zip.update_checker() == (False, '')
