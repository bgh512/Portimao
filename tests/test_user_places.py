"""
Tests that the user's own things are kept in the program folder from source and in the
home folder in the Mac app.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.user_places import (user_folder_preparer,
                                      user_places_finder,
                                      UserPlaces,
                                      )


# ---- CONSTANTS -----------------------------------------------------------------------
SHIPPED_FITS = {'standard.csv': 'shipped standard', 'other.csv': 'shipped other'}


# ---- HELPERS -------------------------------------------------------------------------


# ---- _app_places_maker ---------------------------------------------------------------
def _app_places_maker(tmp_path: Path) -> UserPlaces:
    """
    ---- Summary ----
    Helper function to make a pretend app (its program folder holding two fits) and a
    pretend home folder, and give the app's places.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    SHIPPED_FITS (module constant).

    ---- Outputs ----
    UserPlaces
        The places of the app, with its own folder in the pretend home folder.

    ---- Globals mutated ----
    None. Writes the folders and fits (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    user_places_finder
    """

    program_folder = tmp_path / 'inside_the_app'
    (program_folder / 'fits').mkdir(parents=True)
    for name, text in SHIPPED_FITS.items():
        (program_folder / 'fits' / name).write_text(text)
    (tmp_path / 'home').mkdir()
    return user_places_finder(is_app=True,
                              home=tmp_path / 'home',
                              program_folder=program_folder,
                              )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_app_keeps_things_in_home_folder --------------------------------------------
def test_app_keeps_things_in_home_folder(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the app keeps the fits, the folder used last and the
    logs in a Portimao folder in the home folder, and reads its own files from inside
    the app.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_places_maker
    """

    places = _app_places_maker(tmp_path)
    own = tmp_path / 'home' / 'Portimao'
    assert places.is_app
    assert places.program_folder == tmp_path / 'inside_the_app'
    assert places.own_folder == own
    assert places.fits_folder == own / 'fits'
    assert places.last_answers_file == own / 'last_answers.json'
    assert places.logs_folder == own / 'logs'


# ---- test_app_never_overwrites_a_fit -------------------------------------------------
def test_app_never_overwrites_a_fit(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the app makes its folders, copies in the fit that is
    missing, and leaves a fit the user changed as it is, also when it starts again.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_places_maker
    user_folder_preparer
    """

    places = _app_places_maker(tmp_path)
    places.fits_folder.mkdir(parents=True)
    (places.fits_folder / 'standard.csv').write_text('changed by the user')
    (places.fits_folder / 'mine.csv').write_text('the user own fit')
    for _ in range(2):  # a second start must change nothing
        user_folder_preparer(places)
        assert places.logs_folder.is_dir()
        assert (places.fits_folder / 'standard.csv').read_text() == 'changed by the user'
        assert (places.fits_folder / 'other.csv').read_text() == 'shipped other'
        assert (places.fits_folder / 'mine.csv').read_text() == 'the user own fit'


# ---- test_source_keeps_things_in_program_folder --------------------------------------
def test_source_keeps_things_in_program_folder(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that, run from source, everything stays in the program
    folder, as before the app, and that preparing the places changes nothing there.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    user_folder_preparer
    user_places_finder
    """

    places = user_places_finder(is_app=False,
                                home=tmp_path / 'home',
                                program_folder=tmp_path,
                                )
    assert not places.is_app
    assert places.own_folder == tmp_path
    assert places.fits_folder == tmp_path / 'fits'
    assert places.last_answers_file == tmp_path / 'last_answers.json'
    assert places.logs_folder == tmp_path / 'logs'
    user_folder_preparer(places)
    assert list(tmp_path.iterdir()) == []


# ---- test_source_program_folder_is_found ---------------------------------------------
def test_source_program_folder_is_found() -> None:
    """
    ---- Summary ----
    Main function to check that, run from source with nothing given, the program
    folder found is the one holding main.py.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    user_places_finder
    """

    places = user_places_finder(is_app=False)
    assert (places.program_folder / 'main.py').is_file()
    assert places.own_folder == places.program_folder
