"""
Tests of the haem library: the presets, the joining of library files and the fits offered.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Dict, List, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.spectral_decomposer import (answers_fit_loader,
                                              fit_describer,
                                              fit_loader,
                                              fit_names_lister,
                                              haem_name_plainer,
                                              HAEMS_FOLDER_NAME,
                                              library_haems_lister,
                                              OWN_HAEMS_NAME,
                                              PRESETS_FOLDER_NAME,
                                              )


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
FITS_FOLDER = ROOT / 'fits'
# made-up haems: name -> (wavelength (nm), value (OD/mM/cm)) rows
HAEMS = {'Cyt cc': [(500.0, -2.0), (510.0, -17.0), (520.0, -1.0)],
         'Cyt bH': [(505.0, -3.0), (515.0, -30.0), (525.0, -2.0), (535.0, 1.0)],
         'Cyt a605': [(590.0, -1.0), (600.0, -20.0)],
         }
# the α dip of each haem of the standard preset, (OD/mM/cm, nm), read off the fit files
# it was made from (_USER_REVIEW/inbox/fit_shapes.md)
STANDARD_DIPS = {'Cyt cc': (-17.60, 551.5),
                 'Cyt bH': (-29.90, 565.4),
                 'Cyt b557': (-29.90, 557.4),
                 'Cyt bL': (-30.80, 562.6),
                 'Cyt a605': (-19.80, 598.9),
                 }


# ---- HELPERS -------------------------------------------------------------------------


# ---- _dip_finder ---------------------------------------------------------------------
def _dip_finder(fit: dict, index: int) -> Tuple[float, float]:
    """
    ---- Summary ----
    Helper function to find the α dip of one haem of a fit.

    ---- Inputs ----
    fit : dict
        Fit dictionary, as fit_loader gives it.
    index : int
        Number of the haem in the fit, from 0.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[float, float]
        (lowest value between 540 and 640 nm in OD/mM/cm, its wavelength in nm).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    value in OD/mM/cm = value on the standard scale x 1 000 000.

    ---- Helpers ----
    None.
    """

    pair = fit['data'].iloc[:, [2 * index, 2 * index + 1]].dropna().to_numpy()
    alpha = pair[(pair[:, 0] >= 540) & (pair[:, 0] <= 640)]
    lowest = int(np.argmin(alpha[:, 1]))
    return float(alpha[lowest, 1] * 1e6), float(alpha[lowest, 0])


# ---- _haem_file_writer ---------------------------------------------------------------
def _haem_file_writer(path: Path, haems: Dict[str, List[Tuple[float, float]]]) -> Path:
    """
    ---- Summary ----
    Helper function to write a made-up fit file in the layout with heading lines.

    ---- Inputs ----
    path : Path
        File to write.
    haems : Dict[str, List[Tuple[float, float]]]
        {plain haem name: (wavelength in nm, value in OD/mM/cm) rows}; one haem for a
        library file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The file written.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    names = list(haems)
    lines = ['Portimao fit file,format 1',
             'Unit,OD/mM/cm',
             '',
             ','.join(f'{name},' for name in names),
             ','.join('Wavelength (nm),OD/mM/cm' for _ in names),
             ]
    for row in range(max(len(rows) for rows in haems.values())):
        cells = []
        for name in names:
            cells += ([f'{haems[name][row][0]}', f'{haems[name][row][1]}']
                      if row < len(haems[name]) else ['', ''])
        lines.append(','.join(cells))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path


