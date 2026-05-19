Here’s everything that was added or changed for v2.13.1:

Line 40 — new import

from PyQt6.QtGui import QAction


Lines 99–101 — new constant

GITHUB_RAW_URL = (
    "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/sprintmate.py"
)


Lines 2127–2134 — Help menu wired into the menu bar

_help_menu = self.menuBar().addMenu("Help")
_upd_act = QAction("Check for Updates…", self)
_upd_act.triggered.connect(self._check_for_updates)
_help_menu.addAction(_upd_act)
_help_menu.addSeparator()
_about_act = QAction("About SprintMate", self)
_about_act.triggered.connect(self._show_about)
_help_menu.addAction(_about_act)


Lines 2170–2254 — filter bar rebuilt as two rows

Row 1 (selection): PROJECT → BOARD → SPRINT → Load Stories → COMPARE → compare combo → ⇆ Compare
Row 2 (actions + filters): New Story · Bulk Create · Import · Export → [stretch] → ASSIGNEE · search

The old single fb_layout = QHBoxLayout(filterbar) is replaced by fb_outer = QVBoxLayout(filterbar) containing fb_row1 and fb_row2.

Lines 3989–4044 — four new methods

def _check_for_updates(self): ...        # dispatches fetch to background thread
def _fetch_remote_version() -> str: ...  # @staticmethod — fetches + parses remote APP_VERSION
def _on_update_result(self, remote_version): ...  # shows up-to-date or update-available dialog
def _show_about(self): ...               # About dialog

