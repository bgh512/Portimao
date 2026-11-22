"""
Edges dragged on the plot of a file to choose parts of it, such as the trimmed and
ignored parts.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import base64
import copy
import io
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.colors import to_hex, to_rgb
from PIL import Image, ImageDraw

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_viewer.viewer_preview import IGNORE_COLOUR, TimeAxis


# ---- CONSTANTS -----------------------------------------------------------------------
TRIM_COLOUR = '0.45'
OXIDISED_COLOUR = '#d62728'  # red and blue, as oxidised and reduced blood are drawn
REDUCED_COLOUR = '#1f77b4'
AVERAGE_COLOUR = '#2878B5'  # the blue the averaging windows have in the figures
UNFIT_COLOUR = '#d62728'  # an averaging window that does not fit
PREVIOUS_COLOUR = '#d62728'
# How each kind of part looks: its colour, how strongly its shading covers the plot (0
# to 1), whether it is hatched, and the row of its handles above the plot (0 the top).
# The rows keep two edges that meet apart, so both can still be taken.
PART_STYLES = {'trim': (TRIM_COLOUR, 0.25, True, 0),
               'ignore': (IGNORE_COLOUR, 0.22, False, 1),
               'oxidised': (OXIDISED_COLOUR, 0.18, False, 0),
               'reduced': (REDUCED_COLOUR, 0.18, False, 1),
               'average': (AVERAGE_COLOUR, 0.22, False, 0),
               'average_end': (AVERAGE_COLOUR, 0.22, False, 1),
               'average_unfit': (UNFIT_COLOUR, 0.22, True, 0),
               }
HANDLE_ROW_PX = 22
HANDLE_SIZE_PX = (9, 16)  # (width, height)
HANDLE_BAND_PX = 2 * HANDLE_ROW_PX + 6  # room kept above the picture for the handles
GRAB_DISTANCE_PX = 6  # how near its line the mouse must be to take an edge
HATCH_SPACING_PX = 8
HATCH_STRENGTH = 0.6
EDGE_WIDTH_PX = 2
DRAG_PAUSE_MS = 30  # the shading follows a drag at most this often
WORDS_COLOUR = '#303030'
PREVIOUS_KEY_TEXT = 'red dashed = the limits you entered before'


# ---- EdgeChoice ----------------------------------------------------------------------
@dataclass
class EdgeChoice:
    """
    ---- Summary ----
    What the window needs to let the user choose parts of the plot of every file by
    dragging edges, or typing them in the strip: the fields shown, the value of each
    field for each file, and the rules of the step that uses it.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    fields: List[Tuple[str, str]]
    values: Dict[str, Dict[str, float]]
    layout_finder: Callable[[str, Dict[str, float]],
                            Tuple[List[Tuple[str, float, str, str]],
                                  List[Tuple[float, float, str]],
                                  ],
                            ]
    pointer_reader: Callable[[str, Dict[str, float], str, float], float]
    value_setter: Callable[[str, Dict[str, float], str, float], Dict[str, float]]
    key_text: str = ''
    previous: Dict[str, Dict[str, float]] = field(default_factory=dict)
    is_every_file: bool = True
    value_copier: Optional[Callable[[str, str, str, float], Optional[float]]] = None
    unit: str = 'min'
    switch: Optional[Tuple[str, str]] = None