# ---- _preset_writer ------------------------------------------------------------------
def _preset_writer(path: Path, files: List[str]) -> Path:
    """
    ---- Summary ----
    Helper function to write a made-up preset listing library files.

    ---- Inputs ----
    path : Path
        File to write.
    files : List[str]
        Library file names, in the order the preset lists them.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The file written.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '\n'.join(
            ['Portimao preset,format 1', 'Holds,made up', '', 'Haem file', *files],
            ) + '\n',
        encoding='utf-8',
        )
    return path


# ---- _library_maker ------------------------------------------------------------------
def _library_maker(fits: Path) -> None:
    """
    ---- Summary ----
    Helper function to make a made-up library of three haems, one file each.

    ---- Inputs ----
    fits : Path
        The made-up fits folder.

    ---- Globals read ----
    HAEMS (module constant); HAEMS_FOLDER_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_file_writer
    """

    for name, rows in HAEMS.items():
        stem = name.split()[-1]
        _haem_file_writer(fits / HAEMS_FOLDER_NAME / f'{stem}.csv', {name: rows})


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_preset_joins_its_haems_in_order --------------------------------------------
def test_preset_joins_its_haems_in_order(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a preset gives one fit of its library files, the a
    haems first, then the b, then the c, whatever order it lists them in, each with its
    own rows and values.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    HAEMS (module constant); PRESETS_FOLDER_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    value on the standard scale = value in OD/mM/cm / 1 000 000.

    ---- Helpers ----
    _library_maker
    _preset_writer
    """

    _library_maker(tmp_path)
    _preset_writer(tmp_path / PRESETS_FOLDER_NAME / 'mine.csv',
                   ['cc.csv', 'bH.csv', 'a605.csv'],
                   )
    fit = fit_loader(tmp_path, 'mine.csv')
    names = [haem_name_plainer(name) for name in fit['haem_list']]
    assert names == ['Cyt a605', 'Cyt bH', 'Cyt cc']
    assert fit['haem_files'] == ['a605.csv', 'bH.csv', 'cc.csv']
    assert fit['data'].shape == (4, 6)
    for i, name in enumerate(names):
        pair = fit['data'].iloc[:, [2 * i, 2 * i + 1]].dropna().to_numpy()
        assert np.allclose(pair, np.array(HAEMS[name]) * [1.0, 1e-6], rtol=1e-12)


# ---- test_preset_problems_are_refused ------------------------------------------------
@pytest.mark.parametrize(('files', 'words'),
                         [(['bH.csv', 'gone.csv'], 'gone.csv'),
                          (['two.csv'], 'holds 2 haems'),
                          (['bH.csv', 'bH_again.csv'], 'both called Cyt bH'),
                          ],
                         )
def test_preset_problems_are_refused(tmp_path: Path,
                                     files: List[str],
                                     words: str,
                                     ) -> None:
    """
    ---- Summary ----
    Main function to check that a preset listing a missing file, a library file of two
    haems, or two haems of the same name is refused with a message naming the problem.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    files : List[str]
        Library files the preset lists.
    words : str
        Words the message must hold.

    ---- Globals read ----
    HAEMS (module constant); HAEMS_FOLDER_NAME, PRESETS_FOLDER_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_file_writer
    _library_maker
    _preset_writer
    """

    _library_maker(tmp_path)
    library = tmp_path / HAEMS_FOLDER_NAME
    _haem_file_writer(library / 'two.csv',
                      {'Cyt cc': HAEMS['Cyt cc'], 'Cyt bH': HAEMS['Cyt bH']},
                      )
    _haem_file_writer(library / 'bH_again.csv', {'Cyt bH': HAEMS['Cyt bH']})
    _preset_writer(tmp_path / PRESETS_FOLDER_NAME / 'bad.csv', files)
    with pytest.raises(ValueError, match=words):
        fit_loader(tmp_path, 'bad.csv')


