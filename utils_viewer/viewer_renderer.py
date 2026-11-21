"""
The background thread of the experiment browser window that draws the previews.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import threading
from typing import Callable, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.user_notices import problem_teller
from utils_viewer.viewer_preview import (kept_file_lister,
                                         PreviewSpec,
                                         preview_figure_builder,
                                         time_axis_finder,
                                         TimeAxis,
                                         ViewerSession,
                                         )


# ---- PreviewRenderer -----------------------------------------------------------------
class PreviewRenderer(threading.Thread):
    """
    ---- Summary ----
    Thread that draws the previews with the latest settings: the file being looked at
    first, then the ones beside it (the files the window keeps read), so the arrows lead
    to a drawn file. Any other file is drawn when it is looked at, so a big dataset is
    not read from disk again after every answer. A newer request makes it drop the work
    for the older one.

    ---- Attributes ----
    None public.

    ---- Globals read ----
    settings.PREVIEW_DPI, settings.WINDOW_KEPT_FILES.

    ---- Methods ----
    __init__
    _next_picker
    _picture_maker
    request_setter
    run
    stopper
    wanted_setter
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 session: ViewerSession,
                 deliver: Callable[[int, str, Optional[bytes], str, Optional[TimeAxis]],
                                   None],
                 ) -> None:
        """
        ---- Summary ----
        Method to set up the thread (it is started by the caller).

        ---- Inputs ----
        session : ViewerSession
            The browser session (files, cache).
        deliver : Callable[[int, str, Optional[bytes], str, Optional[TimeAxis]], None]
            Function called with (version, file name, PNG bytes or None, notes, time
            axis of the picture or None) for each finished preview. It is called from
            this thread.

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

        super().__init__(daemon=True, name='preview-renderer')
        self._session = session
        self._deliver = deliver
        self._names: List[str] = [s['name'] for s in session.summaries]
        self._condition = threading.Condition()
        self._spec: Optional[PreviewSpec] = None
        self._version = 0
        self._wanted = 0
        self._done: set = set()
        self._is_stopped = False

    # ---- RENDERER HELPERS ------------------------------------------------------------

    # ---- _next_picker ----------------------------------------------------------------
    def _next_picker(self) -> Optional[str]:
        """
        ---- Summary ----
        Method to pick the file to draw next: the nearest one to the file being looked
        at, among the files the window keeps read, that has not been drawn with the
        current settings. The caller holds the lock.

        ---- Inputs ----
        None.

        ---- Globals read ----
        settings.WINDOW_KEPT_FILES.

        ---- Outputs ----
        Optional[str]
            File name, or None when those files are drawn.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        kept_file_lister
        """

        nearest = kept_file_lister(self._wanted,
                                   len(self._names),
                                   settings.WINDOW_KEPT_FILES,
                                   )
        return next((self._names[i]
                     for i in nearest
                     if self._names[i] not in self._done
                     ),
                    None,
                    )

    # ---- _picture_maker --------------------------------------------------------------
    def _picture_maker(self,
                       spec: PreviewSpec,
                       name: str,
                       ) -> Tuple[Optional[bytes], str, Optional[TimeAxis]]:
        """
        ---- Summary ----
        Method to draw one file and turn the figure into a PNG picture.

        ---- Inputs ----
        spec : PreviewSpec
            The settings to draw with.
        name : str
            Name of the file.

        ---- Globals read ----
        settings.PREVIEW_DPI.

        ---- Outputs ----
        Tuple[Optional[bytes], str, Optional[TimeAxis]]
            (PNG bytes, notes, time axis); the bytes are None when the preview could
            not be drawn and the notes then say why in one sentence. The time axis says
            where the shared time axis sits in the picture, and is None when there is
            none.

        ---- Globals mutated ----
        None. The details of a problem go to the log (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        preview_figure_builder
        problem_teller
        time_axis_finder
        """

        try:
            figure, notes = preview_figure_builder(self._session, spec, name)
            if figure is None:
                return None, notes, None
            buffer = io.BytesIO()
            figure.savefig(buffer, format='png', dpi=settings.PREVIEW_DPI)
            return buffer.getvalue(), notes, time_axis_finder(figure)
        except Exception as exc:  # a preview problem must never stop the questions
            return None, problem_teller(f'Preview not drawn for {name}', exc), None

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- request_setter --------------------------------------------------------------
    def request_setter(self, spec: PreviewSpec, version: int, wanted: int) -> None:
        """
        ---- Summary ----
        Method to ask for the files to be drawn again with new settings: the file being
        looked at and the ones beside it now, any other when it is looked at.

        ---- Inputs ----
        spec : PreviewSpec
            The new settings.
        version : int
            Number of this request; results carry it so old ones can be dropped.
        wanted : int
            Index of the file being looked at, which is drawn first.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Replaces the work of the thread (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        with self._condition:
            self._spec = spec
            self._version = version
            self._wanted = wanted
            self._done = set()
            self._condition.notify_all()

    # ---- run -------------------------------------------------------------------------
    def run(self) -> None:
        """
        ---- Summary ----
        Method that draws previews until stopped. The name is fixed by the thread
        protocol.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Passes each finished preview to the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _next_picker
        _picture_maker
        """

        while True:
            with self._condition:
                while not self._is_stopped:
                    name = self._next_picker() if self._spec is not None else None
                    if name is not None:
                        break
                    self._condition.wait()
                if self._is_stopped:
                    return
                spec, version = self._spec, self._version
            picture, notes, time_axis = self._picture_maker(spec, name)
            with self._condition:
                if version == self._version:
                    self._done.add(name)
            self._deliver(version, name, picture, notes, time_axis)

    # ---- stopper ---------------------------------------------------------------------
    def stopper(self) -> None:
        """
        ---- Summary ----
        Method to stop the thread and wait until it has finished its current preview.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Stops the thread (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        with self._condition:
            self._is_stopped = True
            self._condition.notify_all()
        if self.is_alive() and threading.current_thread() is not self:
            self.join()

    # ---- wanted_setter ---------------------------------------------------------------
    def wanted_setter(self, wanted: int) -> None:
        """
        ---- Summary ----
        Method to say which file is being looked at, so it and the ones beside it are
        drawn next if they have not been drawn with the current settings.

        ---- Inputs ----
        wanted : int
            Index of the file.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the order of the work (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        with self._condition:
            self._wanted = wanted
            self._condition.notify_all()