# ---- EdgeOverlay ---------------------------------------------------------------------
class EdgeOverlay:
    """
    ---- Summary ----
    The edges over the plot of the file shown, while a step lets the user choose parts
    of the plot with them: the parts are shaded into the picture (see-through, so the
    data stays readable), each edge is a line with a handle and its words above the
    plot, and the edges entered before are red dashed lines. An edge is dragged by its
    handle or its line, and the shading follows the drag without the plot being drawn
    again. Every method runs on the window thread, except values_reader.

    ---- Attributes ----
    choice : Optional[EdgeChoice]
        The choice being made, or None while there is none.
    values : Dict[str, Dict[str, float]]
        {file name: {field: value}} as the user has set them so far; replaced, never
        changed in place, at each change.
    is_every_file : bool
        True: a moved or typed edge moves on every file; False: on the file shown only.

    ---- Globals read ----
    The module constants.

    ---- Methods ----
    __init__
    _edges_drawer
    _picture_shader
    _update_runner
    _values_changer
    choice_setter
    field_setter
    hit_layout_finder
    hover_handler
    is_on
    key_teller
    motion_handler
    picture_placer
    press_handler
    release_handler
    values_reader
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 canvas: Any,
                 family: str,
                 on_change: Callable[[], None],
                 ) -> None:
        """
        ---- Summary ----
        Method to set up the overlay, with no choice being made.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        canvas : Any
            The Tk canvas the plot is shown on.
        family : str
            Font family of the words by the handles.
        on_change : Callable[[], None]
            Called after every change of the values, so the window can show them.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the attributes on the instance.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._tk = tk
        self._canvas = canvas
        self._family = family
        self._on_change = on_change
        self.choice: Optional[EdgeChoice] = None
        self.values: Dict[str, Dict[str, float]] = {}
        self.is_every_file = True
        self._name: Optional[str] = None
        self._picture: Optional[Image.Image] = None
        self._item: Optional[int] = None
        self._box: Optional[Tuple[float, float, float, float]] = None
        self._axis: Optional[TimeAxis] = None
        self._photo: Any = None
        self._dragged: Optional[str] = None
        self._drag_x = 0.0
        self._drag_job: Any = None

    # ---- OVERLAY HELPERS -------------------------------------------------------------

    # ---- _edges_drawer ---------------------------------------------------------------
    def _edges_drawer(self) -> None:
        """
        ---- Summary ----
        Method to draw the edges of the file shown over its picture: the edges entered
        before as red dashed lines, then each edge as a line from its handle above the
        plot to the bottom of the panels, with its words beside the handle, towards
        the middle of the plot.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PART_STYLES, PREVIOUS_COLOUR, HANDLE_BAND_PX, HANDLE_ROW_PX, HANDLE_SIZE_PX,
        EDGE_WIDTH_PX, WORDS_COLOUR.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the canvas, tagged 'edges' (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        minute_x_finder
        """

        canvas = self._canvas
        canvas.delete('edges')
        if not self.is_on or self._box is None:
            return
        name, box, axis = self._name, self._box, self._axis
        left, top, width, height = box
        panel_left = left + axis.left * width
        panel_right = left + axis.right * width
        panel_top = top + (1.0 - axis.top) * height
        panel_bottom = top + (1.0 - axis.bottom) * height
        middle = (panel_left + panel_right) / 2.0
        band_top = top - HANDLE_BAND_PX + 3

        # ---- 1 The edges entered before ----------------------------------------------
        if name in self.choice.previous:
            before, _ = self.choice.layout_finder(name, self.choice.previous[name])
            for _, time_min, _, _ in before:
                x = min(max(minute_x_finder(time_min, box, axis), panel_left),
                        panel_right,
                        )
                canvas.create_line(x,
                                   panel_top,
                                   x,
                                   panel_bottom,
                                   fill=PREVIOUS_COLOUR,
                                   dash=(5, 3),
                                   width=1,
                                   tags='edges',
                                   )

        # ---- 2 The edges, their handles and their words ------------------------------
        edges, _ = self.choice.layout_finder(name, self.values[name])
        for key, time_min, words, kind in edges:
            colour, _, _, row = PART_STYLES[kind]
            colour = to_hex(to_rgb(colour))
            x = min(max(minute_x_finder(time_min, box, axis), panel_left), panel_right)
            handle_top = band_top + row * HANDLE_ROW_PX
            canvas.create_line(x,
                               handle_top + HANDLE_SIZE_PX[1],
                               x,
                               panel_bottom,
                               fill=colour,
                               width=EDGE_WIDTH_PX,
                               tags='edges',
                               )
            canvas.create_rectangle(
                x - HANDLE_SIZE_PX[0] / 2.0,
                handle_top,
                x + HANDLE_SIZE_PX[0] / 2.0,
                handle_top + HANDLE_SIZE_PX[1],
                fill=colour,
                outline=WORDS_COLOUR if key == self._dragged else colour,
                tags='edges',
                )
            is_left = x < middle
            canvas.create_text(x + 8 if is_left else x - 8,
                               handle_top + HANDLE_SIZE_PX[1] / 2.0,
                               text=words,
                               anchor='w' if is_left else 'e',
                               fill=WORDS_COLOUR,
                               font=(self._family,
                                     9,
                                     'bold' if key == self._dragged else 'normal',
                                     ),
                               tags='edges',
                               )

    # ---- _picture_shader -------------------------------------------------------------
    def _picture_shader(self) -> None:
        """
        ---- Summary ----
        Method to show the picture of the file shown with its parts shaded, in place of
        the picture on the canvas.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the picture on the canvas (side effect).

        ---- Equations ----
        x in the picture = minute_x_finder with the picture at (0, 0).

        ---- Helpers ----
        minute_x_finder
        photo_maker
        shaded_picture_maker
        """

        if not self.is_on or self._picture is None:
            return
        axis = self._axis
        width, height = self._picture.size
        inside = (0.0, 0.0, width, height)
        lowest, highest = axis.left * width, axis.right * width
        top, bottom = (1.0 - axis.top) * height, (1.0 - axis.bottom) * height
        _, parts = self.choice.layout_finder(self._name, self.values[self._name])
        shaded = []
        for start, end, kind in parts:
            x0 = min(max(minute_x_finder(start, inside, axis), lowest), highest)
            x1 = min(max(minute_x_finder(end, inside, axis), lowest), highest)
            shaded.append((x0, x1, top, bottom, kind))
        self._photo = photo_maker(self._tk,
                                  shaded_picture_maker(self._picture, shaded),
                                  )
        self._canvas.itemconfigure(self._item, image=self._photo)

    # ---- _update_runner --------------------------------------------------------------
    def _update_runner(self) -> None:
        """
        ---- Summary ----
        Method to move the edge being dragged to where the mouse last was, at most
        every DRAG_PAUSE_MS while the mouse moves.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Moves the edge (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _values_changer
        x_minute_finder
        """

        self._drag_job = None
        if self._dragged is None or not self.is_on or self._box is None:
            return
        name = self._name
        time_min = x_minute_finder(self._drag_x, self._box, self._axis)
        value = self.choice.pointer_reader(name,
                                           self.values[name],
                                           self._dragged,
                                           time_min,
                                           )
        self._values_changer(self._dragged, value)

    # ---- _values_changer -------------------------------------------------------------
    def _values_changer(self, key: str, value: float) -> None:
        """
        ---- Summary ----
        Method to set one field of the file shown, or of every file, through the rules
        of the step, then show the result. When the step has a rule for copying, the
        other files get the value that rule gives them from the file shown.

        ---- Inputs ----
        key : str
            The field set.
        value : float
            Its new value, before the rules of each file are applied.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Replaces values, redraws the overlay and tells the window (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_drawer
        _picture_shader
        every_file_setter
        """

        if not self.is_on or self._name not in self.values:
            return
        names = list(self.values) if self.is_every_file else [self._name]
        changed = every_file_setter(self.values,
                                    names,
                                    key,
                                    value,
                                    self.choice.value_setter,
                                    shown=self._name,
                                    copier=self.choice.value_copier,
                                    )
        if changed == self.values:
            self._edges_drawer()
            return
        self.values = changed
        self._picture_shader()
        self._edges_drawer()
        self._on_change()

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- choice_setter ---------------------------------------------------------------
    def choice_setter(self, choice: Optional[EdgeChoice]) -> None:
        """
        ---- Summary ----
        Method to start a choice with its starting values, or end it (None), taking the
        edges off the plot.

        ---- Inputs ----
        choice : Optional[EdgeChoice]
            The choice, or None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Replaces the choice and values and clears the edges (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._drag_job is not None:
            self._canvas.after_cancel(self._drag_job)
            self._drag_job = None
        self._dragged = None
        self.choice = choice
        self.values = copy.deepcopy(choice.values) if choice is not None else {}
        self.is_every_file = choice.is_every_file if choice is not None else True
        self._canvas.delete('edges')
        self._canvas.configure(cursor='')

    # ---- field_setter ----------------------------------------------------------------
    def field_setter(self, key: str, value: float) -> None:
        """
        ---- Summary ----
        Method to take a value typed in the strip for one field of the file shown (of
        every file when is_every_file).

        ---- Inputs ----
        key : str
            The field typed in.
        value : float
            The number typed.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the values and redraws (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _values_changer
        """

        self._values_changer(key, value)

    # ---- hit_layout_finder -----------------------------------------------------------
    def hit_layout_finder(self,
                          ) -> Tuple[List[Tuple[str, float, int]],
                                     float,
                                     Tuple[float, float],
                                     ]:
        """
        ---- Summary ----
        Method to give where the edges of the file shown sit on the canvas, for
        edge_hit_finder.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PART_STYLES, HANDLE_BAND_PX.

        ---- Outputs ----
        Tuple[List[Tuple[str, float, int]], float, Tuple[float, float]]
            ([(key, x in pixels, row of its handle)], top of the handles in pixels,
            (top, bottom) of the panels in pixels).

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        minute_x_finder
        """

        left, top, width, height = self._box
        axis = self._axis
        lowest, highest = left + axis.left * width, left + axis.right * width
        edges, _ = self.choice.layout_finder(self._name, self.values[self._name])
        placed = [(key,
                   min(max(minute_x_finder(time_min, self._box, axis), lowest), highest),
                   PART_STYLES[kind][3],
                   )
                  for key, time_min, _, kind in edges
                  ]
        panel = (top + (1.0 - axis.top) * height, top + (1.0 - axis.bottom) * height)
        return placed, top - HANDLE_BAND_PX + 3, panel

    # ---- hover_handler ---------------------------------------------------------------
    def hover_handler(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to show the mouse as a two-way arrow over an edge it can take.

        ---- Inputs ----
        event : Any
            The Tk motion event.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the cursor of the canvas (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        edge_hit_finder
        hit_layout_finder
        """

        if not self.is_on or self._box is None or self._dragged is not None:
            return
        found = edge_hit_finder(event.x, event.y, *self.hit_layout_finder())
        self._canvas.configure(cursor='sb_h_double_arrow' if found else '')

    # ---- is_on -----------------------------------------------------------------------
    @property
    def is_on(self) -> bool:
        """
        ---- Summary ----
        Whether a choice is being made.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True while a choice is being made.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return self.choice is not None

    # ---- key_teller ------------------------------------------------------------------
    def key_teller(self) -> str:
        """
        ---- Summary ----
        Method to give the words that explain the colours on the plot.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PREVIOUS_KEY_TEXT.

        ---- Outputs ----
        str
            The key of the choice, with the red dashed lines when they are drawn; empty
            when there is no choice.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if not self.is_on:
            return ''
        parts = [self.choice.key_text] if self.choice.key_text else []
        if self.choice.previous:
            parts.append(PREVIOUS_KEY_TEXT)
        return '; '.join(parts)

    # ---- motion_handler --------------------------------------------------------------
    def motion_handler(self, event: Any) -> bool:
        """
        ---- Summary ----
        Method to follow the mouse while an edge is dragged; the edge moves at most
        every DRAG_PAUSE_MS.

        ---- Inputs ----
        event : Any
            The Tk motion event.

        ---- Globals read ----
        DRAG_PAUSE_MS.

        ---- Outputs ----
        bool
            True when an edge is being dragged (the window then does nothing else
            with the drag).

        ---- Globals mutated ----
        None. Schedules the move (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _update_runner
        """

        if self._dragged is None:
            return False
        self._drag_x = float(event.x)
        if self._drag_job is None:
            self._drag_job = self._canvas.after(DRAG_PAUSE_MS, self._update_runner)
        return True

    # ---- picture_placer --------------------------------------------------------------
    def picture_placer(self,
                       name: Optional[str],
                       picture: Optional[Image.Image],
                       item: Optional[int],
                       box: Optional[Tuple[float, float, float, float]],
                       axis: Optional[TimeAxis],
                       ) -> None:
        """
        ---- Summary ----
        Method to take the picture of a file just put on the canvas, shade it and draw
        its edges; with no picture (a message, a figure, a picture without a time
        axis) nothing is drawn until the next one.

        ---- Inputs ----
        name : Optional[str]
            Name of the file shown, or None.
        picture : Optional[Image.Image]
            The picture at the size shown, without shading.
        item : Optional[int]
            The canvas item showing the picture; its picture is replaced.
        box : Optional[Tuple[float, float, float, float]]
            (left, top, width, height) of the picture on the canvas, in pixels.
        axis : Optional[TimeAxis]
            Where the time axis sits in the picture.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the picture, changes it on the canvas and draws the edges (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_drawer
        _picture_shader
        """

        is_usable = (name is not None
                     and picture is not None
                     and axis is not None
                     and self.is_on
                     and name in self.values
                     )
        if not is_usable:
            self._name = self._picture = self._item = self._box = self._axis = None
            self._dragged = None
            return
        self._name, self._item, self._box, self._axis = name, item, box, axis
        self._picture = picture.convert('RGB')
        self._picture_shader()
        self._edges_drawer()

    # ---- press_handler ---------------------------------------------------------------
    def press_handler(self, event: Any) -> bool:
        """
        ---- Summary ----
        Method to take the edge under the mouse when the button is pressed.

        ---- Inputs ----
        event : Any
            The Tk click event.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True when an edge was taken (the window then does nothing else with the
            click).

        ---- Globals mutated ----
        None. Notes the edge taken and redraws the edges (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_drawer
        edge_hit_finder
        hit_layout_finder
        """

        if not self.is_on or self._box is None:
            return False
        found = edge_hit_finder(event.x, event.y, *self.hit_layout_finder())
        if found is None:
            return False
        self._dragged = found
        self._drag_x = float(event.x)
        self._edges_drawer()
        return True

    # ---- release_handler -------------------------------------------------------------
    def release_handler(self, event: Any) -> bool:
        """
        ---- Summary ----
        Method to put the edge being dragged where the button is let go.

        ---- Inputs ----
        event : Any
            The Tk release event.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True when an edge was being dragged.

        ---- Globals mutated ----
        None. Moves the edge and redraws (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_drawer
        _update_runner
        """

        if self._dragged is None:
            return False
        if self._drag_job is not None:
            self._canvas.after_cancel(self._drag_job)
            self._drag_job = None
        self._drag_x = float(event.x)
        self._update_runner()
        self._dragged = None
        self._edges_drawer()
        return True

    # ---- values_reader ---------------------------------------------------------------
    def values_reader(self) -> Dict[str, Dict[str, float]]:
        """
        ---- Summary ----
        Method to give a copy of the values as they are now; safe to call from the
        program thread, as the values are replaced, never changed in place.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Dict[str, Dict[str, float]]
            {file name: {field: value}}.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return copy.deepcopy(self.values)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- edge_hit_finder -----------------------------------------------------------------
def edge_hit_finder(x: float,
                    y: float,
                    edges: List[Tuple[str, float, int]],
                    band_top: float,
                    panel: Tuple[float, float],
                    ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to find the edge the mouse is on: on its handle, or near its line
    between the handles and the bottom of the panels. Where two lines meet, the edge
    whose handle is in the lower row (the inner one) is taken; the other is still taken
    by its handle.

    ---- Inputs ----
    x : float
        Distance of the mouse from the left of the canvas, in pixels.
    y : float
        Distance of the mouse from the top of the canvas, in pixels.
    edges : List[Tuple[str, float, int]]
        [(key, x of its line in pixels, row of its handle, 0 the top)].
    band_top : float
        Top of the first row of handles, in pixels.
    panel : Tuple[float, float]
        (top, bottom) of the panels, in pixels.

    ---- Globals read ----
    GRAB_DISTANCE_PX, HANDLE_ROW_PX, HANDLE_SIZE_PX.

    ---- Outputs ----
    Optional[str]
        The key of the edge, or None when the mouse is on none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    On a handle: row top <= y <= row top + row height and |x - line| <= half a handle
    + 2 px. On a line: band top <= y <= panel bottom and |x - line| <= grab distance.

    ---- Helpers ----
    None.
    """

    for key, line_x, row in edges:
        row_top = band_top + row * HANDLE_ROW_PX
        if (row_top <= y <= row_top + HANDLE_ROW_PX
            and abs(x - line_x) <= HANDLE_SIZE_PX[0] / 2.0 + 2.0
            ):
            return key
    if not band_top <= y <= panel[1]:
        return None
    near = [(round(abs(x - line_x)), -row, index, key)
            for index, (key, line_x, row) in enumerate(edges)
            if abs(x - line_x) <= GRAB_DISTANCE_PX
            ]
    return min(near)[3] if near else None


# ---- every_file_setter ---------------------------------------------------------------
def every_file_setter(values: Dict[str, Dict[str, float]],
                      names: List[str],
                      key: str,
                      value: float,
                      setter: Callable[[str, Dict[str, float], str, float],
                                       Dict[str, float],
                                       ],
                      shown: Optional[str] = None,
                      copier: Optional[Callable[[str, str, str, float],
                                                Optional[float],
                                                ]
                                       ] = None,
                      ) -> Dict[str, Dict[str, float]]:
    """
    ---- Summary ----
    Main function to set one field to the same value on some files, each kept within
    its own limits by the rules of the step. With a rule for copying, the file shown is
    set first, and each other file gets the value the rule gives it from the value the
    file shown ended with; a file the rule gives nothing keeps its values.

    ---- Inputs ----
    values : Dict[str, Dict[str, float]]
        {file name: {field: value}} now; not changed.
    names : List[str]
        The files to set.
    key : str
        The field set.
    value : float
        The value wanted, the same for each file.
    setter : Callable[[str, Dict[str, float], str, float], Dict[str, float]]
        The rule of the step: (file name, its values, field, value) -> its new values.
    shown : Optional[str]
        The file the value was set on; needed only with ``copier``.
    copier : Optional[Callable[[str, str, str, float], Optional[float]]]
        The rule for copying: (file shown, other file, field, value on the file
        shown) -> value for the other file, or None to leave that file as it is.
        None (or no file shown): every file gets the same value.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Dict[str, float]]
        New {file name: {field: value}}; the files not named keep their values.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    changed = dict(values)
    if copier is None or shown is None or shown not in names:
        for name in names:
            changed[name] = setter(name, values[name], key, value)
        return changed
    changed[shown] = setter(shown, values[shown], key, value)
    for name in names:
        if name == shown:
            continue
        copied = copier(shown, name, key, changed[shown][key])
        if copied is not None:
            changed[name] = setter(name, values[name], key, copied)
    return changed


# ---- minute_x_finder -----------------------------------------------------------------
def minute_x_finder(time_min: float,
                    picture_box: Tuple[float, float, float, float],
                    time_axis: TimeAxis,
                    ) -> float:
    """
    ---- Summary ----
    Main function to find where a time falls across the plot area: the inverse of
    pointed_time_finder (utils_viewer/viewer_gui.py).

    ---- Inputs ----
    time_min : float
        The time, in minutes on the time axis of the picture.
    picture_box : Tuple[float, float, float, float]
        (left, top, width, height) of the picture in the plot area, in pixels.
    time_axis : TimeAxis
        Where the time axis sits in the picture, and the times at its ends.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        Distance from the left edge of the plot area, in pixels; outside the panels for
        a time outside the axis.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    share = (time - start) / (end - start);
    x = left + (axis left + share * (axis right - axis left)) * width.

    ---- Helpers ----
    None.
    """

    left, _, width, _ = picture_box
    span = time_axis.end_min - time_axis.start_min
    share = (time_min - time_axis.start_min) / span if span else 0.0
    return left + (time_axis.left + share * (time_axis.right - time_axis.left)) * width


# ---- own_value_lister ----------------------------------------------------------------
def own_value_lister(values: Dict[str, Dict[str, float]]) -> List[str]:
    """
    ---- Summary ----
    Main function to list the files whose values differ from those most files have, so
    the window can mark them.

    ---- Inputs ----
    values : Dict[str, Dict[str, float]]
        {file name: {field: value}}, every file with the same fields.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The files with a value of their own in any field, in the order given; empty
        for fewer than two files.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if len(values) < 2:
        return []
    fields = list(next(iter(values.values())))
    common = {key: Counter(round(own[key], 6)
                           for own in values.values()
                           ).most_common(1)[0][0]
              for key in fields
              }
    return [name
            for name, own in values.items()
            if any(round(own[key], 6) != common[key] for key in fields)
            ]


# ---- photo_maker ---------------------------------------------------------------------
def photo_maker(tk: Any, picture: Image.Image) -> Any:
    """
    ---- Summary ----
    Main function to turn a picture into one Tk can show, quickly enough to follow a
    drag: as raw pixels (PPM), or as PNG where this Tk cannot read those.

    ---- Inputs ----
    tk : Any
        The tkinter module.
    picture : Image.Image
        The picture, in RGB.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Any
        A tk.PhotoImage of the picture.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    width, height = picture.size
    header = f'P6 {width} {height} 255 '.encode('ascii')
    try:
        return tk.PhotoImage(width=width,
                             height=height,
                             data=header + picture.tobytes(),
                             format='PPM',
                             )
    except tk.TclError:  # slower, but read by every Tk
        buffer = io.BytesIO()
        picture.save(buffer, format='PNG')
        return tk.PhotoImage(data=base64.b64encode(buffer.getvalue()).decode('ascii'))


# ---- shaded_picture_maker ------------------------------------------------------------
def shaded_picture_maker(picture: Image.Image,
                         parts: List[Tuple[float, float, float, float, str]],
                         ) -> Image.Image:
    """
    ---- Summary ----
    Main function to shade parts of a picture, see-through so what is under them stays
    readable, each in the colour of its kind and hatched where its kind is.

    ---- Inputs ----
    picture : Image.Image
        The picture; not changed.
    parts : List[Tuple[float, float, float, float, str]]
        [(left, right, top, bottom, kind)] in pixels of the picture, kind a key of
        PART_STYLES; a part narrower than a pixel is left out.

    ---- Globals read ----
    PART_STYLES, HATCH_SPACING_PX, HATCH_STRENGTH.

    ---- Outputs ----
    Image.Image
        A new RGB picture of the same size.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Shaded pixel = (1 - strength) * pixel + strength * colour.

    ---- Helpers ----
    None.
    """

    layer = Image.new('RGBA', picture.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for left, right, top, bottom, kind in parts:
        if right - left < 1.0 or bottom - top < 1.0:
            continue
        colour, strength, is_hatched, _ = PART_STYLES[kind]
        rgb = tuple(round(channel * 255) for channel in to_rgb(colour))
        box = (round(left), round(top), round(right) - 1, round(bottom) - 1)
        draw.rectangle(box, fill=rgb + (round(strength * 255),))
        if not is_hatched:
            continue
        tile = Image.new('RGBA',
                         (box[2] - box[0] + 1, box[3] - box[1] + 1),
                         (0, 0, 0, 0),
                         )
        lines = ImageDraw.Draw(tile)
        for start in range(-tile.height, tile.width, HATCH_SPACING_PX):
            lines.line((start, tile.height, start + tile.height, 0),
                       fill=rgb + (round(HATCH_STRENGTH * 255),),
                       width=1,
                       )
        layer.alpha_composite(tile, (box[0], box[1]))
    return Image.alpha_composite(picture.convert('RGBA'), layer).convert('RGB')


# ---- x_minute_finder -----------------------------------------------------------------
def x_minute_finder(x: float,
                    picture_box: Tuple[float, float, float, float],
                    time_axis: TimeAxis,
                    ) -> float:
    """
    ---- Summary ----
    Main function to find the time at a place across the plot area, kept within the
    time axis, so an edge dragged past the end of the panels stops at their edge.

    ---- Inputs ----
    x : float
        Distance from the left edge of the plot area, in pixels.
    picture_box : Tuple[float, float, float, float]
        (left, top, width, height) of the picture in the plot area, in pixels.
    time_axis : TimeAxis
        Where the time axis sits in the picture, and the times at its ends.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The time in minutes, between the times at the two ends of the axis.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    share = ((x - left) / width - axis left) / (axis right - axis left);
    time = start + share * (end - start).

    ---- Helpers ----
    None.
    """

    left, _, width, _ = picture_box
    across = time_axis.right - time_axis.left
    if width <= 0 or across <= 0:
        return time_axis.start_min
    share = ((x - left) / width - time_axis.left) / across
    share = min(max(share, 0.0), 1.0)
    return time_axis.start_min + share * (time_axis.end_min - time_axis.start_min)