# ---- test_root_file_with_a_preset_name_is_not_offered --------------------------------
def test_root_file_with_a_preset_name_is_not_offered(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the fits offered are the presets, then the user's own
    fit files, and that a fit file with a preset's name (an old copy) is neither
    offered nor loaded in place of the preset.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    HAEMS (module constant); PRESETS_FOLDER_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_file_writer
    _library_maker
    _preset_writer
    """

    _library_maker(tmp_path)
    _preset_writer(tmp_path / PRESETS_FOLDER_NAME / 'standard.csv', ['bH.csv'])
    _haem_file_writer(tmp_path / 'standard.csv', HAEMS)  # an old combined copy
    _haem_file_writer(tmp_path / 'Mine.csv', {'Cyt cc': HAEMS['Cyt cc']})
    assert fit_names_lister(tmp_path) == ['standard.csv', 'Mine.csv']
    assert fit_loader(tmp_path, 'standard.csv')['haem_files'] == ['bH.csv']
    assert len(fit_loader(tmp_path, 'Mine.csv')['haem_list']) == 1
    with pytest.raises(ValueError, match='nothing.csv'):
        fit_loader(tmp_path, 'nothing.csv')


# ---- test_standard_preset_keeps_its_haems --------------------------------------------
def test_standard_preset_keeps_its_haems() -> None:
    """
    ---- Summary ----
    Main function to check that the standard fit, now a preset of the haem library,
    gives the five haems and α dips of the fit file it replaced, and that the cc of
    temp_fit_037v keeps the 35.2 OD/mM/cm of its old file, its preset giving it 2 haems
    per protein.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FITS_FOLDER, STANDARD_DIPS (module constants); settings.STANDARD_FIT.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _dip_finder
    """

    fit = fit_loader(FITS_FOLDER, settings.STANDARD_FIT)
    names = [haem_name_plainer(name) for name in fit['haem_list']]
    assert names == ['Cyt a605', 'Cyt b557', 'Cyt bH', 'Cyt bL', 'Cyt cc']
    for i, name in enumerate(names):
        value, wavelength = _dip_finder(fit, i)
        assert value == pytest.approx(STANDARD_DIPS[name][0], abs=0.01), name
        assert wavelength == pytest.approx(STANDARD_DIPS[name][1], abs=0.1), name
    latest = fit_loader(FITS_FOLDER, 'temp_fit_037v.csv')
    cc = [haem_name_plainer(name) for name in latest['haem_list']].index('Cyt cc')
    assert _dip_finder(latest, cc)[0] == pytest.approx(-35.20, abs=0.01)
    preset = (FITS_FOLDER / PRESETS_FOLDER_NAME / 'temp_fit_037v.csv').read_text(
        encoding='utf-8-sig',
        )
    assert 'Haem file,Haems per protein' in preset
    assert 'c1_037v.csv,2' in preset.splitlines()


# ---- test_own_haems_are_built_from_the_library ---------------------------------------
def test_own_haems_are_built_from_the_library(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the haems ticked under Build a fit: the library is listed
    for the tick boxes in the order a, b, c with each file's haem name; the haems
    ticked load as one fit, named in words with their files; and no haem ticked, or a
    ticked file that is missing, is refused with a message, while a preset name still
    loads the preset.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    OWN_HAEMS_NAME, PRESETS_FOLDER_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _library_maker
    _preset_writer
    """

    _library_maker(tmp_path)
    assert library_haems_lister(tmp_path) == [
        {'file': 'a605.csv', 'haem': 'Cyt a605', 'type': 'a'},
        {'file': 'bH.csv', 'haem': 'Cyt bH', 'type': 'b'},
        {'file': 'cc.csv', 'haem': 'Cyt cc', 'type': 'c'},
        ]
    fit = answers_fit_loader(tmp_path, OWN_HAEMS_NAME, ['cc.csv', 'bH.csv'])
    assert [haem_name_plainer(name) for name in fit['haem_list']] == ['Cyt bH',
                                                                      'Cyt cc',
                                                                      ]
    assert fit_describer(OWN_HAEMS_NAME, ['cc.csv', 'bH.csv']) == (
        f'{OWN_HAEMS_NAME}: cc, bH'
    )
    assert fit_describer('standard.csv', ['cc.csv']) == 'standard.csv'
    with pytest.raises(ValueError, match='Tick at least one haem'):
        answers_fit_loader(tmp_path, OWN_HAEMS_NAME, [])
    with pytest.raises(ValueError, match='gone.csv'):
        answers_fit_loader(tmp_path, OWN_HAEMS_NAME, ['cc.csv', 'gone.csv'])
    _preset_writer(tmp_path / PRESETS_FOLDER_NAME / 'standard.csv', ['bH.csv'])
    assert answers_fit_loader(tmp_path, 'standard.csv', [])['haem_files'] == ['bH.csv']
    assert library_haems_lister(tmp_path / 'nothing') == []
