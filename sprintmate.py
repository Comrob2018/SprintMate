"""
SprintMate - PyQt6 Desktop Application
Team sprint story manager — assignees, story points, transitions, and more.
"""

import sys
import csv
import io
import json
import re
import ssl
import time
import base64
import webbrowser
import urllib.request
import urllib.parse
import urllib.error
from datetime import date

try:
    import keyring
    import keyring.errors
    _KEYRING_AVAILABLE = True
except ImportError:
    _KEYRING_AVAILABLE = False

_KEYRING_SERVICE = "SprintMate"
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QFrame, QScrollArea, QDialog, QDialogButtonBox, QMessageBox,
    QGroupBox, QFormLayout, QListWidget, QListWidgetItem, QMenu,
    QAbstractItemView, QProgressBar, QStatusBar,
    QTabWidget, QDateEdit, QFileDialog, QRadioButton, QTextBrowser,
    QSizePolicy, QToolButton, QScrollArea as QScrollAreaW,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QDate, QTimer, QSettings, QModelIndex,
    QMimeData, QPoint, QByteArray,
)
from PyQt6.QtGui import QAction
from PyQt6.QtGui import (
    QColor, QPalette, QKeySequence, QShortcut, QDrag, QPixmap,
    QPainter, QFont,
)
FIBONACCI   = [0, 1, 2, 3, 5, 8, 13, 21]
PRIORITIES  = ["Highest", "High", "Medium", "Low", "Lowest"]
COMMENT_TEMPLATES = ["Blocked by: ", "Ready for review.", "Carried to next sprint.", "In progress — ETA: ", "Merged to main."]

# ── Table column indices ──────────────────────────────────────────────────────
COL_KEY         = 0
COL_SUMMARY     = 1
COL_ASSIGNEE    = 2
COL_STATUS      = 3
COL_DUE_DATE    = 4
COL_STORY_PTS   = 5
COL_PRIORITY    = 6
COL_ISSUE_TYPE  = 7
COL_FEATURE_LNK = 8

# Columns always visible (not in the right-click toggle menu)
COLS_LOCKED = {COL_KEY, COL_SUMMARY}

# Columns visible by default
COLS_DEFAULT_VISIBLE = {COL_KEY, COL_SUMMARY, COL_ASSIGNEE, COL_STATUS, COL_DUE_DATE}

# All togglable columns: (index, header label)
COLS_TOGGLABLE = [
    (COL_ASSIGNEE,    "ASSIGNEE"),
    (COL_STATUS,      "STATUS"),
    (COL_DUE_DATE,    "DUE DATE"),
    (COL_STORY_PTS,   "PTS"),
    (COL_PRIORITY,    "PRIORITY"),
    (COL_ISSUE_TYPE,  "TYPE"),
    (COL_FEATURE_LNK, "FEATURE LINK"),
]

DARK_BG      = "#0D1117"
PANEL_BG     = "#161B22"
CARD_BG      = "#1C2128"
BORDER       = "#30363D"
ACCENT_BLUE  = "#388BFD"
ACCENT_CYAN  = "#39D5F5"
ACCENT_GREEN = "#3FB950"
ACCENT_ORANGE   = "#F78166"
TEXT_PRI     = "#E6EDF3"
TEXT_SEC     = "#8B949E"
TEXT_DIM     = "#484F58"
HOVER_BG     = "#21262D"
SEL_BG       = "#1F3350"

STATUS_COLORS = {
    "To Do":       TEXT_SEC,
    "In Progress": ACCENT_BLUE,
    "Done":        ACCENT_GREEN,
    "In Review":   ACCENT_CYAN,
    "Blocked":     ACCENT_ORANGE,
}

APP_VERSION  = "2.25.3"
GITHUB_RAW_URL = (
    "https://raw.githubusercontent.com/Comrob2018/SprintMate/main/sprintmate.py"
)

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRI};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
QLabel {{
    color: {TEXT_PRI};
    background: transparent;
}}
QLabel#dim {{
    color: {TEXT_SEC};
    font-size: 11px;
}}
QLabel#heading {{
    color: {ACCENT_CYAN};
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QLabel#subheading {{
    color: {TEXT_SEC};
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: {TEXT_PRI};
    padding: 6px 10px;
    selection-background-color: {ACCENT_BLUE};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {ACCENT_BLUE};
}}
QLineEdit::placeholder {{
    color: {TEXT_DIM};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {TEXT_SEC};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    selection-background-color: {SEL_BG};
    color: {TEXT_PRI};
    outline: none;
}}
QPushButton {{
    background-color: {PANEL_BG};
    color: {TEXT_PRI};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 16px;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {HOVER_BG};
    border-color: {ACCENT_BLUE};
    color: {ACCENT_CYAN};
}}
QPushButton:pressed {{
    background-color: {SEL_BG};
}}
QPushButton#save_btn {{
    background-color: #0E2A30;
    border: 2px solid {ACCENT_CYAN};
    color: {ACCENT_CYAN};
    font-weight: bold;
    font-size: 13px;
}}
QPushButton#save_btn:hover {{
    background-color: {ACCENT_CYAN};
    color: {DARK_BG};
}}
QPushButton#save_btn:pressed {{
    background-color: #2AB8D4;
    color: {DARK_BG};
}}
QPushButton#save_btn:disabled {{
    background-color: #091518;
    border-color: {TEXT_DIM};
    color: {TEXT_DIM};
}}
QPushButton#toolbar_btn {{
    background-color: #0E2A30;
    border: 1px solid {ACCENT_CYAN};
    color: {ACCENT_CYAN};
}}
QPushButton#toolbar_btn:hover {{
    background-color: #163E47;
    border-color: {ACCENT_CYAN};
    color: #ffffff;
}}
QPushButton#toolbar_btn:pressed {{
    background-color: #0A1E23;
}}
QPushButton#toolbar_btn:disabled {{
    background-color: #091518;
    border-color: {TEXT_DIM};
    color: {TEXT_DIM};
}}
QPushButton#primary {{
    background-color: {ACCENT_BLUE};
    color: #ffffff;
    border: none;
    font-weight: bold;
}}
QPushButton#primary:hover {{
    background-color: #4D9FFF;
    color: #ffffff;
}}
QPushButton#success {{
    background-color: {ACCENT_GREEN};
    color: #000000;
    border: none;
    font-weight: bold;
}}
QPushButton#success:hover {{
    background-color: #52C55E;
    color: #000000;
}}
QPushButton#danger {{
    background-color: transparent;
    color: {ACCENT_ORANGE};
    border: 1px solid {ACCENT_ORANGE};
}}
QPushButton#danger:hover {{
    background-color: {ACCENT_ORANGE};
    color: #000000;
}}
QTableWidget {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    color: {TEXT_PRI};
    selection-background-color: {SEL_BG};
    outline: none;
}}
QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {BORDER};
}}
QTableWidget::item:selected {{
    background-color: {SEL_BG};
    color: {ACCENT_CYAN};
}}
QTableWidget::item:hover {{
    background-color: {HOVER_BG};
}}
QHeaderView::section {{
    background-color: {CARD_BG};
    color: {TEXT_SEC};
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid {BORDER};
    padding: 8px 12px;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QScrollBar:vertical {{
    background: {DARK_BG};
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_SEC};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {DARK_BG};
    height: 8px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 4px;
}}
QFrame#card {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QFrame#sidebar {{
    background-color: {PANEL_BG};
    border-right: 1px solid {BORDER};
}}
QFrame#topbar {{
    background-color: {PANEL_BG};
    border-bottom: 1px solid {BORDER};
}}
QStatusBar {{
    background-color: {PANEL_BG};
    border-top: 1px solid {BORDER};
    color: {TEXT_SEC};
    font-size: 11px;
}}
QProgressBar {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {ACCENT_BLUE};
    border-radius: 4px;
}}
QSplitter::handle {{
    background-color: {BORDER};
    width: 1px;
}}
QGroupBox {{
    color: {TEXT_SEC};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-size: 11px;
    letter-spacing: 1px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: {ACCENT_CYAN};
}}
QDialog {{
    background-color: {DARK_BG};
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    background-color: {DARK_BG};
}}
QTabBar::tab {{
    background-color: {PANEL_BG};
    color: {TEXT_SEC};
    border: 1px solid {BORDER};
    border-bottom: none;
    padding: 8px 24px;
    font-size: 12px;
    letter-spacing: 1px;
    min-width: 140px;
}}
QTabBar::tab:selected {{
    background-color: {DARK_BG};
    color: {ACCENT_CYAN};
    border-bottom: 2px solid {ACCENT_BLUE};
}}
QTabBar::tab:hover:!selected {{
    background-color: {HOVER_BG};
    color: {TEXT_PRI};
}}
"""


# ── Jira API client ───────────────────────────────────────────────────────────
class JiraClient:
    """Supports both Jira Cloud (Basic auth, API v3) and Data Center/Server (Bearer PAT, API v2)."""
    MODE_SECONDARY = "Secondary"
    MODE_PRIMARY     = "Primary"

    # mappings
    _FIELD_MAP = {
        MODE_PRIMARY : {
            "story_point": "customfield_10006",
            "feature_link": "customfield_10000"
        },
        MODE_SECONDARY : {
            "story_point": "customfield_10106",
            "feature_link": "customfield_10100"
        },
    }

    def __init__(self, base_url, token, mode=MODE_SECONDARY, email=""):
        self.api_version = "2"  # Both are Data Center
        self.mode = mode
        self.base_url = base_url.rstrip("/")
        fields = self._FIELD_MAP.get(mode)
        self.story_point_field_id = fields.get("story_point")
        self.feature_link_field_id = fields.get("feature_link")
        auth = f"Bearer {token}"
        self.headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, body=None):
        url = f"{self.base_url}/rest/api/{self.api_version}/{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        last_exc = None
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    raw = resp.read().decode()
                    if not raw:
                        return {}
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        preview = raw[:200].replace("\n", " ")
                        raise RuntimeError(
                            f"Jira returned a non-JSON response — your session may have "
                            f"expired or the URL is misconfigured.\nPreview: {preview}"
                        )
            except urllib.error.HTTPError as e:
                body_bytes = e.read().decode(errors="replace")
                try:
                    err_json = json.loads(body_bytes)
                    messages = err_json.get("errorMessages") or list(err_json.get("errors", {}).values())
                    detail = "; ".join(str(m) for m in messages) if messages else body_bytes
                except (json.JSONDecodeError, AttributeError):
                    detail = body_bytes
                raise RuntimeError(f"HTTP {e.code}: [{method} {url}] {detail}")
            except ssl.SSLError as e:
                raise RuntimeError(
                    f"SSL certificate verification failed connecting to {self.base_url}.\n"
                    f"If your Jira instance uses a self-signed or corporate CA certificate, "
                    f"ensure it is trusted by your system's certificate store.\n"
                    f"Details: {e}"
                )
            except (urllib.error.URLError, OSError) as e:
                if attempt == 0:
                    last_exc = e
                    time.sleep(1)
                    continue
                raise RuntimeError(f"Network error [{method} {url}]: {e}") from last_exc
        raise RuntimeError(f"Network error [{method} {url}]: {last_exc}")

    def get_projects(self):
        url = f"{self.base_url}/rest/api/{self.api_version}/project?maxResults=100&orderBy=name"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                return result if isinstance(result, list) else result.get("values", [])
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} [GET {url}]: {e.read().decode()}")

    # All known story point field IDs across Jira DC configurations
    _SP_FALLBACKS = [
        "customfield_10016", "customfield_10006", "customfield_10106",
        "customfield_10028", "customfield_10004", "story_points",
    ]

    def get_story_points(self, fields: dict):
        """Read story points from a fields dict, trying the detected field first
        then all known fallback field IDs. Returns a float or None."""
        candidates = [self.story_point_field_id] + [
            f for f in self._SP_FALLBACKS if f != self.story_point_field_id
        ]
        for key in candidates:
            val = fields.get(key)
            if val is not None:
                try:
                    return float(val)
                except (TypeError, ValueError):
                    continue
        return None

    def get_sprint_detail(self, sprint_id: int) -> dict:
        """Return full sprint metadata including startDate and endDate."""
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return {}

    def create_sprint(self, board_id: int, name: str,
                      start_date: str = "", end_date: str = "",
                      goal: str = "") -> dict:
        """Create a new sprint on the given board.

        Dates should be ISO-8601 with timezone, e.g. '2026-06-23T09:00:00.000Z'.
        Returns the created sprint dict (includes 'id').
        """
        body: dict = {"name": name, "originBoardId": board_id}
        if start_date:
            body["startDate"] = start_date
        if end_date:
            body["endDate"] = end_date
        if goal:
            body["goal"] = goal
        url  = f"{self.base_url}/rest/agile/1.0/sprint"
        data = json.dumps(body).encode()
        req  = urllib.request.Request(url, data=data, headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} creating sprint: {e.read().decode(errors='replace')}")

    def update_sprint(self, sprint_id: int, **fields) -> dict:
        """Update sprint fields (name, state, startDate, endDate, goal, completeDate).

        Pass state='active' to start, state='closed' to close.
        Uses POST (Jira DC standard); falls back to PUT if POST returns 405.
        """
        body = {k: v for k, v in fields.items() if v is not None}
        url  = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}"
        data = json.dumps(body).encode()
        for method in ("POST", "PUT"):
            req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return json.loads(resp.read().decode()) if resp.length else {}
            except urllib.error.HTTPError as e:
                if e.code == 405 and method == "POST":
                    continue   # try PUT
                raise RuntimeError(
                    f"HTTP {e.code} updating sprint {sprint_id}: {e.read().decode(errors='replace')}"
                )
        return {}

    def rank_issue(self, issue_key: str, rank_before_key: str = "", rank_after_key: str = "") -> None:
        """Re-rank an issue relative to another. Uses the Agile API rank endpoint."""
        body: dict = {"issues": [issue_key]}
        if rank_before_key:
            body["rankBeforeIssue"] = rank_before_key
        elif rank_after_key:
            body["rankAfterIssue"] = rank_after_key
        else:
            return
        url = f"{self.base_url}/rest/agile/1.0/issue/rank"
        data = json.dumps(body).encode()
        req  = urllib.request.Request(url, data=data, headers=self.headers, method="PUT")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp.read()
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} ranking issue: {e.read().decode(errors='replace')}")

    def get_velocity_history(self, board_id: int, num_sprints: int = 6) -> list:
        """Fetch closed sprints and compute points done per sprint for velocity chart."""
        sp     = self.story_point_field_id
        url    = (f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"
                  f"?state=closed&maxResults={num_sprints}&startAt=0")
        req    = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                sprints = json.loads(resp.read().decode()).get("values", [])
        except Exception:
            return []
        # Most recent first from Jira — reverse to chronological for display
        sprints = list(reversed(sprints[-num_sprints:]))
        result  = []
        for sprint in sprints:
            sid   = sprint.get("id")
            name  = sprint.get("name", "")
            issues = self.get_sprint_issues(board_id, sid)
            total_pts = done_pts = 0
            for iss in issues:
                f       = iss.get("fields", {})
                pts_raw = next(
                    (f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS) if f.get(k) is not None),
                    None,
                )
                try:
                    pts = int(float(pts_raw)) if pts_raw is not None else 0
                except (TypeError, ValueError):
                    pts = 0
                total_pts += pts
                if (f.get("status") or {}).get("name", "") == "Done":
                    done_pts += pts
            result.append({
                "name":      name,
                "total_pts": total_pts,
                "done_pts":  done_pts,
                "n_total":   len(issues),
                "n_done":    sum(1 for i in issues
                                 if (i.get("fields", {}).get("status") or {}).get("name") == "Done"),
            })
        return result

    def get_boards(self, project_key: str):
        url = f"{self.base_url}/rest/agile/1.0/board?projectKeyOrId={project_key}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode()).get("values", [])
        except urllib.error.HTTPError:
            return []
        except Exception:
            return []

    def get_all_sprints(self, board_id: int) -> list:
        """Fetch all sprints (active, future, closed) for a board."""
        all_sprints = []
        start = 0
        max_results = 50
        while True:
            url = (f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"
                   f"?maxResults={max_results}&startAt={start}")
            req = urllib.request.Request(url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())
            except Exception:
                break
            batch = data.get("values", [])
            all_sprints.extend(batch)
            if data.get("isLast", True) or len(batch) < max_results:
                break
            start += max_results
        return all_sprints

    def get_issues_for_people_report(self, assignees: list[str],
                                     date_from: str = "", date_to: str = "",
                                     sprint_id: int = 0, board_id: int = 0) -> list:
        """Fetch all issues assigned to the given users within a date range or sprint."""
        sp = self.story_point_field_id
        fields = ",".join([
            "summary", "assignee", "status", "priority", "issuetype",
            "duedate", sp, "created", "resolutiondate", "comment",
        ])
        assignee_jql = " OR ".join(f'assignee = "{a}"' for a in assignees)
        if sprint_id and board_id:
            jql = f"({assignee_jql}) AND sprint = {sprint_id}"
        elif date_from and date_to:
            jql = f'({assignee_jql}) AND updated >= "{date_from}" AND updated <= "{date_to}"'
        elif date_from:
            jql = f'({assignee_jql}) AND updated >= "{date_from}"'
        elif date_to:
            jql = f'({assignee_jql}) AND updated <= "{date_to}"'
        else:
            jql = f"({assignee_jql})"
        jql += " ORDER BY assignee ASC, updated DESC"

        all_issues = []
        start = 0
        max_results = 100
        while True:
            encoded = urllib.parse.quote(jql)
            url = (f"{self.base_url}/rest/api/{self.api_version}/search"
                   f"?jql={encoded}&maxResults={max_results}&startAt={start}&fields={fields}")
            req = urllib.request.Request(url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}")
            batch = data.get("issues", [])
            all_issues.extend(batch)
            if len(batch) < max_results:
                break
            start += max_results
        return all_issues

    def get_sprints(self, board_id: int):
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint?state=active,future&maxResults=20"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode()).get("values", [])
        except Exception:
            return []

    def get_sprint_issues(self, board_id: int, sprint_id: int):
        sp = self.story_point_field_id
        fl = self.feature_link_field_id
        fields = ",".join([
            "summary", "assignee", "status", "priority", "description",
            "comment", "issuetype", sp, fl, "duedate",
            "sprint", "closedSprints", "customfield_10020", "issuelinks"
        ])
        max_results = 100
        start = 0
        all_issues = []
        while True:
            url = (f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}"
                   f"/issue?maxResults={max_results}&startAt={start}&fields={fields}")
            req = urllib.request.Request(url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    raw = resp.read().decode()
                    data = json.loads(raw)
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="replace")
                try:
                    err_json = json.loads(body)
                    messages = err_json.get("errorMessages") or list(err_json.get("errors", {}).values())
                    detail = "; ".join(str(m) for m in messages) if messages else body
                except (json.JSONDecodeError, AttributeError):
                    detail = body
                raise RuntimeError(f"HTTP {e.code} loading sprint issues: {detail}")
            except json.JSONDecodeError:
                raise RuntimeError(
                    "Jira returned a non-JSON response while loading sprint issues — "
                    "your session may have expired or the URL is misconfigured."
                )
            batch = data.get("issues", [])
            all_issues.extend(batch)
            if len(batch) < max_results:
                break
            start += max_results
        return all_issues

    def search_issues_jql(self, jql: str, fields: str = "summary,assignee,status"):
        encoded = urllib.parse.quote(jql)
        url = (f"{self.base_url}/rest/api/{self.api_version}/"
            f"search?jql={encoded}&maxResults=50&fields={fields}")
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode()).get("issues", [])
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} [JQL search]: {e.read().decode(errors='replace')}")
        except (urllib.error.URLError, OSError) as e:
            raise RuntimeError(f"Network error [JQL search]: {e}")

    def get_issue_transitions(self, issue_key: str):
        return self._request("GET", f"issue/{issue_key}/transitions").get("transitions", [])

    def transition_issue(self, issue_key: str, transition_id: str):
        self._request("POST", f"issue/{issue_key}/transitions", {"transition": {"id": transition_id}})

    def get_issue_types(self, project_key: str):
        try:
            result = self._request("GET", f"project/{project_key}")
            return result.get("issueTypes", [])
        except Exception:
            return []

    def move_to_sprint(self, issue_key: str, sprint_id: int):
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        body = json.dumps({"issues": [issue_key]}).encode()
        req = urllib.request.Request(url, data=body, headers=self.headers, method="POST")
        try:
            urllib.request.urlopen(req, timeout=15)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode()}")

    def update_issue(self, issue_key: str, fields: dict):
        self._request("PUT", f"issue/{issue_key}", {"fields": fields})

    def add_comment(self, issue_key: str, text: str):
        body = {"body": text}
        self._request("POST", f"issue/{issue_key}/comment", body)

    def test_connection(self):
        return self._request("GET", "myself")

    def create_issue(
        self,
        project_key: str,
        summary: str,
        issuetype_id: str,
        description: str = "",
        assignee_id: str | None = None,
        priority: str | None = None,
        story_points: int | None = None,
        sprint_id: int | None = None,
        due_date: str | None = None,
        feature_link: str | None = None,
    ) -> dict:
        fields: dict = {
            "project":   {"key": project_key},
            "summary":   summary,
            "issuetype": {"id": issuetype_id},
        }
        if description:
            fields["description"] = description
        if assignee_id:
            fields["assignee"] = {"name": assignee_id}
        if priority:
            fields["priority"] = {"name": priority}
        if story_points is not None:
            fields[self.story_point_field_id] = story_points
        if feature_link is not None:
            fields[self.feature_link_field_id] = feature_link
        if due_date:
            fields["duedate"] = due_date
        result = self._request("POST", "issue", {"fields": fields})
        if sprint_id and result.get("key"):
            try:
                self.move_to_sprint(result["key"], sprint_id)
            except Exception:
                pass
        return result

    def search_users(self, query: str):
        all_users = []
        start = 0
        max_results = 200
        while True:
            encoded = urllib.parse.quote(query or ".")
            url = (f"{self.base_url}/rest/api/{self.api_version}/user/search"
                f"?username={encoded}&maxResults={max_results}&startAt={start}")
            req = urllib.request.Request(url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    batch = json.loads(resp.read().decode())
                    if not isinstance(batch, list) or not batch:
                        break
                    all_users.extend(batch)
                    if len(batch) < max_results:
                        break
                    start += max_results
            except Exception:
                break
        return all_users

    def clone_issue(self, project_key: str, summary: str,
                    description: str = "", assignee_name: str = "",
                    issue_type: str = "Story") -> dict:
        """Create a new issue — used as the target of a clone operation."""
        fields: dict = {
            "project":   {"key": project_key},
            "summary":   summary,
            "issuetype": {"name": issue_type},
        }
        if description:
            fields["description"] = description
        if assignee_name:
            fields["assignee"] = {"name": assignee_name}
        return self._request("POST", "issue", {"fields": fields})

    def archive_issues(self, issue_keys: list[str]) -> dict:
        """Archive one or more issues. Requires Jira Data Center 8.1+."""
        url = f"{self.base_url}/rest/api/{self.api_version}/issue/archive"
        headers = dict(self.headers)
        headers["Accept"] = "text/plain"
        body = json.dumps(issue_keys).encode()
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode(errors="replace")
                errors = [l for l in raw.splitlines() if l.strip() and "error" in l.lower()]
                return {"errors": errors}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} archiving issues: {e.read().decode(errors='replace')}")

    def unarchive_issues(self, issue_keys: list[str]) -> dict:
        """Unarchive one or more previously archived issues."""
        url = f"{self.base_url}/rest/api/{self.api_version}/issue/unarchive"
        headers = dict(self.headers)
        headers["Accept"] = "text/plain"
        body = json.dumps(issue_keys).encode()
        req = urllib.request.Request(url, data=body, headers=headers, method="PUT")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode(errors="replace")
                errors = [l for l in raw.splitlines() if l.strip() and "error" in l.lower()]
                return {"errors": errors}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} unarchiving issues: {e.read().decode(errors='replace')}")

    def edit_comment(self, issue_key: str, comment_id: str, new_text: str) -> dict:
        return self._request(
            "PUT", f"issue/{issue_key}/comment/{comment_id}", {"body": new_text}
        )

    def delete_comment(self, issue_key: str, comment_id: str) -> None:
        url = f"{self.base_url}/rest/api/{self.api_version}/issue/{issue_key}/comment/{comment_id}"
        req = urllib.request.Request(url, headers=self.headers, method="DELETE")
        try:
            urllib.request.urlopen(req, timeout=15)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} deleting comment {comment_id}: {e.read().decode(errors='replace')}")

    def attach_file(self, issue_key: str, file_path: str) -> dict:
        """Upload a file as an attachment to a Jira issue using multipart/form-data."""
        import os
        url = f"{self.base_url}/rest/api/{self.api_version}/issue/{issue_key}/attachments"
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        boundary = "----SprintMateUpload7f3a9b"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

        headers = dict(self.headers)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        headers["X-Atlassian-Token"] = "no-check"
        headers.pop("Accept", None)

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode(errors="replace")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            raise RuntimeError(f"HTTP {e.code} attaching file: {detail}")

    def bulk_create_issues(self, project_key: str, rows: list[dict],
                           progress_cb=None) -> list[dict]:
        results = []
        total = len(rows)
        for i, row in enumerate(rows, start=1):
            result = {"row": i, "summary": row.get("summary", ""), "key": None, "error": None}
            try:
                created = self.create_issue(
                    project_key=project_key,
                    summary=row["summary"],
                    issuetype_id=row["issue_type_id"],
                    description=row.get("description", ""),
                    assignee_id=row.get("assignee_id"),
                    priority=row.get("priority"),
                    story_points=row.get("story_points"),
                    sprint_id=row.get("sprint_id"),
                    due_date=row.get("due_date"),
                )
                errors = created.get("errorMessages") or list(created.get("errors", {}).values())
                if errors:
                    result["error"] = "; ".join(str(e) for e in errors)
                else:
                    result["key"] = created.get("key", "")
            except Exception as e:
                result["error"] = str(e)
            results.append(result)
            if progress_cb:
                try:
                    progress_cb(i, total)
                except Exception:
                    pass
        return results


# ── New Story Dialog ─────────────────────────────────────────────────────────
class NewStoryDialog(QDialog):
    def __init__(self, project_key: str, members: list, issue_types: list,
                 sprints: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Story")
        self.setMinimumWidth(520)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        self._project_key = project_key
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("＋  CREATE NEW STORY")
        title.setObjectName("heading")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.summary_edit = QLineEdit()
        self.summary_edit.setPlaceholderText("Story summary (required)…")
        form.addRow("Summary *:", self.summary_edit)

        self.type_combo = QComboBox()
        for it in issue_types:
            self.type_combo.addItem(it.get("name", "?"), it.get("name"))
        for i in range(self.type_combo.count()):
            if self.type_combo.itemText(i).lower() == "story":
                self.type_combo.setCurrentIndex(i)
                break
        form.addRow("Issue Type:", self.type_combo)

        self.priority_combo = QComboBox()
        for p in PRIORITIES:
            self.priority_combo.addItem(p, p)
        form.addRow("Priority:", self.priority_combo)

        # Story points (Fibonacci) with amber warning for 13 and 21
        self.points_combo = QComboBox()
        self.points_combo.addItem("— Not set —", None)
        for v in FIBONACCI:
            label = str(v)
            if v in (13, 21):
                label += "  — consider splitting"
            idx = self.points_combo.count()
            self.points_combo.addItem(label, v)
            if v in (13, 21):
                self.points_combo.setItemData(idx, QColor("#E3B341"), Qt.ItemDataRole.ForegroundRole)
        form.addRow("Story Points:", self.points_combo)

        self.assignee_combo = QComboBox()
        self.assignee_combo.addItem("— Unassigned —", None)
        for m in members:
            uid = m.get("name") or m.get("accountId")
            self.assignee_combo.addItem(m.get("displayName", "?"), uid)
        form.addRow("Assignee:", self.assignee_combo)

        self.sprint_combo = QComboBox()
        self.sprint_combo.addItem("— Backlog (no sprint) —", None)
        for s in sprints:
            state = s.get("state", "")
            self.sprint_combo.addItem(f"[{state.upper()}] {s['name']}", s["id"])
        for i in range(self.sprint_combo.count()):
            if "[ACTIVE]" in self.sprint_combo.itemText(i):
                self.sprint_combo.setCurrentIndex(i)
                break
        form.addRow("Sprint:", self.sprint_combo)

        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("yyyy-MM-dd")
        self.due_date.setDate(QDate.currentDate())
        form.addRow("Due Date:", self.due_date)

        layout.addLayout(form)

        desc_grp = QGroupBox("DESCRIPTION")
        desc_layout = QVBoxLayout(desc_grp)
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Optional description…")
        self.desc_edit.setMinimumHeight(90)
        self.desc_edit.setMaximumHeight(140)
        desc_layout.addWidget(self.desc_edit)
        layout.addWidget(desc_grp)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("＋  Create Story")
        btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("save_btn")
        btns.accepted.connect(self._validate_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _validate_and_accept(self):
        if not self.summary_edit.text().strip():
            QMessageBox.warning(self, "Required", "Please enter a summary for the story.")
            self.summary_edit.setFocus()
            return
        self.accept()

    def get_values(self) -> dict:
        return {
            "summary":      self.summary_edit.text().strip(),
            "issue_type":   self.type_combo.currentData(),
            "priority":     self.priority_combo.currentData(),
            "story_points": self.points_combo.currentData(),
            "assignee_id":  self.assignee_combo.currentData(),
            "sprint_id":    self.sprint_combo.currentData(),
            "due_date":     self.due_date.date().toString("yyyy-MM-dd"),
            "description":  self.desc_edit.toPlainText().strip(),
        }


# ── Bulk Create Dialog ────────────────────────────────────────────────────────
class BulkCreateDialog(QDialog):
    """
    Preview dialog for bulk story creation from a CSV file.

    Expected CSV columns (header row required, order-insensitive):
        summary      — required
        issue_type   — optional (falls back to first available type)
        priority     — optional (Medium if blank)
        story_points — optional (integer or blank)
        assignee     — optional (display name matched case-insensitively)
        sprint       — optional (sprint name matched case-insensitively)
        due_date     — optional (yyyy-MM-dd; today if blank)
        description  — optional

    Rows with a blank summary are flagged as invalid and excluded from creation.
    """

    _COL_ROW      = 0
    _COL_SUMMARY  = 1
    _COL_TYPE     = 2
    _COL_PRIORITY = 3
    _COL_PTS      = 4
    _COL_ASSIGNEE = 5
    _COL_SPRINT   = 6
    _COL_DUE      = 7
    _COL_STATUS   = 8

    TEMPLATE_HEADERS = [
        "summary", "issue_type", "priority", "story_points",
        "assignee", "sprint", "due_date", "description",
    ]

    def __init__(self, rows: list[dict], members: list, issue_types: list,
                 sprints: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Create Stories — Preview")
        self.setMinimumSize(1000, 580)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        self._raw_rows    = rows
        self._members     = {m.get("displayName", "").lower(): m for m in members}
        self._issue_types = {it.get("name", "").lower(): it for it in issue_types}
        self._sprints     = {s.get("name", "").lower(): s for s in sprints}
        self._default_type = issue_types[0].get("name", "") if issue_types else ""
        self._today       = date.today().strftime("%Y-%m-%d")

        self._resolved    = []
        self._valid_count = 0

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("＋＋  BULK CREATE STORIES — PREVIEW")
        title.setObjectName("heading")
        layout.addWidget(title)

        self._summary_lbl = QLabel("")
        self._summary_lbl.setObjectName("dim")
        self._summary_lbl.setWordWrap(True)
        layout.addWidget(self._summary_lbl)

        self._table = QTableWidget()
        self._table.setColumnCount(9)
        self._table.setHorizontalHeaderLabels([
            "#", "SUMMARY", "TYPE", "PRIORITY", "PTS",
            "ASSIGNEE", "SPRINT", "DUE DATE", "STATUS",
        ])
        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(self._COL_ROW,      QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(self._COL_SUMMARY,  QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(self._COL_TYPE,     QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(self._COL_PRIORITY, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(self._COL_PTS,      QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(self._COL_ASSIGNEE, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(self._COL_SPRINT,   QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(self._COL_DUE,      QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(self._COL_STATUS,   QHeaderView.ResizeMode.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setShowGrid(False)
        layout.addWidget(self._table, 1)

        self._warn_lbl = QLabel("")
        self._warn_lbl.setStyleSheet(f"color: {ACCENT_ORANGE}; font-size: 11px;")
        self._warn_lbl.setWordWrap(True)
        layout.addWidget(self._warn_lbl)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._create_btn = btns.button(QDialogButtonBox.StandardButton.Ok)
        self._create_btn.setText("▶  Create Stories")
        self._create_btn.setObjectName("save_btn")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._build_preview()

    def _resolve_row(self, raw: dict) -> dict:
        issues = []
        summary = raw.get("summary", "").strip()
        if not summary:
            issues.append("Missing summary — row will be skipped")

        raw_type = raw.get("issue_type", "").strip().lower()
        if raw_type and raw_type in self._issue_types:
            itype = self._issue_types[raw_type]
        elif self._issue_types:
            itype = next(iter(self._issue_types.values()))
            if raw_type:
                issues.append(f"Unknown type '{raw.get('issue_type')}' — using '{itype.get('name')}'")
        else:
            itype = {"name": "", "id": ""}

        raw_pri = raw.get("priority", "").strip()
        if raw_pri and raw_pri in PRIORITIES:
            priority = raw_pri
        else:
            priority = "Medium"
            if raw_pri:
                issues.append(f"Unknown priority '{raw_pri}' — using 'Medium'")

        raw_pts = raw.get("story_points", "").strip()
        story_points = None
        if raw_pts:
            try:
                story_points = int(float(raw_pts))
            except ValueError:
                issues.append(f"Invalid story points '{raw_pts}' — leaving unset")

        raw_assignee = raw.get("assignee", "").strip()
        member = None
        if raw_assignee:
            member = self._members.get(raw_assignee.lower())
            if not member:
                issues.append(f"Assignee '{raw_assignee}' not found — leaving unassigned")

        raw_sprint = raw.get("sprint", "").strip()
        sprint = None
        if raw_sprint:
            sprint = self._sprints.get(raw_sprint.lower())
            if not sprint:
                issues.append(f"Sprint '{raw_sprint}' not found — leaving unassigned")

        raw_due = raw.get("due_date", "").strip()
        if raw_due:
            try:
                date.fromisoformat(raw_due)
                due_date = raw_due
            except ValueError:
                issues.append(f"Invalid due date '{raw_due}' — using today")
                due_date = self._today
        else:
            due_date = self._today

        return {
            "summary":      summary,
            "issue_type":   itype.get("name", ""),
            "issue_type_id": itype.get("id", ""),
            "priority":     priority,
            "story_points": story_points,
            "assignee_name": member.get("displayName", "") if member else "",
            "assignee_id":  (member.get("name") or member.get("accountId")) if member else None,
            "sprint_name":  sprint.get("name", "") if sprint else "",
            "sprint_id":    sprint.get("id") if sprint else None,
            "due_date":     due_date,
            "description":  raw.get("description", "").strip(),
            "_issues":      issues,
            "_valid":       bool(summary),
        }

    def _build_preview(self):
        self._resolved = [self._resolve_row(r) for r in self._raw_rows]
        self._valid_count = sum(1 for r in self._resolved if r["_valid"])
        invalid_count = len(self._resolved) - self._valid_count
        warn_count = sum(1 for r in self._resolved if r["_valid"] and r["_issues"])

        self._summary_lbl.setText(
            f"{len(self._resolved)} rows found — "
            f"{self._valid_count} valid, "
            f"{invalid_count} invalid (will be skipped), "
            f"{warn_count} with warnings."
        )

        self._table.setRowCount(0)
        for i, row in enumerate(self._resolved):
            r = self._table.rowCount()
            self._table.insertRow(r)

            is_valid = row["_valid"]
            has_warn = bool(row["_issues"])
            fg = QColor(TEXT_PRI) if is_valid else QColor(ACCENT_ORANGE)

            def cell(text, align=Qt.AlignmentFlag.AlignLeft, _fg=fg):
                item = QTableWidgetItem(str(text))
                item.setForeground(_fg)
                item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                return item

            self._table.setItem(r, self._COL_ROW,      cell(str(i + 1), Qt.AlignmentFlag.AlignCenter))
            self._table.setItem(r, self._COL_SUMMARY,  cell(row["summary"] or "— MISSING —"))
            self._table.setItem(r, self._COL_TYPE,     cell(row["issue_type"]))
            self._table.setItem(r, self._COL_PRIORITY, cell(row["priority"]))
            self._table.setItem(r, self._COL_PTS,      cell(str(row["story_points"]) if row["story_points"] is not None else "—"))
            self._table.setItem(r, self._COL_ASSIGNEE, cell(row["assignee_name"] or "—"))
            self._table.setItem(r, self._COL_SPRINT,   cell(row["sprint_name"] or "—"))
            self._table.setItem(r, self._COL_DUE,      cell(row["due_date"]))

            if not is_valid:
                status_item = QTableWidgetItem("✗  " + "; ".join(row["_issues"]))
                status_item.setForeground(QColor(ACCENT_ORANGE))
            elif has_warn:
                status_item = QTableWidgetItem("⚠  " + "; ".join(row["_issues"]))
                status_item.setForeground(QColor("#E3B341"))
            else:
                status_item = QTableWidgetItem("✓  Ready")
                status_item.setForeground(QColor(ACCENT_GREEN))
            self._table.setItem(r, self._COL_STATUS, status_item)
            self._table.setRowHeight(r, 36)

        warnings_text = ""
        if invalid_count:
            warnings_text += f"⚠  {invalid_count} row(s) with no summary will be skipped.  "
        if warn_count:
            warnings_text += f"⚠  {warn_count} row(s) have warnings — they will still be created with fallback values."
        self._warn_lbl.setText(warnings_text.strip())

        self._create_btn.setText(
            f"▶  Create {self._valid_count} Stor{'ies' if self._valid_count != 1 else 'y'}"
        )
        self._create_btn.setEnabled(self._valid_count > 0)

    def get_valid_rows(self) -> list[dict]:
        return [r for r in self._resolved if r["_valid"]]


# ── Import Comments Dialog ────────────────────────────────────────────────────
class ImportCommentsDialog(QDialog):
    def __init__(self, parsed: dict, loaded_keys: set, story_info: dict,
                 cross_keys=None, cross_map=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Comments — Preview")
        self.setMinimumWidth(860)
        self.setMinimumHeight(520)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        self._parsed     = parsed
        self._cross_map  = cross_map or {}
        cross_keys       = cross_keys or set()

        matched   = {k: v for k, v in parsed.items() if k in loaded_keys}
        unmatched = {k: v for k, v in parsed.items() if k not in loaded_keys}

        matched_count   = len(matched)
        unmatched_count = len(unmatched)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("◈  IMPORT COMMENTS PREVIEW")
        title.setObjectName("heading")
        layout.addWidget(title)

        summary_lbl = QLabel(
            f"Found {len(parsed)} entries — "
            f"{matched_count} matched to loaded stories, "
            f"{unmatched_count} not found in current sprint."
        )
        summary_lbl.setObjectName("dim")
        summary_lbl.setWordWrap(True)
        layout.addWidget(summary_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["KEY", "SUMMARY", "ASSIGNEE", "CROSS-POST TO", "COMMENT"]
        )
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        for key, entry in parsed.items():
            comment  = entry["comment"]
            summary  = entry.get("summary") or (story_info.get(key, ("", ""))[0]) or "—"
            assignee = entry.get("assignee") or (story_info.get(key, ("", ""))[1]) or "—"

            row = self.table.rowCount()
            self.table.insertRow(row)

            key_item = QTableWidgetItem(key)
            key_item.setForeground(QColor(ACCENT_CYAN))
            self.table.setItem(row, 0, key_item)

            self.table.setItem(row, 1, QTableWidgetItem(summary))
            self.table.setItem(row, 2, QTableWidgetItem(assignee))

            cross_keys = (cross_map or {}).get(key, [])
            cross_text = ", ".join(cross_keys) if cross_keys else "—"
            cross_item = QTableWidgetItem(cross_text)
            cross_item.setForeground(QColor(ACCENT_CYAN if cross_keys else TEXT_DIM))
            self.table.setItem(row, 3, cross_item)

            truncated = comment[:100] + ("…" if len(comment) > 100 else "")
            self.table.setItem(row, 4, QTableWidgetItem(truncated))
            self.table.setRowHeight(row, 36)

        layout.addWidget(self.table, 1)

        self._detail_frame = QFrame()
        self._detail_frame.setObjectName("card")
        self._detail_frame.setVisible(False)
        detail_layout = QVBoxLayout(self._detail_frame)
        detail_layout.setContentsMargins(14, 10, 14, 10)
        detail_layout.setSpacing(6)

        detail_title = QLabel("SELECTED ENTRY")
        detail_title.setObjectName("subheading")
        detail_layout.addWidget(detail_title)

        self._detail_key     = QLabel("")
        self._detail_summary = QLabel("")
        self._detail_assignee= QLabel("")
        self._detail_cross   = QLabel("")
        self._detail_comment = QTextEdit()
        self._detail_comment.setReadOnly(True)
        self._detail_comment.setMaximumHeight(70)

        for lbl in (self._detail_key, self._detail_summary,
                    self._detail_assignee, self._detail_cross):
            lbl.setWordWrap(True)
            detail_layout.addWidget(lbl)
        detail_layout.addWidget(self._detail_comment)
        layout.addWidget(self._detail_frame)
        
        selection = self.table.selectionModel()         
        cur_index = selection.currentIndex()            
        current_row = cur_index.row() if cur_index.isValid() else -1

        previous_row = -1                                

        self._current_row  = current_row
        self._previous_row = previous_row
        self.table.selectionModel().currentRowChanged.connect(self._on_row_changed)

        if unmatched:
            warn = QLabel(f"⚠  {len(unmatched)} keys not found in current sprint will be skipped.")
            warn.setStyleSheet(f"color: {ACCENT_ORANGE}; font-size: 11px;")
            layout.addWidget(warn)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(
            f"▶  Post {len(matched)} Comment{'s' if len(matched) != 1 else ''}"
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("save_btn")
        btns.button(QDialogButtonBox.StandardButton.Ok).setEnabled(len(matched) > 0)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._to_post = {k: entry["comment"] for k, entry in parsed.items() if k in loaded_keys}

    def _on_row_changed(self, current: QModelIndex, previous: QModelIndex):
        self._previous_row = self._current_row
        
        self._current_row = current.row() if current.isValid() else -1
        if not current.isValid():
            return
        
        row = self._current_row
        if row < 0:
            self._detail_frame.setVisible(False)
            return
        
        key_item = self.table.item(row, 0)
        if not key_item:
            self._detail_frame.setVisible(False)
            return

        key      = key_item.text()
        summary  = self.table.item(row, 1).text() if self.table.item(row, 1) else "—"
        assignee = self.table.item(row, 2).text() if self.table.item(row, 2) else "—"
        cross_keys = self._cross_map.get(key, [])
        cross      = ", ".join(cross_keys) if cross_keys else ""
        entry    = self._parsed.get(key, {})
        comment  = entry.get("comment", "") if isinstance(entry, dict) else entry

        self._detail_key.setText(
            f'<span style="color:{ACCENT_CYAN}; font-weight:bold;">{key}</span>'
        )
        self._detail_key.setTextFormat(Qt.TextFormat.RichText)
        self._detail_summary.setText(f"Summary:  {summary}")
        self._detail_assignee.setText(f"Assignee:  {assignee}")
        self._detail_cross.setText(
            f'Cross-post to:  <span style="color:{ACCENT_CYAN};">{cross}</span>'
            if cross else
            f'<span style="color:{TEXT_DIM};">No cross-instance match found.</span>'
        )
        self._detail_cross.setTextFormat(Qt.TextFormat.RichText)
        self._detail_comment.setPlainText(comment)
        self._detail_frame.setVisible(True)

    def get_comments(self) -> dict:
        return self._to_post


# ── Worker threads ────────────────────────────────────────────────────────────
class Worker(QThread):
    result   = pyqtSignal(object)
    error    = pyqtSignal(str)
    progress = pyqtSignal(int, int)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn, self._args, self._kwargs = fn, args, kwargs

    def run(self):
        try:
            self.result.emit(self._fn(*self._args, **self._kwargs))
        except Exception as e:
            self.error.emit(str(e))


# ── Settings dialog ───────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SprintMate — Connection Settings")
        self.setMinimumWidth(520)
        self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("⚙  SPRINTMATE — CONNECTION SETTINGS")
        title.setObjectName("heading")
        layout.addWidget(title)

        hint = QLabel("Configure each instance separately. Use the toggle to switch between them.")
        hint.setObjectName("dim")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(0)

        toggle_style = f"""
            QPushButton {{ border: 1px solid {BORDER}; border-radius: 0; padding: 6px 24px; font-size: 12px; }}
            QPushButton:checked {{ background-color: {ACCENT_BLUE}; color: #fff; border-color: {ACCENT_BLUE}; font-weight: bold; }}
            QPushButton:first-child {{ border-radius: 6px 0 0 6px; }}
            QPushButton:last-child  {{ border-radius: 0 6px 6px 0; }}
        """

        self.primary_btn = QPushButton("◈  PRIMARY")
        self.primary_btn.setCheckable(True)
        self.primary_btn.setFixedHeight(34)
        self.primary_btn.setStyleSheet(toggle_style)

        self.secondary_btn = QPushButton("◈  SECONDARY")
        self.secondary_btn.setCheckable(True)
        self.secondary_btn.setFixedHeight(34)
        self.secondary_btn.setStyleSheet(toggle_style)

        self.primary_btn.clicked.connect(lambda: self._set_mode(JiraClient.MODE_PRIMARY))
        self.secondary_btn.clicked.connect(lambda: self._set_mode(JiraClient.MODE_SECONDARY))

        mode_layout.addWidget(self.primary_btn)
        mode_layout.addWidget(self.secondary_btn)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        self.instance_lbl = QLabel("")
        self.instance_lbl.setObjectName("subheading")
        layout.addWidget(self.instance_lbl)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("e.g. Production, Staging, Dev…")
        form.addRow("Display Name:", self.display_name_edit)
        _dn_hint = QLabel("Optional. Replaces 'Primary' / 'Secondary' labels throughout the app.")
        _dn_hint.setObjectName("dim")
        _dn_hint.setWordWrap(True)
        form.addRow("", _dn_hint)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://jira.yourcompany.com")
        form.addRow("Jira URL:", self.url_edit)

        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholderText("Personal Access Token")
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("PAT Token:", self.token_edit)

        expiry_row = QHBoxLayout()
        self.expiry_edit = QLineEdit()
        self.expiry_edit.setPlaceholderText("yyyy-MM-dd  (leave blank if no expiry)")
        self.expiry_edit.setMaximumWidth(200)
        self.expiry_clear_btn = QPushButton("Clear")
        self.expiry_clear_btn.setFixedWidth(70)
        self.expiry_clear_btn.clicked.connect(lambda: self.expiry_edit.setText(""))
        expiry_row.addWidget(self.expiry_edit)
        expiry_row.addWidget(self.expiry_clear_btn)
        expiry_row.addStretch()
        form.addRow("Token Expiry:", expiry_row)

        self.default_project_edit = QLineEdit()
        self.default_project_edit.setPlaceholderText("e.g. project1")
        form.addRow("Default Project:", self.default_project_edit)
        _dp_hint = QLabel("Auto-selects this project in the dropdown on connect.")
        _dp_hint.setObjectName("dim")
        form.addRow("", _dp_hint)

        self.default_board_edit = QLineEdit()
        self.default_board_edit.setPlaceholderText("e.g. project1 board")
        form.addRow("Default Board:", self.default_board_edit)
        _db_hint = QLabel("Auto-selects this board once the project is loaded.")
        _db_hint.setObjectName("dim")
        form.addRow("", _db_hint)

        self.filter_projects_edit = QLineEdit()
        self.filter_projects_edit.setPlaceholderText("e.g. project1, project2")
        form.addRow("Filter Projects:", self.filter_projects_edit)
        _fp_hint = QLabel("Comma-separated. Only matching projects appear in the dropdown. Leave blank to show all.")
        _fp_hint.setObjectName("dim")
        _fp_hint.setWordWrap(True)
        form.addRow("", _fp_hint)

        self.filter_boards_edit = QLineEdit()
        self.filter_boards_edit.setPlaceholderText("e.g. project1 board, project2 board")
        form.addRow("Filter Boards:", self.filter_boards_edit)
        _fb_hint = QLabel("Comma-separated. Only matching boards appear in the dropdown. Leave blank to show all.")
        _fb_hint.setObjectName("dim")
        _fb_hint.setWordWrap(True)
        form.addRow("", _fb_hint)
        layout.addLayout(form)

        conn_row = QHBoxLayout()
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._test)
        conn_row.addWidget(self.test_btn)
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("dim")
        conn_row.addWidget(self.status_lbl, 1)
        layout.addLayout(conn_row)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Save")
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._data = {
            JiraClient.MODE_SECONDARY: {
                "url":            settings.get("secondary_url", ""),
                "token":          settings.get("secondary_token", ""),
                "token_expiry":   settings.get("secondary_token_expiry", ""),
                "default_project": settings.get("secondary_default_project", ""),
                "default_board":  settings.get("secondary_default_board", ""),
                "filter_projects": settings.get("secondary_filter_projects", ""),
                "filter_boards":  settings.get("secondary_filter_boards", ""),
                "display_name":   settings.get("secondary_display_name", ""),
            },
            JiraClient.MODE_PRIMARY: {
                "url":            settings.get("primary_url", ""),
                "token":          settings.get("primary_token", ""),
                "token_expiry":   settings.get("primary_token_expiry", ""),
                "default_project": settings.get("primary_default_project", ""),
                "default_board":  settings.get("primary_default_board", ""),
                "filter_projects": settings.get("primary_filter_projects", ""),
                "filter_boards":  settings.get("primary_filter_boards", ""),
                "display_name":   settings.get("primary_display_name", ""),
            },
        }
        self._set_mode(settings.get("mode", JiraClient.MODE_SECONDARY))

    def _set_mode(self, mode: str):
        if hasattr(self, "_mode"):
            self._data[self._mode]["url"]   = self.url_edit.text().strip()
            self._data[self._mode]["token"] = self.token_edit.text().strip()
            self._data[self._mode]["token_expiry"] = self.expiry_edit.text().strip()
            self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()
            self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()
            self._data[self._mode]["filter_projects"] = self.filter_projects_edit.text().strip()
            self._data[self._mode]["filter_boards"]   = self.filter_boards_edit.text().strip()
            self._data[self._mode]["display_name"]    = self.display_name_edit.text().strip()

        self._mode = mode
        is_secondary = mode == JiraClient.MODE_SECONDARY
        self.secondary_btn.setChecked(is_secondary)
        self.primary_btn.setChecked(not is_secondary)
        default_label = "SECONDARY" if is_secondary else "PRIMARY"
        custom_name   = self._data[mode].get("display_name", "").strip()
        self.instance_lbl.setText(f"{custom_name or default_label} INSTANCE")

        self.url_edit.setText(self._data[mode]["url"])
        self.token_edit.setText(self._data[mode]["token"])
        self.expiry_edit.setText(self._data[mode].get("token_expiry", ""))
        self.default_project_edit.setText(self._data[mode]["default_project"])
        self.default_board_edit.setText(self._data[mode].get("default_board", ""))
        self.filter_projects_edit.setText(self._data[mode].get("filter_projects", ""))
        self.filter_boards_edit.setText(self._data[mode].get("filter_boards", ""))
        self.display_name_edit.setText(self._data[mode].get("display_name", ""))
        self.status_lbl.setText("")

    def _test(self):
        self.status_lbl.setText("Testing…")
        self.status_lbl.setStyleSheet(f"color: {TEXT_SEC};")
        self.test_btn.setEnabled(False)
        s = self.get_settings()
        client = JiraClient(s["url"], s["token"], s["mode"], s.get("email", ""))
        worker = Worker(client.test_connection)
        worker.result.connect(self._on_test_result)
        worker.error.connect(self._on_test_error)
        self._test_worker = worker
        worker.finished.connect(lambda: setattr(self, "_test_worker", None))
        worker.start()

    def _on_test_result(self, info):
        self.test_btn.setEnabled(True)
        name = info.get("displayName", "unknown")
        self.status_lbl.setText(f"✓ Connected as {name}")
        self.status_lbl.setStyleSheet(f"color: {ACCENT_GREEN};")

    def _on_test_error(self, error: str):
        self.test_btn.setEnabled(True)
        self.status_lbl.setText(f"✗ {error[:100]}")
        self.status_lbl.setStyleSheet(f"color: {ACCENT_ORANGE};")

    def _save_and_accept(self):
        self._data[self._mode]["url"]   = self.url_edit.text().strip()
        self._data[self._mode]["token"] = self.token_edit.text().strip()
        self._data[self._mode]["token_expiry"] = self.expiry_edit.text().strip()
        self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()
        self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()
        self._data[self._mode]["filter_projects"] = self.filter_projects_edit.text().strip()
        self._data[self._mode]["filter_boards"]   = self.filter_boards_edit.text().strip()
        self._data[self._mode]["display_name"]    = self.display_name_edit.text().strip()
        self.accept()

    def get_settings(self):
        return {
            "mode":           self._mode,
            "secondary_url":   self._data[JiraClient.MODE_SECONDARY]["url"],
            "secondary_token": self._data[JiraClient.MODE_SECONDARY]["token"],
            "secondary_token_expiry": self._data[JiraClient.MODE_SECONDARY].get("token_expiry", ""),
            "secondary_display_name": self._data[JiraClient.MODE_SECONDARY].get("display_name", ""),
            "primary_url":       self._data[JiraClient.MODE_PRIMARY]["url"],
            "primary_token":     self._data[JiraClient.MODE_PRIMARY]["token"],
            "primary_token_expiry": self._data[JiraClient.MODE_PRIMARY].get("token_expiry", ""),
            "primary_display_name":  self._data[JiraClient.MODE_PRIMARY].get("display_name", ""),
            "url":   self._data[self._mode]["url"],
            "token": self._data[self._mode]["token"],
            "secondary_default_project": self._data[JiraClient.MODE_SECONDARY]["default_project"],
            "primary_default_project":     self._data[JiraClient.MODE_PRIMARY]["default_project"],
            "secondary_default_board": self._data[JiraClient.MODE_SECONDARY].get("default_board", ""),
            "primary_default_board":     self._data[JiraClient.MODE_PRIMARY].get("default_board", ""),
            "secondary_filter_projects": self._data[JiraClient.MODE_SECONDARY].get("filter_projects", ""),
            "primary_filter_projects":     self._data[JiraClient.MODE_PRIMARY].get("filter_projects", ""),
            "secondary_filter_boards":   self._data[JiraClient.MODE_SECONDARY].get("filter_boards", ""),
            "primary_filter_boards":       self._data[JiraClient.MODE_PRIMARY].get("filter_boards", ""),
        }


# ── Story edit panel ──────────────────────────────────────────────────────────
class StoryEditPanel(QFrame):
    saved   = pyqtSignal(str, dict, str, object, object)
    changed = pyqtSignal()   # emitted when any field is modified

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.current_key = None
        self._members = []
        self._sprints = []
        self._transitions = []
        self._current_sprint_id = None
        self._snapshot = {}
        self._pending_assignee = None
        self._full_comment_text = ""
        self._comments_data = []  # full comment dicts including IDs
        self._pre_save_snapshot = None
        self._sp_field = JiraClient._FIELD_MAP[JiraClient.MODE_SECONDARY]["story_point"]
        self._fl_field = "customfield_10100"
        self._base_url = ""
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        hdr = QHBoxLayout()
        self.title_lbl = QLabel("Select a story to edit")
        self.title_lbl.setObjectName("heading")
        self.title_lbl.setWordWrap(True)
        self.key_lbl = QLabel("")
        self.key_lbl.setObjectName("dim")
        self.copy_key_btn = QPushButton("⎘")
        self.copy_key_btn.setToolTip("Copy issue key to clipboard")
        self.copy_key_btn.setFixedSize(28, 28)
        self.copy_key_btn.setObjectName("dim")
        self.copy_key_btn.setEnabled(False)
        self.copy_key_btn.clicked.connect(self._copy_key)
        # ── Open in Jira button ───────────────────────────────────────────────
        self.open_jira_btn = QPushButton("⎋  Open in Jira")
        self.open_jira_btn.setToolTip("Open this issue in Jira in your browser")
        self.open_jira_btn.setFixedHeight(28)
        self.open_jira_btn.setEnabled(False)
        self.open_jira_btn.clicked.connect(self._open_in_jira)
        self.clone_btn = QPushButton("⎘  Clone")
        self.clone_btn.setToolTip("Clone this story to a project or instance")
        self.clone_btn.setFixedHeight(28)
        self.clone_btn.setEnabled(False)
        self.attach_btn = QPushButton("📎  Attach File")
        self.attach_btn.setToolTip("Upload one or more files as attachments to this issue")
        self.attach_btn.setFixedHeight(28)
        self.attach_btn.setEnabled(False)
        hdr.addWidget(self.title_lbl, 1)
        hdr.addWidget(self.key_lbl)
        hdr.addWidget(self.copy_key_btn)
        hdr.addWidget(self.open_jira_btn)
        hdr.addWidget(self.clone_btn)
        hdr.addWidget(self.attach_btn)
        layout.addLayout(hdr)

        self.status_badge = QLabel("")
        self.status_badge.setStyleSheet(f"color: {ACCENT_CYAN}; font-size:11px; letter-spacing:1px;")
        layout.addWidget(self.status_badge)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {BORDER};")
        layout.addWidget(sep)

        # ── Core fields ───────────────────────────────────────────────────────
        grp_fields = QGroupBox("STORY FIELDS")
        form = QFormLayout(grp_fields)
        form.setSpacing(10)

        self.assignee_combo = QComboBox()
        form.addRow("Assignee:", self.assignee_combo)

        self.feature_link_edit = QLineEdit()
        self.feature_link_edit.setPlaceholderText("Feature link URL or ID…")
        form.addRow("Feature Link:", self.feature_link_edit)

        self.issuetype_combo = QComboBox()
        form.addRow("Issue Type:", self.issuetype_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItem("— Keep current —", None)
        for p in PRIORITIES:
            self.priority_combo.addItem(p, p)
        form.addRow("Priority:", self.priority_combo)

        # Fibonacci story points with amber warning for 13 and 21
        self.points_combo = QComboBox()
        self.points_combo.addItem("— Not set —", None)
        for v in FIBONACCI:
            label = str(v)
            if v in (13, 21):
                label += "  — consider splitting"
            idx = self.points_combo.count()
            self.points_combo.addItem(label, v)
            if v in (13, 21):
                self.points_combo.setItemData(idx, QColor("#E3B341"), Qt.ItemDataRole.ForegroundRole)
        form.addRow("Story Points:", self.points_combo)

        self.sprint_combo = QComboBox()
        form.addRow("Sprint:", self.sprint_combo)

        due_row = QHBoxLayout()
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("yyyy-MM-dd")
        self.due_date.setDate(QDate.currentDate())
        self.due_clear_btn = QPushButton("Clear")
        self.due_clear_btn.setFixedWidth(90)
        self.due_clear_btn.clicked.connect(self._clear_due_date)
        self._due_set = False
        due_row.addWidget(self.due_date)
        due_row.addWidget(self.due_clear_btn)
        due_row.addStretch()
        form.addRow("Due Date:", due_row)

        layout.addWidget(grp_fields)

        # ── Status transition ─────────────────────────────────────────────────
        grp_status = QGroupBox("STATUS TRANSITION")
        status_layout = QHBoxLayout(grp_status)
        status_layout.setSpacing(8)
        self.transition_combo = QComboBox()
        self.transition_combo.addItem("— No transition —", None)
        status_layout.addWidget(self.transition_combo, 1)
        layout.addWidget(grp_status)

        # ── Description ───────────────────────────────────────────────────────
        grp_desc = QGroupBox("DESCRIPTION")
        desc_layout = QVBoxLayout(grp_desc)
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Story description…")
        self.desc_edit.setMinimumHeight(100)
        desc_layout.addWidget(self.desc_edit)
        layout.addWidget(grp_desc)

        # ── Comment history ───────────────────────────────────────────────────
        grp_history = QGroupBox("RECENT COMMENTS")
        history_layout = QVBoxLayout(grp_history)
        history_layout.setContentsMargins(8, 8, 8, 8)
        history_layout.setSpacing(4)
        self.comment_history = QTextEdit()
        self.comment_history.setReadOnly(True)
        self.comment_history.setMaximumHeight(120)
        self.comment_history.setPlaceholderText("No comments yet.")
        self.comment_history.setStyleSheet(
            f"background: {DARK_BG}; border: none; color: {TEXT_SEC}; font-size: 12px;"
        )
        history_layout.addWidget(self.comment_history)
        _comment_btn_row = QHBoxLayout()
        _comment_btn_row.setSpacing(6)
        self._expand_comment_btn = QPushButton("⤢  Expand")
        self._expand_comment_btn.setFixedHeight(24)
        self._expand_comment_btn.setEnabled(False)
        self._expand_comment_btn.setToolTip("View the selected comment in full")
        self._expand_comment_btn.clicked.connect(self._expand_comment)
        _comment_btn_row.addWidget(self._expand_comment_btn)
        self._edit_comment_btn = QPushButton("✎  Edit")
        self._edit_comment_btn.setFixedHeight(24)
        self._edit_comment_btn.setEnabled(False)
        self._edit_comment_btn.setToolTip("Edit the most recent comment")
        _comment_btn_row.addWidget(self._edit_comment_btn)
        self._delete_comment_btn = QPushButton("✕  Delete")
        self._delete_comment_btn.setFixedHeight(24)
        self._delete_comment_btn.setEnabled(False)
        self._delete_comment_btn.setObjectName("danger")
        self._delete_comment_btn.setToolTip("Delete the most recent comment")
        _comment_btn_row.addWidget(self._delete_comment_btn)
        _comment_btn_row.addStretch()
        history_layout.addLayout(_comment_btn_row)
        layout.addWidget(grp_history)

        # ── Issue links (read-only) ───────────────────────────────────────────
        self._links_grp = QGroupBox("LINKED ISSUES")
        links_layout = QVBoxLayout(self._links_grp)
        links_layout.setContentsMargins(8, 8, 8, 8)
        links_layout.setSpacing(2)
        self._links_list = QTextEdit()
        self._links_list.setReadOnly(True)
        self._links_list.setMaximumHeight(80)
        self._links_list.setPlaceholderText("No links.")
        self._links_list.setStyleSheet(
            f"background: {DARK_BG}; border: none; color: {TEXT_SEC}; font-size: 12px;"
        )
        links_layout.addWidget(self._links_list)
        self._links_grp.setVisible(False)
        layout.addWidget(self._links_grp)

        # ── Comment ───────────────────────────────────────────────────────────
        grp_comment = QGroupBox("ADD COMMENT")
        comment_layout = QVBoxLayout(grp_comment)
        _tr = QHBoxLayout()
        _tl = QLabel("Template:"); _tl.setObjectName("dim"); _tr.addWidget(_tl)
        self.comment_template_combo = QComboBox()
        self.comment_template_combo.addItem("— select —", None)
        for _t in COMMENT_TEMPLATES: self.comment_template_combo.addItem(_t, _t)
        self.comment_template_combo.currentIndexChanged.connect(self._apply_comment_template)
        _tr.addWidget(self.comment_template_combo, 1)
        comment_layout.addLayout(_tr)
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Type a comment to post…")
        self.comment_edit.setMaximumHeight(80)
        comment_layout.addWidget(self.comment_edit)
        layout.addWidget(grp_comment)

        layout.addStretch()
        self.undo_btn = QPushButton("↩  Undo Save")
        self.undo_btn.setMinimumHeight(40)
        self.undo_btn.setToolTip("Restore the state from before the last save")
        self.undo_btn.setEnabled(False)
        self.undo_btn.clicked.connect(self._undo_save)
        layout.addWidget(self.undo_btn)
        self.save_btn = QPushButton("▶  SAVE CHANGES")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

        # ── Wire dirty-state detection ────────────────────────────────────────
        self.assignee_combo.currentIndexChanged.connect(self._check_dirty)
        self.feature_link_edit.textChanged.connect(self._check_dirty)
        self.issuetype_combo.currentIndexChanged.connect(self._check_dirty)
        self.priority_combo.currentIndexChanged.connect(self._check_dirty)
        self.points_combo.currentIndexChanged.connect(self._check_dirty)
        self.sprint_combo.currentIndexChanged.connect(self._check_dirty)
        self.due_date.dateChanged.connect(self._check_dirty)
        self.transition_combo.currentIndexChanged.connect(self._check_dirty)
        self.desc_edit.textChanged.connect(self._check_dirty)
        self.comment_edit.textChanged.connect(self._check_dirty)

    def _apply_comment_template(self, index: int):
        text = self.comment_template_combo.itemData(index)
        if not text: return
        self.comment_edit.setPlainText(text)
        self.comment_edit.setFocus()
        cur = self.comment_edit.textCursor()
        cur.movePosition(cur.MoveOperation.End)
        self.comment_edit.setTextCursor(cur)
        self.comment_template_combo.blockSignals(True)
        self.comment_template_combo.setCurrentIndex(0)
        self.comment_template_combo.blockSignals(False)

    def _copy_key(self):
        if self.current_key:
            QApplication.clipboard().setText(self.current_key)
            self.copy_key_btn.setText("✓")
            QTimer.singleShot(1500, lambda: self.copy_key_btn.setText("⎘"))

    def _undo_save(self):
        if not self._pre_save_snapshot:
            return
        snap = self._pre_save_snapshot
        self.blockSignals(True)
        for i in range(self.assignee_combo.count()):
            if self.assignee_combo.itemData(i) == snap.get("assignee"):
                self.assignee_combo.setCurrentIndex(i)
                break
        self.feature_link_edit.setText(snap.get("feature_link", ""))
        for i in range(self.issuetype_combo.count()):
            if self.issuetype_combo.itemData(i) == snap.get("issuetype"):
                self.issuetype_combo.setCurrentIndex(i)
                break
        for i in range(self.priority_combo.count()):
            if self.priority_combo.itemData(i) == snap.get("priority"):
                self.priority_combo.setCurrentIndex(i)
                break
        for i in range(self.points_combo.count()):
            if self.points_combo.itemData(i) == snap.get("points"):
                self.points_combo.setCurrentIndex(i)
                break
        for i in range(self.sprint_combo.count()):
            if self.sprint_combo.itemData(i) == snap.get("sprint"):
                self.sprint_combo.setCurrentIndex(i)
                break
        if snap.get("due_set") and snap.get("due_date"):
            self._due_set = True
            self.due_date.setDate(QDate.fromString(snap["due_date"], "yyyy-MM-dd"))
        else:
            self._due_set = False
            self.due_date.setDate(QDate.currentDate())
        self.desc_edit.setPlainText(snap.get("desc", ""))
        self.blockSignals(False)
        self._snapshot = self._snapshot_state()
        self._pre_save_snapshot = None
        self.undo_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

    def _open_in_jira(self):
        if self.current_key and self._base_url:
            webbrowser.open(f"{self._base_url}/browse/{self.current_key}")

    def _clear_due_date(self):
        self._due_set = False
        self.due_date.setStyleSheet(f"color: {TEXT_DIM};")
        self.due_date.setDate(QDate.currentDate())
        self._check_dirty()

    def _snapshot_state(self) -> dict:
        return {
            "assignee":     self.assignee_combo.currentData(),
            "feature_link": self.feature_link_edit.text(),
            "issuetype":    self.issuetype_combo.currentData(),
            "priority":     self.priority_combo.currentData(),
            "points":       self.points_combo.currentData(),
            "sprint":       self.sprint_combo.currentData(),
            "due_set":      self._due_set,
            "due_date":     self.due_date.date().toString("yyyy-MM-dd"),
            "transition":   self.transition_combo.currentData(),
            "desc":         self.desc_edit.toPlainText(),
            "comment":      self.comment_edit.toPlainText(),
        }

    def _check_dirty(self):
        if not self.current_key:
            return
        current  = self._snapshot_state()
        is_dirty = (current != self._snapshot)
        self.save_btn.setEnabled(is_dirty)
        if is_dirty:
            self.save_btn.setToolTip("Unsaved changes")
            self.changed.emit()
        else:
            self.save_btn.setToolTip("No changes to save")

    def set_members(self, members: list):
        if members and isinstance(members[0], dict) and "to" in members[0] and "displayName" not in members[0]:
            return
        # Don't clear the existing dropdown if the new list is empty
        if not members:
            return
        self._members = members
        self.assignee_combo.clear()
        self.assignee_combo.addItem("— Unassigned —", None)
        for m in members:
            uid = m.get("name") or m.get("key") or m.get("accountId")
            display = m.get("displayName") or m.get("name") or "?"
            self.assignee_combo.addItem(display, uid)

        if self._pending_assignee:
            found = False
            for i in range(self.assignee_combo.count()):
                if self.assignee_combo.itemData(i) == self._pending_assignee:
                    self.assignee_combo.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.assignee_combo.insertItem(1, f"{self._pending_assignee} (current)", self._pending_assignee)
                self.assignee_combo.setCurrentIndex(1)

    def set_issue_types(self, issue_types: list):
        self.issuetype_combo.clear()
        for it in issue_types:
            self.issuetype_combo.addItem(it.get("name", "?"), it.get("id"))

    def set_sprints(self, sprints: list):
        self._sprints = sprints
        self.sprint_combo.clear()
        self.sprint_combo.addItem("— Keep current —", None)
        for s in sprints:
            state = s.get("state", "")
            label = f"[{state.upper()}] {s['name']}"
            self.sprint_combo.addItem(label, s["id"])

    def set_transitions(self, transitions: list):
        self._transitions = transitions
        self.transition_combo.clear()
        self.transition_combo.addItem("— No transition —", None)
        for t in transitions:
            self.transition_combo.addItem(t.get("name", "?"), t.get("id"))

    def load_issue(self, issue: dict):
        _tracked = [
            self.assignee_combo, self.feature_link_edit, self.issuetype_combo,
            self.priority_combo, self.points_combo, self.sprint_combo,
            self.due_date, self.transition_combo, self.desc_edit, self.comment_edit,
        ]
        for w in _tracked:
            w.blockSignals(True)
        try:
            self._load_issue_fields(issue)
        finally:
            for w in _tracked:
                w.blockSignals(False)
        self._pre_save_snapshot = None
        self.undo_btn.setEnabled(False)
        self._snapshot = self._snapshot_state()
        self.save_btn.setEnabled(False)
        self.save_btn.setToolTip("No changes to save")
        self.copy_key_btn.setEnabled(True)
        self.open_jira_btn.setEnabled(True)
        self.clone_btn.setEnabled(True)
        self.attach_btn.setEnabled(True)

    def _load_issue_fields(self, issue: dict):
        self.current_key = issue["key"]
        fields = issue.get("fields", {})

        self.key_lbl.setText(self.current_key)
        self.title_lbl.setText(fields.get("summary", ""))
        status = fields.get("status", {}).get("name", "")
        self.status_badge.setText(f"◈  {status.upper()}")

        assignee = fields.get("assignee")
        if assignee:
            self._pending_assignee = (
                assignee.get("name") or assignee.get("key") or assignee.get("accountId")
            )
            for i in range(self.assignee_combo.count()):
                if self.assignee_combo.itemData(i) == self._pending_assignee:
                    self.assignee_combo.setCurrentIndex(i)
                    break
            else:
                display = assignee.get("displayName", self._pending_assignee)
                self.assignee_combo.insertItem(1, display, self._pending_assignee)
                self.assignee_combo.setCurrentIndex(1)
        else:
            self._pending_assignee = None
            self.assignee_combo.setCurrentIndex(0)

        itype = fields.get("issuetype", {})
        itype_id = itype.get("id")
        self.issuetype_combo.setCurrentIndex(0)
        for i in range(self.issuetype_combo.count()):
            if self.issuetype_combo.itemData(i) == itype_id:
                self.issuetype_combo.setCurrentIndex(i)
                break

        priority = fields.get("priority", {})
        pname = priority.get("name") if priority else None
        self.priority_combo.setCurrentIndex(0)
        for i in range(self.priority_combo.count()):
            if self.priority_combo.itemData(i) == pname:
                self.priority_combo.setCurrentIndex(i)
                break

        pts = next((fields.get(k) for k in ([self._sp_field] + JiraClient._SP_FALLBACKS) if fields.get(k) is not None), None)
        self.points_combo.setCurrentIndex(0)
        if pts is not None:
            try:
                pts_int = int(float(pts))
            except (TypeError, ValueError):
                pts_int = None
            if pts_int is not None:
                for i in range(self.points_combo.count()):
                    if self.points_combo.itemData(i) == pts_int:
                        self.points_combo.setCurrentIndex(i)
                        break

        fl_field = self._fl_field
        fl_value = fields.get(fl_field) or ""
        if isinstance(fl_value, dict):
            fl_value = fl_value.get("url", "") or fl_value.get("id", "")
        self.feature_link_edit.setText(str(fl_value) if fl_value else "")

        sprint_field = fields.get("customfield_10020") or []
        if isinstance(sprint_field, list) and sprint_field:
            current_sprint = sprint_field[-1]
            self._current_sprint_id = current_sprint.get("id")
        else:
            self._current_sprint_id = None
        self.sprint_combo.setCurrentIndex(0)

        duedate = fields.get("duedate")
        if duedate:
            self._due_set = True
            parsed_date = QDate.fromString(duedate[:10], "yyyy-MM-dd")
            self.due_date.setDate(parsed_date if parsed_date.isValid() else QDate.currentDate())
            self.due_date.setStyleSheet(f"color: {TEXT_PRI};")
        else:
            self._due_set = False
            self.due_date.setDate(QDate.currentDate())
            self.due_date.setStyleSheet(f"color: {TEXT_DIM};")

        self.transition_combo.setCurrentIndex(0)

        desc = fields.get("description") or {}
        plain = self._adf_to_text(desc) if isinstance(desc, dict) else (desc or "")
        self.desc_edit.setPlainText(plain)

        self.comment_edit.clear()

        comments_data = fields.get("comment", {})
        if isinstance(comments_data, dict):
            all_comments = comments_data.get("comments", [])
        else:
            all_comments = []
        self._comments_data = all_comments  # store with IDs for edit/delete
        recent = all_comments[-5:]
        if recent:
            lines = []
            full_lines = []
            for c in reversed(recent):
                author = (c.get("author") or {})
                name = author.get("displayName") or author.get("name") or "Unknown"
                created = (c.get("created") or "")[:10]
                body = c.get("body") or {}
                text = self._adf_to_text(body) if isinstance(body, dict) else str(body)
                text = text.strip()
                full_lines.append(f"[{created}] {name}:\n{text}")
                display_text = text.replace("\n", " ")
                if len(display_text) > 200:
                    display_text = display_text[:200] + "…"
                lines.append(f"[{created}] {name}: {display_text}")
            self.comment_history.setPlainText("\n\n".join(lines))
            self._full_comment_text = "\n\n".join(full_lines)
            self._expand_comment_btn.setEnabled(True)
            self._edit_comment_btn.setEnabled(True)
            self._delete_comment_btn.setEnabled(True)
        else:
            self.comment_history.setPlainText("")
            self._full_comment_text = ""
            self._comments_data = []
            self._expand_comment_btn.setEnabled(False)
            self._edit_comment_btn.setEnabled(False)
            self._delete_comment_btn.setEnabled(False)

        # ── Issue links ───────────────────────────────────────────────────────
        links = fields.get("issuelinks", [])
        if links:
            link_lines = []
            for lnk in links:
                ltype = (lnk.get("type") or {}).get("name", "relates to")
                if "outwardIssue" in lnk:
                    rel   = (lnk.get("type") or {}).get("outward", ltype)
                    other = lnk["outwardIssue"]
                elif "inwardIssue" in lnk:
                    rel   = (lnk.get("type") or {}).get("inward", ltype)
                    other = lnk["inwardIssue"]
                else:
                    continue
                okey    = other.get("key", "?")
                osumm   = (other.get("fields") or {}).get("summary", "")[:60]
                ostatus = ((other.get("fields") or {}).get("status") or {}).get("name", "")
                link_lines.append(f"{rel}  {okey}  [{ostatus}]  {osumm}")
            self._links_list.setPlainText("\n".join(link_lines))
            self._links_grp.setVisible(True)
        else:
            self._links_list.setPlainText("")
            self._links_grp.setVisible(False)
        if self.current_key:
            QApplication.clipboard().setText(self.current_key)
            self.copy_key_btn.setText("✓")
            QTimer.singleShot(1500, lambda: self.copy_key_btn.setText("⎘"))

    def _expand_comment(self):
        full_text = self._full_comment_text
        if not full_text:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Comment — {self.current_key or ''}")
        dlg.setMinimumSize(540, 320)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        viewer = QTextEdit()
        viewer.setReadOnly(True)
        viewer.setPlainText(full_text)
        viewer.setStyleSheet(
            f"background: {DARK_BG}; border: 1px solid {BORDER}; "
            f"color: {TEXT_PRI}; font-size: 13px;"
        )
        layout.addWidget(viewer, 1)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.exec()

    def _adf_to_text(self, node: dict, _depth: int = 0) -> str:
        if not node or _depth > 50:
            return ""
        parts = []
        if node.get("type") == "text":
            parts.append(node.get("text", ""))
        for child in node.get("content", []):
            parts.append(self._adf_to_text(child, _depth + 1))
            if child.get("type") in ("paragraph", "heading"):
                parts.append("\n")
        return "".join(parts)

    def _on_save(self):
        if not self.current_key:
            return
        fields = {}

        aid = self.assignee_combo.currentData()
        fields["assignee"] = {"name": aid} if aid else None

        itype_id = self.issuetype_combo.currentData()
        if itype_id:
            fields["issuetype"] = {"id": itype_id}

        pname = self.priority_combo.currentData()
        if pname:
            fields["priority"] = {"name": pname}

        pts = self.points_combo.currentData()
        if pts is not None:
            fields[self._sp_field] = pts

        fl_val = self.feature_link_edit.text().strip()
        if fl_val:
            fields[self._fl_field] = fl_val

        if self._due_set:
            fields["duedate"] = self.due_date.date().toString("yyyy-MM-dd")
        else:
            fields["duedate"] = None

        desc_text = self.desc_edit.toPlainText().strip()
        if desc_text:
            fields["description"] = desc_text

        target_sprint = self.sprint_combo.currentData()
        transition_id = self.transition_combo.currentData()
        comment = self.comment_edit.toPlainText().strip()
        self._pre_save_snapshot = self._snapshot_state()
        self.saved.emit(self.current_key, fields, comment, transition_id, target_sprint)


# ── Export Stories Dialog ─────────────────────────────────────────────────────
class ExportStoriesDialog(QDialog):
    def __init__(self, issues: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Stories — Select")
        self.setMinimumSize(640, 520)
        self._issues = issues
        self._basket = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        avail_lbl = QLabel("AVAILABLE STORIES")
        avail_lbl.setObjectName("subheading")
        layout.addWidget(avail_lbl)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search by key or summary…")
        self._search.textChanged.connect(self._filter_available)
        layout.addWidget(self._search)

        self._avail_list = QListWidget()
        self._avail_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._avail_list.itemDoubleClicked.connect(self._add_selected)
        for issue in sorted(issues, key=lambda i: i.get("key", "")):
            self._add_avail_item(issue)
        layout.addWidget(self._avail_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add ▶")
        add_btn.clicked.connect(self._add_selected)
        remove_btn = QPushButton("◀ Remove")
        remove_btn.clicked.connect(self._remove_selected)
        btn_row.addWidget(add_btn)
        btn_row.addStretch()
        btn_row.addWidget(remove_btn)
        layout.addLayout(btn_row)

        basket_lbl = QLabel("SELECTED FOR EXPORT")
        basket_lbl.setObjectName("subheading")
        layout.addWidget(basket_lbl)

        self._basket_list = QListWidget()
        self._basket_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._basket_list.itemDoubleClicked.connect(self._remove_selected)
        layout.addWidget(self._basket_list)

        self._basket_count_lbl = QLabel("0 stories selected")
        self._basket_count_lbl.setObjectName("dim")
        layout.addWidget(self._basket_count_lbl)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Export Selected")
        btns.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self._export_btn = btns.button(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _add_avail_item(self, issue):
        key     = issue.get("key", "")
        summary = (issue.get("fields") or {}).get("summary", "")
        item = QListWidgetItem(f"{key}  —  {summary}")
        item.setData(Qt.ItemDataRole.UserRole, key)
        self._avail_list.addItem(item)

    def _filter_available(self, text):
        term = text.strip().lower()
        for i in range(self._avail_list.count()):
            item = self._avail_list.item(i)
            item.setHidden(bool(term and term not in item.text().lower()))

    def _add_selected(self):
        for item in self._avail_list.selectedItems():
            key = item.data(Qt.ItemDataRole.UserRole)
            if key not in self._basket:
                issue = next((iss for iss in self._issues if iss.get("key") == key), None)
                if issue:
                    self._basket[key] = issue
                    basket_item = QListWidgetItem(item.text())
                    basket_item.setData(Qt.ItemDataRole.UserRole, key)
                    self._basket_list.addItem(basket_item)
        self._update_count()

    def _remove_selected(self):
        for item in self._basket_list.selectedItems():
            key = item.data(Qt.ItemDataRole.UserRole)
            self._basket.pop(key, None)
            self._basket_list.takeItem(self._basket_list.row(item))
        self._update_count()

    def _update_count(self):
        n = len(self._basket)
        self._basket_count_lbl.setText(f"{n} stor{'ies' if n != 1 else 'y'} selected")
        self._export_btn.setEnabled(n > 0)

    def get_selected_issues(self) -> list:
        return list(self._basket.values())


# ── Sprint Report Dialog ──────────────────────────────────────────────────────
def _apply_dark_palette(browser, bg: str = None, base: str = None):
    """Force a QTextBrowser to use dark colours for its document background.
    setStyleSheet alone does not override the Base palette role that
    QTextBrowser uses to paint its document area."""
    bg   = bg   or DARK_BG
    base = base or PANEL_BG
    pal  = browser.palette()
    pal.setColor(QPalette.ColorRole.Base,          QColor(base))
    pal.setColor(QPalette.ColorRole.Window,        QColor(bg))
    pal.setColor(QPalette.ColorRole.Text,          QColor(TEXT_PRI))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(CARD_BG))
    browser.setPalette(pal)
    browser.setAutoFillBackground(True)

class SprintReportDialog(QDialog):
    """Sprint report dialog with two tabs: Sprint Report and People Report."""

    def __init__(self, issues: list, sprint_label: str, sp_field: str,
                 fl_field: str, base_url: str, adf_to_text_fn,
                 client=None, board_id: int = 0, sprint_detail: dict = None,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sprint Report")
        self.setMinimumSize(960, 720)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        self._issues        = issues
        self._sprint_label  = sprint_label
        self._sp_field      = sp_field
        self._fl_field      = fl_field
        self._base_url      = base_url
        self._adf_to_text   = adf_to_text_fn
        self._client        = client
        self._board_id      = board_id
        self._sprint_detail = sprint_detail or {}
        self._html          = ""
        self._people_html   = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs, 1)

        # ── Tab 1: Sprint Report ──────────────────────────────────────────────
        sprint_tab = QWidget()
        sprint_layout = QVBoxLayout(sprint_tab)
        sprint_layout.setSpacing(10)
        sprint_layout.setContentsMargins(0, 12, 0, 0)

        # Controls row — mirrors People tab layout
        sr_ctrl_row = QHBoxLayout()
        sr_ctrl_row.setSpacing(12)

        # -- Scope: Sprint or Date Range
        sr_scope_grp = QGroupBox("SCOPE")
        sr_scope_inner = QVBoxLayout(sr_scope_grp)
        sr_scope_inner.setSpacing(6)

        self._sr_scope_sprint_rb = QRadioButton("Sprint")
        self._sr_scope_date_rb   = QRadioButton("Date Range")
        self._sr_scope_sprint_rb.setChecked(True)
        sr_scope_inner.addWidget(self._sr_scope_sprint_rb)
        sr_scope_inner.addWidget(self._sr_scope_date_rb)

        self._sr_sprint_combo = QComboBox()
        self._sr_sprint_combo.setMinimumWidth(220)
        self._sr_sprint_combo.addItem("Loading sprints…")
        self._sr_sprint_combo.setEnabled(False)
        sr_scope_inner.addWidget(self._sr_sprint_combo)

        sr_date_row = QHBoxLayout()
        self._sr_date_from = QLineEdit()
        self._sr_date_from.setPlaceholderText("From  YYYY-MM-DD")
        self._sr_date_from.setEnabled(False)
        self._sr_date_to = QLineEdit()
        self._sr_date_to.setPlaceholderText("To  YYYY-MM-DD")
        self._sr_date_to.setEnabled(False)
        sr_date_row.addWidget(self._sr_date_from)
        sr_date_row.addWidget(QLabel("→"))
        sr_date_row.addWidget(self._sr_date_to)
        sr_scope_inner.addLayout(sr_date_row)
        sr_ctrl_row.addWidget(sr_scope_grp)
        sr_ctrl_row.addStretch()
        sprint_layout.addLayout(sr_ctrl_row)

        def _on_sr_scope_toggle():
            use_sprint = self._sr_scope_sprint_rb.isChecked()
            self._sr_sprint_combo.setEnabled(use_sprint and self._sr_sprint_combo.count() > 0)
            self._sr_date_from.setEnabled(not use_sprint)
            self._sr_date_to.setEnabled(not use_sprint)

        self._sr_scope_sprint_rb.toggled.connect(_on_sr_scope_toggle)
        self._sr_scope_date_rb.toggled.connect(_on_sr_scope_toggle)

        # Generate button + status
        sr_gen_row = QHBoxLayout()
        self._sr_gen_btn = QPushButton("▶  Generate Sprint Report")
        self._sr_gen_btn.setObjectName("save_btn")
        self._sr_gen_btn.clicked.connect(self._generate_sprint_report)
        sr_gen_row.addWidget(self._sr_gen_btn)
        self._sr_status = QLabel("")
        self._sr_status.setObjectName("dim")
        sr_gen_row.addWidget(self._sr_status, 1)
        sprint_layout.addLayout(sr_gen_row)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        self._browser.setStyleSheet(
            f"QTextBrowser {{ background: {DARK_BG}; color: {TEXT_PRI}; "
            f"border: 1px solid {BORDER}; border-radius: 6px; }}"
        )
        _apply_dark_palette(self._browser)
        sprint_layout.addWidget(self._browser, 1)

        sprint_btn_row = QHBoxLayout()
        self._save_sprint_btn = QPushButton("⬇  Save as HTML")
        self._save_sprint_btn.setObjectName("toolbar_btn")
        self._save_sprint_btn.clicked.connect(self._save_html)
        self._save_sprint_btn.setEnabled(False)
        sprint_btn_row.addWidget(self._save_sprint_btn)
        sprint_btn_row.addStretch()
        sprint_layout.addLayout(sprint_btn_row)
        self._tabs.addTab(sprint_tab, "📊  Sprint Report")
        # ── Tab 2: People Report ──────────────────────────────────────────────
        people_tab = QWidget()
        people_layout = QVBoxLayout(people_tab)
        people_layout.setSpacing(10)
        people_layout.setContentsMargins(0, 12, 0, 0)

        # Controls row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(12)

        # -- Scope: Sprint or Date Range
        scope_grp = QGroupBox("SCOPE")
        scope_inner = QVBoxLayout(scope_grp)
        scope_inner.setSpacing(6)

        self._scope_sprint_rb = QRadioButton("Sprint")
        self._scope_date_rb   = QRadioButton("Date Range")
        self._scope_sprint_rb.setChecked(True)
        scope_inner.addWidget(self._scope_sprint_rb)
        scope_inner.addWidget(self._scope_date_rb)

        # Sprint selector
        self._sprint_scope_combo = QComboBox()
        self._sprint_scope_combo.setMinimumWidth(220)
        self._sprint_scope_combo.addItem("Loading sprints…")
        self._sprint_scope_combo.setEnabled(False)
        scope_inner.addWidget(self._sprint_scope_combo)

        # Date range
        date_row = QHBoxLayout()
        self._date_from = QLineEdit()
        self._date_from.setPlaceholderText("From  YYYY-MM-DD")
        self._date_from.setEnabled(False)
        self._date_to = QLineEdit()
        self._date_to.setPlaceholderText("To  YYYY-MM-DD")
        self._date_to.setEnabled(False)
        date_row.addWidget(self._date_from)
        date_row.addWidget(QLabel("→"))
        date_row.addWidget(self._date_to)
        scope_inner.addLayout(date_row)
        ctrl_row.addWidget(scope_grp)

        def _on_scope_toggle():
            use_sprint = self._scope_sprint_rb.isChecked()
            self._sprint_scope_combo.setEnabled(use_sprint and self._sprint_scope_combo.count() > 0)
            self._date_from.setEnabled(not use_sprint)
            self._date_to.setEnabled(not use_sprint)

        self._scope_sprint_rb.toggled.connect(_on_scope_toggle)
        self._scope_date_rb.toggled.connect(_on_scope_toggle)

        # -- People selector
        people_grp = QGroupBox("PEOPLE")
        people_inner = QVBoxLayout(people_grp)
        people_inner.setSpacing(6)

        people_inner.addWidget(QLabel("Select from sprint:"))
        self._people_list = QListWidget()
        self._people_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._people_list.setMaximumHeight(120)

        # Populate from current sprint assignees
        seen = set()
        for iss in issues:
            aobj = (iss.get("fields") or {}).get("assignee") or {}
            name = aobj.get("name") or aobj.get("accountId") or ""
            display = aobj.get("displayName") or name
            if name and name not in seen:
                seen.add(name)
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, name)
                self._people_list.addItem(item)

        people_inner.addWidget(self._people_list)
        people_inner.addWidget(QLabel("Add more (comma-separated usernames):"))
        self._extra_people = QLineEdit()
        self._extra_people.setPlaceholderText("e.g. jsmith, adoe")
        people_inner.addWidget(self._extra_people)
        ctrl_row.addWidget(people_grp, 1)

        people_layout.addLayout(ctrl_row)

        # Generate button + status
        gen_row = QHBoxLayout()
        self._gen_btn = QPushButton("▶  Generate People Report")
        self._gen_btn.setObjectName("save_btn")
        self._gen_btn.clicked.connect(self._generate_people_report)
        gen_row.addWidget(self._gen_btn)
        self._people_status = QLabel("")
        self._people_status.setObjectName("dim")
        gen_row.addWidget(self._people_status, 1)
        people_layout.addLayout(gen_row)

        self._people_browser = QTextBrowser()
        self._people_browser.setOpenExternalLinks(True)
        self._people_browser.setStyleSheet(
            f"QTextBrowser {{ background: {DARK_BG}; color: {TEXT_PRI}; "
            f"border: 1px solid {BORDER}; border-radius: 6px; }}"
        )
        _apply_dark_palette(self._people_browser)
        people_layout.addWidget(self._people_browser, 1)

        people_btn_row = QHBoxLayout()
        save_people_btn = QPushButton("⬇  Save as HTML")
        save_people_btn.setObjectName("toolbar_btn")
        save_people_btn.clicked.connect(self._save_people_html)
        save_people_btn.setEnabled(False)
        self._save_people_btn = save_people_btn
        people_btn_row.addWidget(save_people_btn)
        people_btn_row.addStretch()
        people_layout.addLayout(people_btn_row)

        self._tabs.addTab(people_tab, "👤  People Report")

        # Close button row
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._load_sprints_for_tabs()

    def _load_sprints_for_tabs(self):
        """Fetch all sprints and populate both the Sprint Report and People Report scope combos."""
        if not self._client or not self._board_id:
            for combo in (self._sr_sprint_combo, self._sprint_scope_combo):
                combo.clear()
                combo.addItem("No board available")
            return

        def _do():
            return self._client.get_all_sprints(self._board_id)

        worker = Worker(_do)
        worker.result.connect(self._on_sprints_loaded)
        worker.error.connect(lambda e: (
            self._sr_sprint_combo.addItem("Failed to load"),
            self._sprint_scope_combo.addItem("Failed to load"),
        ))
        worker.start()
        self._sprint_worker = worker

    # ── Sprint Report ─────────────────────────────────────────────────────────
    def _generate_sprint_report(self):
        self._sr_gen_btn.setEnabled(False)
        self._sr_status.setText("Fetching issues…")
        self._browser.setHtml("<p style='color:#888;padding:20px;'>Loading…</p>")

        # Determine scope and build the fetch callable up front so
        # scope_label is always defined before _on_done references it.
        use_sprint  = self._sr_scope_sprint_rb.isChecked()
        sprint_id   = self._sr_sprint_combo.currentData() or 0 if use_sprint else 0
        date_from   = "" if use_sprint else self._sr_date_from.text().strip()
        date_to     = "" if use_sprint else self._sr_date_to.text().strip()

        if use_sprint:
            scope_label = self._sr_sprint_combo.currentText()
            if not sprint_id:
                self._sr_gen_btn.setEnabled(True)
                self._sr_status.setText("⚠ No sprint selected.")
                return
        else:
            scope_label = f"{date_from or '…'} → {date_to or '…'}"

        def _do() -> list:
            if use_sprint:
                return self._client.get_sprint_issues(self._board_id, sprint_id)
            # Date range — fetch via JQL search
            jql_parts = []
            if date_from:
                jql_parts.append(f'updated >= "{date_from}"')
            if date_to:
                jql_parts.append(f'updated <= "{date_to}"')
            jql = " AND ".join(jql_parts) if jql_parts else "updated >= -90d"
            jql += " ORDER BY updated DESC"
            encoded = urllib.parse.quote(jql)
            sp = self._client.story_point_field_id
            fields = ",".join([
                "summary", "assignee", "status", "priority", "issuetype",
                "duedate", sp, "comment",
            ])
            all_issues: list = []
            start = 0
            max_results = 100
            while True:
                url = (f"{self._client.base_url}/rest/api/{self._client.api_version}/search"
                       f"?jql={encoded}&maxResults={max_results}&startAt={start}&fields={fields}")
                req = urllib.request.Request(url, headers=self._client.headers)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                batch = data.get("issues", [])
                all_issues.extend(batch)
                if len(batch) < max_results:
                    break
                start += max_results
            return all_issues

        def _on_done(issues: list) -> None:
            self._sr_gen_btn.setEnabled(True)
            self._sr_status.setText(f"✓ {len(issues)} issues loaded.")
            self._save_sprint_btn.setEnabled(True)
            self._build_report(issues, scope_label)

        def _on_err(e: str) -> None:
            self._sr_gen_btn.setEnabled(True)
            self._sr_status.setText(f"✗ {e}")
            self._browser.setHtml(
                f"<p style='color:#f78166;padding:20px;'>Error: {e}</p>"
            )

        worker = Worker(_do)
        worker.result.connect(_on_done)
        worker.error.connect(_on_err)
        worker.start()
        self._sr_worker = worker

    def _build_report(self, issues: list = None, scope_label: str = ""):
        issues    = issues if issues is not None else self._issues
        sp        = self._sp_field
        today_str = date.today().strftime("%B %d, %Y")
        title     = scope_label or self._sprint_label

        total_pts = done_pts = 0
        status_counts: dict[str, int]   = {}
        assignee_stats: dict[str, dict] = {}

        for iss in issues:
            f      = iss.get("fields", {})
            status = (f.get("status") or {}).get("name", "—")
            status_counts[status] = status_counts.get(status, 0) + 1
            pts_raw = next(
                (f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS)
                 if f.get(k) is not None), None
            )
            try:
                pts = int(float(pts_raw)) if pts_raw is not None else 0
            except (TypeError, ValueError):
                pts = 0
            total_pts += pts
            if status == "Done":
                done_pts += pts
            aobj  = f.get("assignee") or {}
            aname = aobj.get("displayName") or aobj.get("name") or "Unassigned"
            if aname not in assignee_stats:
                assignee_stats[aname] = {
                    "total": 0, "done": 0, "pts": 0, "done_pts": 0, "stories": []
                }
            assignee_stats[aname]["total"] += 1
            assignee_stats[aname]["pts"]   += pts
            if status == "Done":
                assignee_stats[aname]["done"]     += 1
                assignee_stats[aname]["done_pts"] += pts
            assignee_stats[aname]["stories"].append(iss)

        pct_done      = round(done_pts / total_pts * 100) if total_pts else 0
        n_done        = status_counts.get("Done", 0)
        n_total       = len(issues)
        n_remaining   = n_total - n_done
        remaining_pts = total_pts - done_pts

        start_str  = (self._sprint_detail.get("startDate") or "")[:10]
        end_str    = (self._sprint_detail.get("endDate")   or "")[:10]
        date_range = f"{start_str} \u2192 {end_str}" if start_str and end_str else ""

        STATUS_CSS = {
            "To Do":       ("#6e7681", "#f6f8fa"),
            "In Progress": ("#388bfd", "#dbeafe"),
            "Done":        ("#3fb950", "#dcfce7"),
            "In Review":   ("#a371f7", "#f3e8ff"),
            "Blocked":     ("#f78166", "#fff1ee"),
        }

        def status_badge(name):
            fg, bg = STATUS_CSS.get(name, ("#8b949e", "#f6f8fa"))
            return (
                f'<span style="display:inline-block;padding:3px 10px;border-radius:12px;'
                f'font-size:11px;font-weight:600;background:{bg};color:{fg};">'
                f'{name}</span>'
            )

        def priority_badge(name):
            cfg = {
                "Highest": ("#f78166", "\u25b2\u25b2"),
                "High":    ("#e3b341", "\u25b2"),
                "Medium":  ("#388bfd", "\u25cf"),
                "Low":     ("#3fb950", "\u25bc"),
                "Lowest":  ("#8b949e", "\u25bc\u25bc"),
            }
            colour, sym = cfg.get(name, ("#8b949e", "\u25cf"))
            return (
                f'<span style="color:{colour};font-size:11px;" title="{name}">'
                f'{sym}</span>'
            )

        def mini_bar(pct, colour="#388bfd", width=140):
            filled = max(0, min(pct, 100))
            return (
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'<div style="flex:0 0 {width}px;height:6px;background:#e9ecef;'
                f'border-radius:3px;overflow:hidden;">'
                f'<div style="width:{filled}%;height:6px;background:{colour};'
                f'border-radius:3px;"></div></div>'
                f'<span style="font-size:11px;color:#57606a;white-space:nowrap;">'
                f'{pct}%</span></div>'
            )

        def ring(pct, colour="#3fb950", r=38):
            circ = round(2 * 3.14159 * r, 1)
            dash = round(pct / 100 * circ, 1)
            return (
                f'<svg width="{r*2+8}" height="{r*2+8}" viewBox="0 0 {r*2+8} {r*2+8}" '
                f'style="transform:rotate(-90deg);">'
                f'<circle cx="{r+4}" cy="{r+4}" r="{r}" fill="none" '
                f'stroke="#e9ecef" stroke-width="6"/>'
                f'<circle cx="{r+4}" cy="{r+4}" r="{r}" fill="none" '
                f'stroke="{colour}" stroke-width="6" '
                f'stroke-dasharray="{dash} {circ}" stroke-linecap="round"/>'
                f'</svg>'
            )

        burndown_svg = self._build_burndown_svg(total_pts, done_pts, n_total, n_done)
        velocity_ring = ring(pct_done)

        stat_cards = f"""
    <div class="stat-grid">
      <div class="stat-card" style="border-left:4px solid #388bfd;">
    <div class="stat-icon">&#128203;</div>
    <div class="stat-val">{n_total}</div>
    <div class="stat-lbl">Total Stories</div>
    <div class="stat-sub">{n_remaining} remaining</div>
      </div>
      <div class="stat-card" style="border-left:4px solid #3fb950;">
    <div class="stat-icon">&#9989;</div>
    <div class="stat-val">{n_done}</div>
    <div class="stat-lbl">Stories Done</div>
    <div class="stat-sub">{round(n_done/n_total*100) if n_total else 0}% complete</div>
      </div>
      <div class="stat-card" style="border-left:4px solid #a371f7;">
    <div class="stat-icon">&#9670;</div>
    <div class="stat-val">{total_pts}</div>
    <div class="stat-lbl">Total Points</div>
    <div class="stat-sub">{remaining_pts} remaining</div>
      </div>
      <div class="stat-card" style="border-left:4px solid #3fb950;">
    <div class="stat-icon">&#9889;</div>
    <div class="stat-val">{done_pts}</div>
    <div class="stat-lbl">Points Done</div>
    <div class="stat-sub">&nbsp;</div>
      </div>
      <div class="stat-card" style="border-left:4px solid #e3b341;align-items:center;">
    <div style="position:relative;display:inline-block;">
      {velocity_ring}
      <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                  font-size:14px;font-weight:700;color:#1f2328;">{pct_done}%</div>
    </div>
    <div class="stat-lbl" style="margin-top:6px;">Velocity</div>
      </div>
    </div>"""

        status_bar_segs = ""
        status_legend   = ""
        for sname, cnt in sorted(status_counts.items(), key=lambda x: -x[1]):
            fg, bg = STATUS_CSS.get(sname, ("#8b949e", "#e9ecef"))
            pct = round(cnt / n_total * 100) if n_total else 0
            if pct == 0:
                continue
            status_bar_segs += (
                f'<div style="flex:{pct};background:{fg};height:100%;" '
                f'title="{sname}: {cnt} ({pct}%)"></div>'
            )
            status_legend += (
                f'<div style="display:flex;align-items:center;gap:6px;white-space:nowrap;">'
                f'<div style="width:10px;height:10px;border-radius:2px;background:{fg};'
                f'flex-shrink:0;"></div>'
                f'<span style="font-size:12px;color:#57606a;">{sname}</span>'
                f'<span style="font-size:12px;font-weight:600;color:#1f2328;">{cnt}</span>'
                f'<span style="font-size:11px;color:#8b949e;">({pct}%)</span>'
                f'</div>'
            )
        status_section = f"""
    <div class="card">
      <div class="card-title">Status Breakdown</div>
      <div style="height:20px;border-radius:6px;overflow:hidden;display:flex;margin-bottom:14px;">
    {status_bar_segs}
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:16px;">
    {status_legend}
      </div>
    </div>"""

        assignee_cards = ""
        for aname, ast in sorted(assignee_stats.items(), key=lambda x: -x[1]["pts"]):
            ap  = round(ast["done_pts"] / ast["pts"] * 100) if ast["pts"] else 0
            sp_ = round(ast["done"] / ast["total"] * 100)   if ast["total"] else 0
            initials = "".join(w[0].upper() for w in aname.split()[:2]) or "?"
            assignee_cards += f"""
    <div class="assignee-card">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
    <div style="width:36px;height:36px;border-radius:50%;background:#388bfd22;
                color:#388bfd;font-weight:700;font-size:13px;display:flex;
                align-items:center;justify-content:center;flex-shrink:0;">{initials}</div>
    <div>
      <div style="font-weight:600;font-size:13px;color:#1f2328;">{aname}</div>
      <div style="font-size:11px;color:#57606a;">{ast['total']} stories &middot; {ast['pts']} pts</div>
    </div>
      </div>
      <div style="font-size:11px;color:#57606a;margin-bottom:4px;">Stories complete</div>
      {mini_bar(sp_, "#3fb950")}
      <div style="font-size:11px;color:#57606a;margin:8px 0 4px;">Points complete</div>
      {mini_bar(ap, "#388bfd")}
      <div style="display:flex;gap:16px;margin-top:10px;padding-top:10px;
              border-top:1px solid #f0f0f0;font-size:11px;">
    <span><strong style="color:#3fb950;">{ast['done']}</strong>
          <span style="color:#8b949e;">done</span></span>
    <span><strong style="color:#388bfd;">{ast['done_pts']}</strong>
          <span style="color:#8b949e;">pts done</span></span>
    <span><strong style="color:#e3b341;">{ast['total']-ast['done']}</strong>
          <span style="color:#8b949e;">remaining</span></span>
      </div>
    </div>"""

        story_rows_html = ""
        for iss in sorted(issues, key=lambda i: i.get("key", "")):
            f      = iss.get("fields", {})
            key    = iss.get("key", "")
            summ   = f.get("summary", "")
            status = (f.get("status") or {}).get("name", "&#8212;")
            pri    = (f.get("priority") or {}).get("name", "&#8212;")
            itype  = (f.get("issuetype") or {}).get("name", "&#8212;")
            due    = (f.get("duedate") or "")[:10] or "&#8212;"
            aobj   = f.get("assignee") or {}
            aname  = aobj.get("displayName") or aobj.get("name") or "&#8212;"
            pts_raw = next(
                (f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS)
                 if f.get(k) is not None), None
            )
            try:
                pts_str = str(int(float(pts_raw))) if pts_raw is not None else "&#8212;"
            except (TypeError, ValueError):
                pts_str = "&#8212;"

            key_cell = (
                f'<a href="{self._base_url}/browse/{key}" '
                f'style="color:#388bfd;font-weight:600;text-decoration:none;">{key}</a>'
                if self._base_url else f'<strong>{key}</strong>'
            )

            row_style = ""
            due_style = "color:#1f2328;"
            if due not in ("&#8212;", ""):
                try:
                    days = (date.fromisoformat(due) - date.today()).days
                    if days < 0:
                        row_style = "background:#fff5f5;"
                        due_style = "color:#cf222e;font-weight:600;"
                    elif days <= 3:
                        due_style = "color:#9a6700;font-weight:600;"
                except ValueError:
                    pass

            story_rows_html += (
                f'<tr style="{row_style}">'
                f'<td style="white-space:nowrap;">{key_cell}</td>'
                f'<td style="max-width:320px;">{summ}</td>'
                f'<td style="white-space:nowrap;">{aname}</td>'
                f'<td>{status_badge(status)}</td>'
                f'<td style="text-align:center;">{priority_badge(pri)}</td>'
                f'<td style="text-align:center;font-weight:600;">{pts_str}</td>'
                f'<td style="text-align:center;{due_style}">{due}</td>'
                f'<td style="color:#57606a;font-size:11px;">{itype}</td>'
                f'</tr>'
            )

        self._html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <title>Sprint Report \u2014 {title}</title>
    <style>
      *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 13px; color: #1f2328; background: transparent;
    padding: 32px 24px; line-height: 1.5;
      }}
      .report-header {{
    background: linear-gradient(135deg, #1c2128 0%, #2d333b 100%);
    color: #cdd9e5; border-radius: 12px; padding: 28px 32px; margin-bottom: 28px;
      }}
      .report-header h1 {{
    font-size: 24px; font-weight: 700; color: #ffffff;
    margin-bottom: 6px; letter-spacing: -0.3px;
      }}
      .report-header .sub {{ font-size: 15px; color: #8b949e; margin-top: 2px; }}
      .report-header .meta {{
    font-size: 12px; color: #8b949e; display: flex;
    gap: 20px; flex-wrap: wrap; margin-top: 8px;
      }}
      .section-heading {{
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #57606a; margin: 32px 0 14px;
    display: flex; align-items: center; gap: 8px;
      }}
      .section-heading::after {{
    content: ''; flex: 1; height: 1px; background: #d0d7de;
      }}
      .stat-grid {{ display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 8px; }}
      .stat-card {{
    background: #ffffff; border: 1px solid #d0d7de; border-radius: 10px;
    padding: 18px 20px; min-width: 140px; flex: 1; display: flex;
    flex-direction: column; box-shadow: 0 1px 3px rgba(0,0,0,.04);
      }}
      .stat-icon {{ font-size: 18px; margin-bottom: 8px; }}
      .stat-val  {{ font-size: 30px; font-weight: 700; color: #1f2328; line-height: 1; }}
      .stat-lbl  {{
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .5px; color: #57606a; margin-top: 4px;
      }}
      .stat-sub  {{ font-size: 11px; color: #8b949e; margin-top: 3px; }}
      .card {{
    background: #ffffff; border: 1px solid #d0d7de; border-radius: 10px;
    padding: 20px 24px; margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
      }}
      .card-title {{ font-size: 13px; font-weight: 700; color: #1f2328; margin-bottom: 14px; }}
      .assignee-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 14px;
      }}
      .assignee-card {{
    background: #ffffff; border: 1px solid #d0d7de; border-radius: 10px;
    padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.04);
      }}
      .table-wrap {{
    background: #ffffff; border: 1px solid #d0d7de; border-radius: 10px;
    overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.04);
      }}
      table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
      thead th {{
    background: #f6f8fa; padding: 10px 14px; text-align: left;
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .6px; color: #57606a; border-bottom: 1px solid #d0d7de;
    position: sticky; top: 0;
      }}
      tbody td {{
    padding: 10px 14px; border-bottom: 1px solid #f0f0f0; vertical-align: middle;
      }}
      tbody tr:last-child td {{ border-bottom: none; }}
      tbody tr:hover td {{ background: #f6f8fa !important; }}
      .burndown-card {{
    background: #ffffff; border: 1px solid #d0d7de; border-radius: 10px;
    padding: 20px 24px; margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
      }}
      @media print {{
    body {{ background: #fff; padding: 16px; font-size: 11px; }}
    .report-header {{
      background: #1c2128 !important;
      -webkit-print-color-adjust: exact; print-color-adjust: exact;
    }}
    .stat-card, .card, .assignee-card, .table-wrap, .burndown-card {{
      box-shadow: none; break-inside: avoid;
    }}
    .section-heading {{ margin-top: 20px; }}
    thead th {{ position: static; }}
      }}
    </style>
    </head>
    <body>

    <div class="report-header">
      <h1>Sprint Report</h1>
      <div class="sub">{title}</div>
      <div class="meta">
    {"<span>&#128197; " + date_range + "</span>" if date_range else ""}
    <span>&#128197; Generated {today_str}</span>
    <span>&#128202; {n_total} stories &middot; {total_pts} points</span>
      </div>
    </div>

    <div class="section-heading">Summary</div>
    {stat_cards}

    <div class="section-heading">Burndown</div>
    <div class="burndown-card">
      <div class="card-title">Points Remaining Over Sprint</div>
      {burndown_svg}
    </div>

    <div class="section-heading">Status</div>
    {status_section}

    <div class="section-heading">Team</div>
    <div class="assignee-grid">{assignee_cards}</div>

    <div class="section-heading">All Stories</div>
    <div class="table-wrap">
    <table>
      <thead><tr>
    <th>Key</th><th>Summary</th><th>Assignee</th><th>Status</th>
    <th>Pri</th><th>Pts</th><th>Due</th><th>Type</th>
      </tr></thead>
      <tbody>{story_rows_html}</tbody>
    </table>
    </div>

    </body>
    </html>"""
        self._browser.setHtml(self._html)

    def _build_burndown_svg(self, total_pts: int, done_pts: int,
                            n_total: int, n_done: int) -> str:
        """Generate a burndown SVG using real sprint start/end dates when available."""
        W, H    = 680, 240
        PAD_L   = 52
        PAD_R   = 20
        PAD_T   = 24
        PAD_B   = 44
        chart_w = W - PAD_L - PAD_R
        chart_h = H - PAD_T - PAD_B

        today      = date.today()
        start_str  = (self._sprint_detail.get("startDate") or "")[:10]
        end_str    = (self._sprint_detail.get("endDate")   or "")[:10]
        try:
            sprint_start = date.fromisoformat(start_str)
            sprint_end   = date.fromisoformat(end_str)
            sprint_days  = max(1, (sprint_end - sprint_start).days)
            current_day  = max(0, min(sprint_days, (today - sprint_start).days))
        except (ValueError, TypeError):
            sprint_days = 14
            pct_elapsed = min(1.0, done_pts / total_pts) if total_pts else 0.0
            current_day = round(pct_elapsed * sprint_days)
            start_str   = ""
            end_str     = ""

        remaining = max(0, total_pts - done_pts)

        def px(day):
            return PAD_L + round(day / sprint_days * chart_w)

        def py(pts):
            if total_pts == 0:
                return PAD_T + chart_h
            return PAD_T + chart_h - round(pts / total_pts * chart_h)

        ideal_shade = (
            f"M{px(0)},{py(total_pts)} L{px(sprint_days)},{py(0)} "
            f"L{px(sprint_days)},{PAD_T + chart_h} L{px(0)},{PAD_T + chart_h} Z"
        )
        actual_shade = (
            f"M{px(0)},{py(total_pts)} L{px(current_day)},{py(remaining)} "
            f"L{px(current_day)},{PAD_T + chart_h} L{px(0)},{PAD_T + chart_h} Z"
        )

        grid = ""
        step = 1 if sprint_days <= 7 else 2
        for d in range(0, sprint_days + 1, step):
            gx = px(d)
            grid += (
                f'<line x1="{gx}" y1="{PAD_T}" x2="{gx}" y2="{PAD_T + chart_h}" '
                f'stroke="#f0f0f0" stroke-width="1"/>'
            )
        for i in range(6):
            v  = round(total_pts * i / 5) if total_pts else 0
            gy = py(v)
            grid += (
                f'<line x1="{PAD_L}" y1="{gy}" x2="{PAD_L + chart_w}" y2="{gy}" '
                f'stroke="#e9ecef" stroke-width="1"/>'
                f'<text x="{PAD_L - 8}" y="{gy + 4}" text-anchor="end" '
                f'fill="#8b949e" font-size="10" font-family="sans-serif">{v}</text>'
            )

        x_labels = "".join(
            f'<text x="{px(d)}" y="{PAD_T + chart_h + 16}" text-anchor="middle" '
            f'fill="#8b949e" font-size="10" font-family="sans-serif">{d}</text>'
            for d in range(0, sprint_days + 1, step)
        )

        ideal_at_today = (
            total_pts - round(total_pts * current_day / sprint_days)
            if sprint_days else total_pts
        )
        diff = ideal_at_today - remaining
        if diff > 0:
            callout_text  = f"\u25b2 {diff} pts ahead"
            callout_color = "#3fb950"
        elif diff < 0:
            callout_text  = f"\u25bc {abs(diff)} pts behind"
            callout_color = "#f78166"
        else:
            callout_text  = "On track"
            callout_color = "#8b949e"

        callout_x      = px(current_day)
        callout_anchor = "middle"
        if callout_x < PAD_L + 60:
            callout_anchor = "start"
        elif callout_x > PAD_L + chart_w - 60:
            callout_anchor = "end"

        callout = (
            f'<text x="{callout_x}" y="{py(remaining) - 14}" '
            f'text-anchor="{callout_anchor}" fill="{callout_color}" '
            f'font-size="11" font-weight="bold" font-family="sans-serif">'
            f'{callout_text}</text>'
        )

        date_note = f" \u00b7 {start_str} \u2192 {end_str}" if start_str and end_str else ""

        return f"""<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg"
     style="display:block;max-width:100%;">
      <rect x="{PAD_L}" y="{PAD_T}" width="{chart_w}" height="{chart_h}"
        fill="#fafbfc" rx="4" ry="4"/>
      {grid}
      <path d="{ideal_shade}" fill="#3fb950" fill-opacity="0.05"/>
      <path d="{actual_shade}" fill="#388bfd" fill-opacity="0.12"/>
      <line x1="{px(0)}" y1="{py(total_pts)}" x2="{px(sprint_days)}" y2="{py(0)}"
        stroke="#3fb950" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.7"/>
      <polyline points="{px(0)},{py(total_pts)} {px(current_day)},{py(remaining)}"
            fill="none" stroke="#388bfd" stroke-width="2.5"
            stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="{px(current_day)}" cy="{py(remaining)}" r="6"
          fill="#388bfd" stroke="#ffffff" stroke-width="2.5"/>
      {callout}
      <line x1="{PAD_L}" y1="{PAD_T}" x2="{PAD_L}" y2="{PAD_T + chart_h}"
        stroke="#d0d7de" stroke-width="1"/>
      <line x1="{PAD_L}" y1="{PAD_T + chart_h}"
        x2="{PAD_L + chart_w}" y2="{PAD_T + chart_h}" stroke="#d0d7de" stroke-width="1"/>
      {x_labels}
      <text x="{PAD_L + chart_w // 2}" y="{H - 4}" text-anchor="middle"
        fill="#8b949e" font-size="11" font-family="sans-serif">Sprint Day</text>
      <text x="10" y="{PAD_T + chart_h // 2}" text-anchor="middle"
        fill="#8b949e" font-size="11" font-family="sans-serif"
        transform="rotate(-90,10,{PAD_T + chart_h // 2})">Pts Remaining</text>
      <line x1="{PAD_L + chart_w - 148}" y1="{PAD_T + 10}"
        x2="{PAD_L + chart_w - 130}" y2="{PAD_T + 10}"
        stroke="#3fb950" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.7"/>
      <text x="{PAD_L + chart_w - 126}" y="{PAD_T + 14}"
        fill="#57606a" font-size="10" font-family="sans-serif">Ideal</text>
      <line x1="{PAD_L + chart_w - 90}" y1="{PAD_T + 10}"
        x2="{PAD_L + chart_w - 72}" y2="{PAD_T + 10}"
        stroke="#388bfd" stroke-width="2.5"/>
      <text x="{PAD_L + chart_w - 68}" y="{PAD_T + 14}"
        fill="#57606a" font-size="10" font-family="sans-serif">Actual</text>
    </svg>
    <p style="font-size:11px;color:#8b949e;margin:8px 0 0;font-family:sans-serif;">
      {total_pts} total pts \u00b7 {done_pts} done \u00b7 {remaining} remaining
      \u00b7 day {current_day} of {sprint_days}{date_note}
    </p>"""


    def _save_html(self):
        from PyQt6.QtWidgets import QFileDialog
        scope = self._sr_sprint_combo.currentText() if self._sr_scope_sprint_rb.isChecked() \
                else f"{self._sr_date_from.text()}-{self._sr_date_to.text()}"
        slug = re.sub(r"[^\w\-]", "-", scope or self._sprint_label)[:60]
        suggested = f"sprint-report-{slug}-{date.today()}.html"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Sprint Report", suggested,
            "HTML Files (*.html);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._html)
            QMessageBox.information(self, "Saved", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))

    # ── People Report ─────────────────────────────────────────────────────────
    def _on_sprints_loaded(self, sprints):
        for combo in (self._sr_sprint_combo, self._sprint_scope_combo):
            combo.clear()
            if not sprints:
                combo.addItem("No sprints found")
                continue
            for s in reversed(sprints):  # most recent first
                state = s.get("state", "")
                label = f"{s.get('name', '')}  [{state}]"
                combo.addItem(label, userData=s.get("id"))

        # Pre-select the current sprint in the Sprint Report combo if possible
        for i in range(self._sr_sprint_combo.count()):
            if self._sprint_label in (self._sr_sprint_combo.itemText(i) or ""):
                self._sr_sprint_combo.setCurrentIndex(i)
                break

        self._sr_sprint_combo.setEnabled(
            self._sr_scope_sprint_rb.isChecked() and bool(sprints)
        )
        self._sprint_scope_combo.setEnabled(
            self._scope_sprint_rb.isChecked() and bool(sprints)
        )

    def _generate_people_report(self):
        # Collect selected people
        selected = []
        for i in range(self._people_list.count()):
            item = self._people_list.item(i)
            if item.isSelected():
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        extras = [n.strip() for n in self._extra_people.text().split(",") if n.strip()]
        assignees = list(dict.fromkeys(selected + extras))  # dedupe, preserve order

        if not assignees:
            QMessageBox.warning(self, "No People Selected",
                                "Please select at least one person or enter a username.")
            return

        # Determine scope
        sprint_id = 0
        date_from = ""
        date_to   = ""
        scope_label = ""

        if self._scope_sprint_rb.isChecked():
            sprint_id  = self._sprint_scope_combo.currentData() or 0
            scope_label = self._sprint_scope_combo.currentText()
        else:
            date_from   = self._date_from.text().strip()
            date_to     = self._date_to.text().strip()
            scope_label = f"{date_from or '…'} → {date_to or '…'}"

        self._gen_btn.setEnabled(False)
        self._people_status.setText("Fetching issues…")
        self._people_browser.setHtml("<p style='color:#888;padding:20px;'>Loading…</p>")

        def _do():
            return self._client.get_issues_for_people_report(
                assignees=assignees,
                date_from=date_from,
                date_to=date_to,
                sprint_id=sprint_id,
                board_id=self._board_id,
            )

        def _on_done(issues):
            self._gen_btn.setEnabled(True)
            self._people_status.setText(f"✓ {len(issues)} issues fetched.")
            self._build_people_report(issues, assignees, scope_label)
            self._save_people_btn.setEnabled(True)

        def _on_err(e):
            self._gen_btn.setEnabled(True)
            self._people_status.setText(f"✗ {e}")
            self._people_browser.setHtml(
                f"<p style='color:#f78166;padding:20px;'>Error: {e}</p>"
            )

        worker = Worker(_do)
        worker.result.connect(_on_done)
        worker.error.connect(_on_err)
        worker.start()
        self._people_report_worker = worker

    def _build_people_report(self, issues: list, assignees: list, scope_label: str):
        sp    = self._sp_field
        today = date.today().strftime("%Y-%m-%d")

        # ── Group issues by assignee username ─────────────────────────────────
        by_assignee: dict[str, dict] = {}
        for a in assignees:
            by_assignee[a] = {
                "display": a, "total": 0, "done": 0,
                "pts": 0, "done_pts": 0,
                "by_status": {},
                "cycle_times": [],
                "issues": [],
            }

        for iss in issues:
            f     = iss.get("fields", {})
            aobj  = f.get("assignee") or {}
            aname = aobj.get("name") or aobj.get("accountId") or ""
            if aname not in by_assignee:
                continue
            rec = by_assignee[aname]
            rec["display"] = aobj.get("displayName") or aname

            status = (f.get("status") or {}).get("name", "—")
            pts_raw = next((f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS) if f.get(k) is not None), None)
            try:
                pts = int(float(pts_raw)) if pts_raw is not None else 0
            except (TypeError, ValueError):
                pts = 0

            rec["total"] += 1
            rec["pts"]   += pts
            rec["by_status"][status] = rec["by_status"].get(status, 0) + 1

            if status == "Done":
                rec["done"]      += 1
                rec["done_pts"]  += pts
                created     = f.get("created", "")[:10]
                resolved    = f.get("resolutiondate", "")[:10]
                if created and resolved:
                    try:
                        ct = (date.fromisoformat(resolved) - date.fromisoformat(created)).days
                        rec["cycle_times"].append(max(0, ct))
                    except ValueError:
                        pass

            rec["issues"].append(iss)

        # ── Shared CSS ────────────────────────────────────────────────────────
        STATUS_CSS = {
            "To Do":       "#6e7681", "In Progress": "#388bfd",
            "Done":        "#3fb950", "In Review":   "#39d5f5",
            "Blocked":     "#f78166",
        }

        def badge(name):
            col = STATUS_CSS.get(name, "#8b949e")
            return (f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;'
                    f'font-size:11px;font-weight:bold;background:{col}22;color:{col};'
                    f'border:1px solid {col}55;">{name}</span>')

        def bar(pct, colour="#388bfd", width=140):
            filled = max(0, min(pct, 100))
            return (f'<div style="display:inline-block;width:{width}px;height:8px;'
                    f'background:#e0e0e0;border-radius:4px;vertical-align:middle;">'
                    f'<div style="width:{filled}%;height:8px;background:{colour};'
                    f'border-radius:4px;"></div></div>&nbsp;{pct}%')

        td = "padding:8px 12px;border-bottom:1px solid #e0e0e0;vertical-align:middle;"
        th = ("padding:8px 12px;background:#f6f8fa;font-size:11px;letter-spacing:.5px;"
              "text-transform:uppercase;border-bottom:2px solid #d0d7de;text-align:left;")

        # ── Summary table ─────────────────────────────────────────────────────
        summary_rows = []
        for aname in assignees:
            rec  = by_assignee.get(aname, {})
            if not rec:
                continue
            done_pct = round(rec["done"] / rec["total"] * 100) if rec["total"] else 0
            pts_pct  = round(rec["done_pts"] / rec["pts"] * 100) if rec["pts"] else 0
            avg_ct   = (round(sum(rec["cycle_times"]) / len(rec["cycle_times"]), 1)
                        if rec["cycle_times"] else "—")
            status_breakdown = " &nbsp; ".join(
                f'{badge(s)} ×{c}' for s, c in sorted(rec["by_status"].items())
            )
            summary_rows.append(
                f"<tr>"
                f"<td><strong>{rec.get('display', aname)}</strong></td>"
                f"<td style='text-align:center;'>{rec['total']}</td>"
                f"<td style='text-align:center;'>{rec['done']}</td>"
                f"<td>{bar(done_pct, '#3fb950')}</td>"
                f"<td style='text-align:center;'>{rec['pts']}</td>"
                f"<td style='text-align:center;'>{rec['done_pts']}</td>"
                f"<td>{bar(pts_pct, '#388bfd')}</td>"
                f"<td style='text-align:center;'>{avg_ct}</td>"
                f"<td>{status_breakdown}</td>"
                f"</tr>"
            )

        # ── Per-person detail sections ─────────────────────────────────────────
        detail_sections = []
        for aname in assignees:
            rec = by_assignee.get(aname, {})
            if not rec or not rec["issues"]:
                continue
            rows = []
            for iss in sorted(rec["issues"], key=lambda i: i.get("key", "")):
                f      = iss.get("fields", {})
                key    = iss.get("key", "")
                summ   = f.get("summary", "")
                status = (f.get("status") or {}).get("name", "—")
                pri    = (f.get("priority") or {}).get("name", "—")
                itype  = (f.get("issuetype") or {}).get("name", "—")
                due    = (f.get("duedate") or "")[:10] or "—"
                pts_raw = next((f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS) if f.get(k) is not None), None)
                try:
                    pts_str = str(int(float(pts_raw))) if pts_raw is not None else "—"
                except (TypeError, ValueError):
                    pts_str = "—"
                resolved = (f.get("resolutiondate") or "")[:10] or "—"
                key_cell = (f'<a href="{self._base_url}/browse/{key}" style="color:#388bfd;">{key}</a>'
                            if self._base_url else key)
                due_style = ""
                if due != "—":
                    try:
                        days = (date.fromisoformat(due) - date.today()).days
                        if days < 0:
                            due_style = "color:#f78166;font-weight:bold;"
                        elif days <= 3:
                            due_style = "color:#e3b341;"
                    except ValueError:
                        pass
                rows.append(
                    f"<tr>"
                    f"<td>{key_cell}</td><td>{summ}</td>"
                    f"<td>{badge(status)}</td>"
                    f"<td style='text-align:center;'>{pts_str}</td>"
                    f"<td style='text-align:center;{due_style}'>{due}</td>"
                    f"<td>{resolved}</td><td>{itype}</td><td>{pri}</td>"
                    f"</tr>"
                )
            done_pct = round(rec["done"] / rec["total"] * 100) if rec["total"] else 0
            detail_sections.append(f"""
<h2 style="margin-top:36px;border-bottom:2px solid #d0d7de;padding-bottom:6px;">
  {rec.get('display', aname)}
  <span style="font-size:13px;font-weight:400;color:#57606a;margin-left:12px;">
    {rec['total']} stories &nbsp;·&nbsp; {rec['done']} done &nbsp;·&nbsp;
    {rec['pts']} pts total &nbsp;·&nbsp; {rec['done_pts']} pts done &nbsp;·&nbsp;
    {done_pct}% complete
  </span>
</h2>
<table>
  <tr>
    <th>Key</th><th>Summary</th><th>Status</th><th>Pts</th>
    <th>Due</th><th>Resolved</th><th>Type</th><th>Priority</th>
  </tr>
  {"".join(rows)}
</table>""")

        self._people_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>People Report — {scope_label}</title>
<style>
  body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
          color:#1f2328;background:transparent;margin:0;padding:32px; }}
  h1   {{ font-size:22px;font-weight:700;margin:0 0 4px; }}
  h2   {{ font-size:16px;font-weight:700; }}
  .meta {{ font-size:12px;color:#57606a;margin-bottom:28px; }}
  table {{ border-collapse:collapse;width:100%;font-size:13px;margin-bottom:24px; }}
  th    {{ {th} }}
  td    {{ {td} }}
  tr:last-child td {{ border-bottom:none; }}
  tr:hover td {{ background:#f6f8fa; }}
</style>
</head>
<body>
<h1>People Report</h1>
<div class="meta">
  Scope: {scope_label} &nbsp;·&nbsp;
  People: {", ".join(by_assignee[a].get("display", a) for a in assignees if a in by_assignee)} &nbsp;·&nbsp;
  Generated {today}
</div>

<h2 style="margin-bottom:10px;">Summary</h2>
<table>
  <tr>
    <th>Person</th><th>Stories</th><th>Done</th><th>Story Progress</th>
    <th>Total Pts</th><th>Done Pts</th><th>Points Progress</th>
    <th>Avg Cycle (days)</th><th>By Status</th>
  </tr>
  {"".join(summary_rows)}
</table>

{"".join(detail_sections)}
</body>
</html>"""

        self._people_browser.setHtml(self._people_html)

    def _save_people_html(self):
        from PyQt6.QtWidgets import QFileDialog
        suggested = f"people-report-{date.today()}.html"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save People Report", suggested,
            "HTML Files (*.html);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._people_html)
            QMessageBox.information(self, "Saved", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))


# ── Sprint Manager Dialog ─────────────────────────────────────────────────────
class SprintManagerDialog(QDialog):
    """Create a new sprint, or start / close / rename the active sprint."""

    sprint_changed = pyqtSignal()   # emitted after any successful operation

    def __init__(self, board_id: int, board_name: str, sprints: list,
                 client, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sprint Manager")
        self.setMinimumSize(520, 480)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        self._board_id   = board_id
        self._board_name = board_name
        self._sprints    = sprints
        self._client     = client

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(12)

        heading = QLabel(f"◈  SPRINT MANAGER  —  {board_name}")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        tabs = QTabWidget()
        layout.addWidget(tabs, 1)

        # ── Tab 1: Create Sprint ──────────────────────────────────────────────
        create_tab = QWidget()
        cl = QVBoxLayout(create_tab)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(10)

        cf = QFormLayout()
        cf.setSpacing(10)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. Sprint 43")
        cf.addRow("Sprint Name *:", self._name_edit)

        self._goal_edit = QLineEdit()
        self._goal_edit.setPlaceholderText("Optional sprint goal")
        cf.addRow("Goal:", self._goal_edit)

        self._start_edit = QDateEdit()
        self._start_edit.setCalendarPopup(True)
        self._start_edit.setDisplayFormat("yyyy-MM-dd")
        self._start_edit.setDate(QDate.currentDate())
        cf.addRow("Start Date:", self._start_edit)

        self._end_edit = QDateEdit()
        self._end_edit.setCalendarPopup(True)
        self._end_edit.setDisplayFormat("yyyy-MM-dd")
        self._end_edit.setDate(QDate.currentDate().addDays(14))
        cf.addRow("End Date:", self._end_edit)

        self._start_now_cb = QRadioButton("Create and immediately start this sprint")
        self._create_only_cb = QRadioButton("Create as future sprint (start later)")
        self._create_only_cb.setChecked(True)
        cf.addRow("", self._start_now_cb)
        cf.addRow("", self._create_only_cb)

        cl.addLayout(cf)

        self._create_status = QLabel("")
        self._create_status.setObjectName("dim")
        self._create_status.setWordWrap(True)
        cl.addWidget(self._create_status)
        cl.addStretch()

        self._create_btn = QPushButton("＋  Create Sprint")
        self._create_btn.setObjectName("save_btn")
        self._create_btn.clicked.connect(self._do_create)
        cl.addWidget(self._create_btn)

        tabs.addTab(create_tab, "＋  Create")

        # ── Tab 2: Manage Existing Sprint ────────────────────────────────────
        manage_tab = QWidget()
        ml = QVBoxLayout(manage_tab)
        ml.setContentsMargins(16, 16, 16, 16)
        ml.setSpacing(10)

        sf = QFormLayout()
        sf.setSpacing(10)

        self._sprint_combo = QComboBox()
        for s in sprints:
            state = s.get("state", "")
            self._sprint_combo.addItem(f"[{state.upper()}]  {s['name']}", s["id"])
        self._sprint_combo.currentIndexChanged.connect(self._on_sprint_selected)
        sf.addRow("Sprint:", self._sprint_combo)

        self._edit_name = QLineEdit()
        sf.addRow("Rename to:", self._edit_name)

        self._edit_goal = QLineEdit()
        self._edit_goal.setPlaceholderText("Optional")
        sf.addRow("Goal:", self._edit_goal)

        self._edit_start = QDateEdit()
        self._edit_start.setCalendarPopup(True)
        self._edit_start.setDisplayFormat("yyyy-MM-dd")
        sf.addRow("Start Date:", self._edit_start)

        self._edit_end = QDateEdit()
        self._edit_end.setCalendarPopup(True)
        self._edit_end.setDisplayFormat("yyyy-MM-dd")
        sf.addRow("End Date:", self._edit_end)

        ml.addLayout(sf)

        self._manage_status = QLabel("")
        self._manage_status.setObjectName("dim")
        self._manage_status.setWordWrap(True)
        ml.addWidget(self._manage_status)
        ml.addStretch()

        action_row = QHBoxLayout()
        self._save_btn = QPushButton("💾  Save Changes")
        self._save_btn.setObjectName("save_btn")
        self._save_btn.clicked.connect(self._do_save)
        action_row.addWidget(self._save_btn)
        action_row.addStretch()
        self._start_btn = QPushButton("▶  Start Sprint")
        self._start_btn.setObjectName("toolbar_btn")
        self._start_btn.clicked.connect(self._do_start)
        action_row.addWidget(self._start_btn)
        self._close_btn = QPushButton("■  Close Sprint")
        self._close_btn.setObjectName("danger")
        self._close_btn.clicked.connect(self._do_close)
        action_row.addWidget(self._close_btn)
        ml.addLayout(action_row)

        tabs.addTab(manage_tab, "⚙  Manage")

        close_row = QHBoxLayout()
        close_row.addStretch()
        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self.accept)
        close_row.addWidget(done_btn)
        layout.addLayout(close_row)

        # Populate manage tab with first sprint
        if sprints:
            self._on_sprint_selected(0)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _selected_sprint(self) -> dict:
        idx = self._sprint_combo.currentIndex()
        if idx < 0 or idx >= len(self._sprints):
            return {}
        return self._sprints[idx]

    def _on_sprint_selected(self, idx: int):
        s = self._selected_sprint()
        if not s:
            return
        self._edit_name.setText(s.get("name", ""))
        self._edit_goal.setText(s.get("goal", "") or "")

        def _parse_date(val):
            raw = (val or "")[:10]
            try:
                d = date.fromisoformat(raw)
                return QDate(d.year, d.month, d.day)
            except ValueError:
                return QDate.currentDate()

        self._edit_start.setDate(_parse_date(s.get("startDate")))
        self._edit_end.setDate(_parse_date(s.get("endDate")))

        state = s.get("state", "").lower()
        self._start_btn.setEnabled(state == "future")
        self._close_btn.setEnabled(state == "active")
        self._save_btn.setEnabled(True)

    def _to_iso(self, qdate: QDate, time_suffix: str = "T09:00:00.000Z") -> str:
        return qdate.toString("yyyy-MM-dd") + time_suffix

    # ── Create ────────────────────────────────────────────────────────────────
    def _do_create(self):
        name = self._name_edit.text().strip()
        if not name:
            self._create_status.setText("⚠ Sprint name is required.")
            return
        start = self._to_iso(self._start_edit.date())
        end   = self._to_iso(self._end_edit.date(), "T17:00:00.000Z")
        goal  = self._goal_edit.text().strip()
        start_now = self._start_now_cb.isChecked()

        self._create_btn.setEnabled(False)
        self._create_status.setText("Creating sprint…")

        class _W(QThread):
            result = pyqtSignal(object)
            error  = pyqtSignal(str)
            def __init__(self, fn, *a):
                super().__init__()
                self._fn, self._a = fn, a
            def run(self):
                try:    self.result.emit(self._fn(*self._a))
                except Exception as e: self.error.emit(str(e))

        def _on_done(sprint):
            sid  = sprint.get("id")
            sname = sprint.get("name", name)
            if start_now and sid:
                try:
                    self._client.update_sprint(sid, state="active",
                                               startDate=start, endDate=end)
                    self._create_status.setText(f'✓ Sprint "{sname}" created and started.')
                except Exception as e:
                    self._create_status.setText(
                        f'✓ Sprint "{sname}" created (id {sid}), '
                        f'but could not start it: {e}'
                    )
            else:
                self._create_status.setText(f'✓ Sprint "{sname}" created (id {sid}).')
            self._create_btn.setEnabled(True)
            self._name_edit.clear()
            self._goal_edit.clear()
            self.sprint_changed.emit()

        def _on_err(e):
            self._create_status.setText(f"✗ {e}")
            self._create_btn.setEnabled(True)

        w = _W(self._client.create_sprint, self._board_id, name, start, end, goal)
        w.result.connect(_on_done)
        w.error.connect(_on_err)
        w.start()
        self._w_create = w

    # ── Save (rename / update dates / goal) ───────────────────────────────────
    def _do_save(self):
        s = self._selected_sprint()
        if not s:
            return
        sid   = s["id"]
        name  = self._edit_name.text().strip() or s.get("name", "")
        goal  = self._edit_goal.text().strip()
        start = self._to_iso(self._edit_start.date())
        end   = self._to_iso(self._edit_end.date(), "T17:00:00.000Z")

        self._save_btn.setEnabled(False)
        self._manage_status.setText("Saving…")

        self._run_manage(
            self._client.update_sprint, sid,
            name=name, goal=goal, startDate=start, endDate=end,
            on_ok=lambda _: (
                self._manage_status.setText(f"✓ Sprint updated."),
                self._save_btn.setEnabled(True),
                self.sprint_changed.emit(),
            ),
            on_err=lambda e: (
                self._manage_status.setText(f"✗ {e}"),
                self._save_btn.setEnabled(True),
            ),
        )

    # ── Start ─────────────────────────────────────────────────────────────────
    def _do_start(self):
        s = self._selected_sprint()
        if not s:
            return
        sid   = s["id"]
        start = self._to_iso(self._edit_start.date())
        end   = self._to_iso(self._edit_end.date(), "T17:00:00.000Z")

        reply = QMessageBox.question(
            self, "Start Sprint",
            f'Start sprint  "{s["name"]}"?\n\n'
            f'Start: {self._edit_start.date().toString("yyyy-MM-dd")}\n'
            f'End:   {self._edit_end.date().toString("yyyy-MM-dd")}\n\n'
            "Only one sprint can be active at a time. "
            "If another sprint is already active this will fail.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._start_btn.setEnabled(False)
        self._manage_status.setText("Starting sprint…")
        self._run_manage(
            self._client.update_sprint, sid,
            state="active", startDate=start, endDate=end,
            on_ok=lambda _: (
                self._manage_status.setText(f'✓ Sprint "{s["name"]}" is now active.'),
                self._start_btn.setEnabled(False),
                self._close_btn.setEnabled(True),
                self.sprint_changed.emit(),
            ),
            on_err=lambda e: (
                self._manage_status.setText(f"✗ {e}"),
                self._start_btn.setEnabled(True),
            ),
        )

    # ── Close ─────────────────────────────────────────────────────────────────
    def _do_close(self):
        s = self._selected_sprint()
        if not s:
            return
        sid = s["id"]

        reply = QMessageBox.question(
            self, "Close Sprint",
            f'Close sprint  "{s["name"]}"?\n\n'
            "Incomplete stories will remain on the board and can be moved "
            "to a future sprint. This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._close_btn.setEnabled(False)
        self._manage_status.setText("Closing sprint…")
        complete = self._to_iso(QDate.currentDate(), "T17:00:00.000Z")
        self._run_manage(
            self._client.update_sprint, sid,
            state="closed", completeDate=complete,
            on_ok=lambda _: (
                self._manage_status.setText(f'✓ Sprint "{s["name"]}" closed.'),
                self._close_btn.setEnabled(False),
                self._start_btn.setEnabled(False),
                self.sprint_changed.emit(),
            ),
            on_err=lambda e: (
                self._manage_status.setText(f"✗ {e}"),
                self._close_btn.setEnabled(True),
            ),
        )

    # ── Thread runner ─────────────────────────────────────────────────────────
    def _run_manage(self, fn, *args, on_ok, on_err, **kwargs):
        class _W(QThread):
            result = pyqtSignal(object)
            error  = pyqtSignal(str)
            def __init__(self, fn, *a, **kw):
                super().__init__()
                self._fn, self._a, self._kw = fn, a, kw
            def run(self):
                try:    self.result.emit(self._fn(*self._a, **self._kw))
                except Exception as e: self.error.emit(str(e))

        w = _W(fn, *args, **kwargs)
        w.result.connect(on_ok)
        w.error.connect(on_err)
        w.start()
        self._w_manage = w   # keep alive


# ── Velocity History Dialog ───────────────────────────────────────────────────
class VelocityHistoryDialog(QDialog):
    """Shows a bar chart of points committed vs completed across recent closed sprints."""

    def __init__(self, board_id: int, client, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Velocity History")
        self.setMinimumSize(740, 460)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self._board_id = board_id
        self._client   = client

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("◈  VELOCITY HISTORY")
        title.setObjectName("heading")
        layout.addWidget(title)

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Sprints to show:"))
        self._num_combo = QComboBox()
        for n in [3, 5, 6, 8, 10]:
            self._num_combo.addItem(str(n), n)
        self._num_combo.setCurrentIndex(2)   # default 6
        ctrl.addWidget(self._num_combo)
        self._gen_btn = QPushButton("▶  Load")
        self._gen_btn.setObjectName("toolbar_btn")
        self._gen_btn.clicked.connect(self._load)
        ctrl.addWidget(self._gen_btn)
        self._status_lbl = QLabel("")
        self._status_lbl.setObjectName("dim")
        ctrl.addWidget(self._status_lbl, 1)
        layout.addLayout(ctrl)

        # SVG chart area
        self._chart_lbl = QLabel()
        self._chart_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._chart_lbl.setMinimumHeight(300)
        self._chart_lbl.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid {BORDER}; border-radius: 8px;")
        layout.addWidget(self._chart_lbl, 1)

        # Summary table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Sprint", "Total Pts", "Done Pts", "Stories", "Done"])
        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, 5):
            hh.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.setMaximumHeight(180)
        layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        self._export_btn = QPushButton("⬇  Export CSV")
        self._export_btn.setObjectName("toolbar_btn")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._export_csv)
        btn_row.addWidget(self._export_btn)
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._data: list = []
        self._load()

    def _load(self):
        self._gen_btn.setEnabled(False)
        self._status_lbl.setText("Loading sprint history…")
        num = self._num_combo.currentData()

        from PyQt6.QtCore import QThread, pyqtSignal as _sig

        class _W(QThread):
            result = _sig(object)
            error  = _sig(str)
            def __init__(self, fn, *a):
                super().__init__()
                self._fn, self._a = fn, a
            def run(self):
                try:    self.result.emit(self._fn(*self._a))
                except Exception as e: self.error.emit(str(e))

        w = _W(self._client.get_velocity_history, self._board_id, num)
        w.result.connect(self._on_data)
        w.error.connect(lambda e: (
            self._status_lbl.setText(f"✗ {e}"),
            self._gen_btn.setEnabled(True),
        ))
        w.start()
        self._w = w

    def _on_data(self, data: list):
        self._data = data
        self._gen_btn.setEnabled(True)
        self._export_btn.setEnabled(bool(data))
        if not data:
            self._status_lbl.setText("No closed sprints found.")
            return
        self._status_lbl.setText(f"✓ {len(data)} sprints loaded.")
        self._render_chart(data)
        self._populate_table(data)

    def _render_chart(self, data: list):
        W, H      = 680, 280
        PAD_L     = 52
        PAD_R     = 16
        PAD_T     = 20
        PAD_B     = 60
        chart_w   = W - PAD_L - PAD_R
        chart_h   = H - PAD_T - PAD_B
        n         = len(data)
        max_pts   = max((d["total_pts"] for d in data), default=1) or 1
        bar_group = chart_w / n
        bar_w     = max(4, int(bar_group * 0.35))
        gap       = max(2, int(bar_group * 0.06))

        def py(pts):
            return PAD_T + chart_h - round(pts / max_pts * chart_h)

        bars = ""
        x_labels = ""
        for i, d in enumerate(data):
            cx   = PAD_L + int(i * bar_group + bar_group / 2)
            # Committed bar (total)
            bx1  = cx - bar_w - gap // 2
            bh1  = round(d["total_pts"] / max_pts * chart_h)
            by1  = PAD_T + chart_h - bh1
            # Done bar
            bx2  = cx + gap // 2
            bh2  = round(d["done_pts"]  / max_pts * chart_h)
            by2  = PAD_T + chart_h - bh2
            bars += (
                f'<rect x="{bx1}" y="{by1}" width="{bar_w}" height="{bh1}" '
                f'fill="{ACCENT_BLUE}" rx="3" opacity="0.7"/>'
                f'<rect x="{bx2}" y="{by2}" width="{bar_w}" height="{bh2}" '
                f'fill="{ACCENT_GREEN}" rx="3"/>'
            )
            if d["total_pts"]:
                bars += (
                    f'<text x="{bx1 + bar_w//2}" y="{by1 - 4}" text-anchor="middle" '
                    f'fill="{TEXT_SEC}" font-size="9">{d["total_pts"]}</text>'
                    f'<text x="{bx2 + bar_w//2}" y="{by2 - 4}" text-anchor="middle" '
                    f'fill="{ACCENT_GREEN}" font-size="9">{d["done_pts"]}</text>'
                )
            short = d["name"][:14] + "…" if len(d["name"]) > 14 else d["name"]
            x_labels += (
                f'<text x="{cx}" y="{PAD_T + chart_h + 16}" text-anchor="middle" '
                f'fill="{TEXT_SEC}" font-size="9">{short}</text>'
            )

        # Y-axis ticks
        y_ticks = ""
        for v in range(0, int(max_pts) + 1, max(1, int(max_pts) // 5)):
            yy = py(v)
            y_ticks += (
                f'<line x1="{PAD_L}" y1="{yy}" x2="{PAD_L + chart_w}" y2="{yy}" '
                f'stroke="{BORDER}" stroke-width="1"/>'
                f'<text x="{PAD_L - 6}" y="{yy + 4}" text-anchor="end" '
                f'fill="{TEXT_SEC}" font-size="9">{v}</text>'
            )

        legend = (
            f'<rect x="{PAD_L}" y="{H - 18}" width="12" height="10" fill="{ACCENT_BLUE}" rx="2" opacity="0.7"/>'
            f'<text x="{PAD_L + 16}" y="{H - 9}" fill="{TEXT_SEC}" font-size="10">Committed</text>'
            f'<rect x="{PAD_L + 90}" y="{H - 18}" width="12" height="10" fill="{ACCENT_GREEN}" rx="2"/>'
            f'<text x="{PAD_L + 106}" y="{H - 9}" fill="{TEXT_SEC}" font-size="10">Completed</text>'
        )

        svg = (
            f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" '
            f'style="background:{DARK_BG};">'
            f'{y_ticks}{bars}{x_labels}{legend}'
            f'<line x1="{PAD_L}" y1="{PAD_T}" x2="{PAD_L}" y2="{PAD_T + chart_h}" '
            f'stroke="{BORDER}" stroke-width="1"/>'
            f'<line x1="{PAD_L}" y1="{PAD_T + chart_h}" x2="{PAD_L + chart_w}" y2="{PAD_T + chart_h}" '
            f'stroke="{BORDER}" stroke-width="1"/>'
            f'</svg>'
        )
        pix = QPixmap(W, H)
        pix.fill(QColor(DARK_BG))
        try:
            from PyQt6.QtSvg import QSvgRenderer
            renderer = QSvgRenderer(QByteArray(svg.encode()))
            painter  = QPainter(pix)
            renderer.render(painter)
            painter.end()
        except ImportError:
            # PyQt6.QtSvg not available — fall back to text label
            self._chart_lbl.setText(
                "Install PyQt6-Qt6-Svg for chart rendering.\n"
                "pip install PyQt6-Qt6-Svg"
            )
            return
        self._chart_lbl.setPixmap(pix)

    def _populate_table(self, data: list):
        self._table.setRowCount(0)
        for d in data:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(d["name"]))
            for c, val in enumerate([d["total_pts"], d["done_pts"], d["n_total"], d["n_done"]], 1):
                it = QTableWidgetItem(str(val))
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c == 2:
                    it.setForeground(QColor(ACCENT_GREEN))
                self._table.setItem(row, c, it)
            self._table.setRowHeight(row, 32)

    def _export_csv(self):
        if not self._data:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Velocity CSV", "velocity-history.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["sprint", "total_pts", "done_pts", "n_total", "n_done"])
                for d in self._data:
                    w.writerow([d["name"], d["total_pts"], d["done_pts"], d["n_total"], d["n_done"]])
            QMessageBox.information(self, "Exported", f"Velocity data saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))


# ── Kanban Board ──────────────────────────────────────────────────────────────
KANBAN_STATUSES = ["To Do", "In Progress", "In Review", "Done", "Blocked"]
KANBAN_MIME     = "application/x-sprintmate-kanban-key"


class KanbanCard(QFrame):
    """Single draggable story card on the Kanban board."""
    clicked = pyqtSignal(str)  # emits issue key

    def __init__(self, issue: dict, sp_field: str, parent=None):
        super().__init__(parent)
        self._key   = issue.get("key", "")
        self._issue = issue
        self.setObjectName("card")
        self.setFixedWidth(220)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAcceptDrops(False)

        f       = issue.get("fields", {})
        summary = f.get("summary", "")[:80]
        aobj    = f.get("assignee") or {}
        assignee = aobj.get("displayName") or aobj.get("name") or "—"
        pts_raw = next((f.get(k) for k in ([sp_field] + JiraClient._SP_FALLBACKS)
                        if f.get(k) is not None), None)
        try:
            pts = str(int(float(pts_raw))) if pts_raw is not None else "—"
        except (TypeError, ValueError):
            pts = "—"
        status  = (f.get("status") or {}).get("name", "")
        color   = STATUS_COLORS.get(status, TEXT_SEC)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        key_lbl = QLabel(self._key)
        key_lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 11px; font-weight: bold;")
        layout.addWidget(key_lbl)

        sum_lbl = QLabel(summary)
        sum_lbl.setWordWrap(True)
        sum_lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px;")
        layout.addWidget(sum_lbl)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 4, 0, 0)
        a_lbl = QLabel(assignee)
        a_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px;")
        a_lbl.setMaximumWidth(130)
        footer.addWidget(a_lbl, 1)
        pts_lbl = QLabel(f"◈ {pts} pts")
        pts_lbl.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
        footer.addWidget(pts_lbl)
        layout.addLayout(footer)

        self.setStyleSheet(f"""
            KanbanCard {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-left: 3px solid {color};
                border-radius: 6px;
            }}
            KanbanCard:hover {{
                border-color: {ACCENT_BLUE};
                border-left-color: {color};
            }}
        """)

    @property
    def key(self):
        return self._key

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.position().toPoint() - self._drag_start).manhattanLength() < 10:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(KANBAN_MIME, self._key.encode())
        drag.setMimeData(mime)
        # Render a ghost pixmap
        pix = QPixmap(self.size())
        pix.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pix)
        painter.setOpacity(0.75)
        self.render(painter)
        painter.end()
        drag.setPixmap(pix)
        drag.setHotSpot(self._drag_start)
        drag.exec(Qt.DropAction.MoveAction)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if (event.position().toPoint() - getattr(self, '_drag_start', QPoint())).manhattanLength() < 10:
                self.clicked.emit(self._key)
        super().mouseReleaseEvent(event)


class KanbanColumn(QFrame):
    """One status column on the Kanban board; accepts card drops."""
    card_dropped = pyqtSignal(str, str)  # (issue_key, new_status)

    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self._status = status
        self.setAcceptDrops(True)
        self.setMinimumWidth(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        color = STATUS_COLORS.get(status, TEXT_SEC)
        self.setStyleSheet(f"""
            KanbanColumn {{
                background-color: {PANEL_BG};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(6)

        # Header
        hdr = QHBoxLayout()
        self._hdr_lbl = QLabel(status.upper())
        self._hdr_lbl.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: bold; letter-spacing: 1px;"
        )
        hdr.addWidget(self._hdr_lbl)
        self._count_lbl = QLabel("0")
        self._count_lbl.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; background: {CARD_BG}; "
            f"padding: 1px 6px; border-radius: 8px;"
        )
        hdr.addWidget(self._count_lbl)
        hdr.addStretch()
        outer.addLayout(hdr)

        # Scrollable card area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._card_container = QWidget()
        self._card_container.setStyleSheet("background: transparent;")
        self._cards_layout = QVBoxLayout(self._card_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(6)
        self._cards_layout.addStretch()

        scroll.setWidget(self._card_container)
        outer.addWidget(scroll, 1)

        self._cards: list[KanbanCard] = []
        self._highlight = False

    def add_card(self, card: KanbanCard):
        self._cards.append(card)
        # Insert before the stretch
        self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)
        self._count_lbl.setText(str(len(self._cards)))

    def clear_cards(self):
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()
        self._count_lbl.setText("0")

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(KANBAN_MIME):
            event.acceptProposedAction()
            self._set_highlight(True)

    def dragLeaveEvent(self, event):
        self._set_highlight(False)

    def dropEvent(self, event):
        self._set_highlight(False)
        if event.mimeData().hasFormat(KANBAN_MIME):
            key = event.mimeData().data(KANBAN_MIME).data().decode()
            event.acceptProposedAction()
            self.card_dropped.emit(key, self._status)

    def _set_highlight(self, on: bool):
        color = ACCENT_BLUE if on else BORDER
        self.setStyleSheet(f"""
            KanbanColumn {{
                background-color: {PANEL_BG};
                border: 1px solid {color};
                border-radius: 8px;
            }}
        """)


class KanbanBoardWidget(QWidget):
    """Full Kanban board: one column per status, drag-and-drop between them."""
    story_selected       = pyqtSignal(str)
    transition_requested = pyqtSignal(str, str)
    new_story_requested  = pyqtSignal()
    load_requested       = pyqtSignal()   # ask MainWindow to load the current sprint

    def __init__(self, parent=None):
        super().__init__(parent)
        self._columns: dict[str, KanbanColumn] = {}
        self._sp_field     = ""
        self._last_issues: list = []
        self._all_issues:  list = []
        self._base_url     = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # ── Load toolbar (shown when board is empty) ───────────────────────────
        self._load_bar = QFrame()
        self._load_bar.setStyleSheet(
            f"QFrame {{ background: {PANEL_BG}; border: 1px solid {BORDER}; "
            f"border-radius: 8px; }}"
        )
        lb = QHBoxLayout(self._load_bar)
        lb.setContentsMargins(12, 8, 12, 8)
        lb.setSpacing(8)
        lb.addWidget(QLabel("PROJECT"))
        self._kb_project_combo = QComboBox()
        self._kb_project_combo.setMinimumWidth(160)
        self._kb_project_combo.setEnabled(False)
        lb.addWidget(self._kb_project_combo)
        lb.addWidget(QLabel("BOARD"))
        self._kb_board_combo = QComboBox()
        self._kb_board_combo.setMinimumWidth(160)
        self._kb_board_combo.setEnabled(False)
        lb.addWidget(self._kb_board_combo)
        lb.addWidget(QLabel("SPRINT"))
        self._kb_sprint_combo = QComboBox()
        self._kb_sprint_combo.setMinimumWidth(180)
        self._kb_sprint_combo.setEnabled(False)
        lb.addWidget(self._kb_sprint_combo)
        self._kb_load_btn = QPushButton("↺  Load")
        self._kb_load_btn.setObjectName("toolbar_btn")
        self._kb_load_btn.setEnabled(False)
        self._kb_load_btn.clicked.connect(self._on_kb_load_clicked)
        lb.addWidget(self._kb_load_btn)
        lb.addStretch()
        self._kb_hint = QLabel("Select a sprint and click Load to populate the board.")
        self._kb_hint.setObjectName("dim")
        lb.addWidget(self._kb_hint)
        layout.addWidget(self._load_bar)

        # ── Board header ──────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        self._title_lbl = QLabel("◈  ACTIVE SPRINT")
        self._title_lbl.setObjectName("heading")
        hdr.addWidget(self._title_lbl)
        hdr.addStretch()
        new_btn = QPushButton("＋  New Story")
        new_btn.setObjectName("toolbar_btn")
        new_btn.clicked.connect(self.new_story_requested.emit)
        hdr.addWidget(new_btn)
        self._status_lbl = QLabel("No stories loaded")
        self._status_lbl.setObjectName("dim")
        hdr.addWidget(self._status_lbl)
        layout.addLayout(hdr)

        # ── Filter bar ────────────────────────────────────────────────────────
        filter_bar = QFrame()
        filter_bar.setStyleSheet(
            f"QFrame {{ background: transparent; border-bottom: 1px solid {BORDER}; "
            f"padding-bottom: 4px; }}"
        )
        fb = QHBoxLayout(filter_bar)
        fb.setContentsMargins(0, 0, 0, 6)
        fb.setSpacing(8)

        self._filter_edit = QLineEdit()
        self._filter_edit.setPlaceholderText("🔍  Filter cards by summary or key…")
        self._filter_edit.setMaximumWidth(260)
        self._filter_edit.textChanged.connect(self._apply_filters)
        fb.addWidget(self._filter_edit)

        fb.addWidget(QLabel("Assignee:"))
        self._assignee_combo = QComboBox()
        self._assignee_combo.setMinimumWidth(140)
        self._assignee_combo.addItem("All", None)
        self._assignee_combo.currentIndexChanged.connect(self._apply_filters)
        fb.addWidget(self._assignee_combo)

        fb.addWidget(QLabel("Priority:"))
        self._priority_combo = QComboBox()
        self._priority_combo.setMinimumWidth(110)
        self._priority_combo.addItem("All", None)
        for p in ["Highest", "High", "Medium", "Low", "Lowest"]:
            self._priority_combo.addItem(p, p)
        self._priority_combo.currentIndexChanged.connect(self._apply_filters)
        fb.addWidget(self._priority_combo)

        self._clear_btn = QPushButton("✕  Clear")
        self._clear_btn.setObjectName("toolbar_btn")
        self._clear_btn.setFixedHeight(26)
        self._clear_btn.clicked.connect(self._clear_filters)
        fb.addWidget(self._clear_btn)
        fb.addStretch()

        self._filter_count_lbl = QLabel("")
        self._filter_count_lbl.setObjectName("dim")
        fb.addWidget(self._filter_count_lbl)

        layout.addWidget(filter_bar)

        # ── Columns row ───────────────────────────────────────────────────────
        cols_widget = QWidget()
        cols_layout = QHBoxLayout(cols_widget)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(10)

        for status in KANBAN_STATUSES:
            col = KanbanColumn(status)
            col.card_dropped.connect(self._on_card_dropped)
            self._columns[status] = col
            cols_layout.addWidget(col, 1)

        scroll = QScrollArea()
        scroll.setWidget(cols_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        layout.addWidget(scroll, 1)

    # ── Public API ────────────────────────────────────────────────────────────
    def sync_combos(self, project_combo: QComboBox, board_combo: QComboBox,
                    sprint_combo: QComboBox):
        """Mirror the Stories-tab project/board/sprint combos into the Kanban toolbar."""
        self._kb_project_combo.blockSignals(True)
        self._kb_board_combo.blockSignals(True)
        self._kb_sprint_combo.blockSignals(True)

        # Project
        self._kb_project_combo.clear()
        for i in range(project_combo.count()):
            self._kb_project_combo.addItem(project_combo.itemText(i),
                                           project_combo.itemData(i))
        self._kb_project_combo.setCurrentIndex(project_combo.currentIndex())
        self._kb_project_combo.setEnabled(project_combo.count() > 0)

        # Board
        self._kb_board_combo.clear()
        for i in range(board_combo.count()):
            self._kb_board_combo.addItem(board_combo.itemText(i),
                                         board_combo.itemData(i))
        self._kb_board_combo.setCurrentIndex(board_combo.currentIndex())
        self._kb_board_combo.setEnabled(board_combo.count() > 0)

        # Sprint
        self._kb_sprint_combo.clear()
        for i in range(sprint_combo.count()):
            self._kb_sprint_combo.addItem(sprint_combo.itemText(i),
                                          sprint_combo.itemData(i))
        self._kb_sprint_combo.setCurrentIndex(sprint_combo.currentIndex())
        self._kb_sprint_combo.setEnabled(sprint_combo.count() > 0)
        self._kb_load_btn.setEnabled(sprint_combo.count() > 0)

        self._kb_project_combo.blockSignals(False)
        self._kb_board_combo.blockSignals(False)
        self._kb_sprint_combo.blockSignals(False)

    def _on_kb_load_clicked(self):
        """Sync selected values back to Stories combos then request a load."""
        self.load_requested.emit()

    def set_sprint_name(self, name: str):
        """Update the board title to reflect the active sprint name."""
        self._title_lbl.setText(f"◈  {name.upper()}" if name else "◈  ACTIVE SPRINT")

    def set_base_url(self, url: str):
        self._base_url = url

    def populate(self, issues: list, sp_field: str, force: bool = False):
        """Populate board. Skips re-render if issues unchanged and force=False."""
        if not force and issues is self._last_issues and sp_field == self._sp_field:
            return
        self._last_issues = issues
        self._all_issues  = issues
        self._sp_field    = sp_field
        # Hide load bar once stories are present; show it when board is empty
        self._load_bar.setVisible(not bool(issues))
        self._rebuild_assignee_combo(issues)
        self._render_issues(issues)

    def clear(self):
        """Clear all cards and show the load toolbar."""
        self._last_issues = []
        self._all_issues  = []
        for col in self._columns.values():
            col.clear_cards()
        self._status_lbl.setText("No stories loaded")
        self._load_bar.setVisible(True)

    def refresh(self, issues: list, sp_field: str):
        """Force re-render (used after a transition)."""
        self.populate(issues, sp_field, force=True)

    # ── Filter logic ──────────────────────────────────────────────────────────
    def _rebuild_assignee_combo(self, issues: list):
        self._assignee_combo.blockSignals(True)
        current = self._assignee_combo.currentData()
        self._assignee_combo.clear()
        self._assignee_combo.addItem("All", None)
        seen = {}
        for iss in issues:
            aobj = (iss.get("fields") or {}).get("assignee") or {}
            name = aobj.get("displayName") or aobj.get("name") or ""
            uid  = aobj.get("accountId") or aobj.get("name") or ""
            if uid and uid not in seen:
                seen[uid] = name
                self._assignee_combo.addItem(name or uid, uid)
        # Restore previous selection if still present
        for i in range(self._assignee_combo.count()):
            if self._assignee_combo.itemData(i) == current:
                self._assignee_combo.setCurrentIndex(i)
                break
        self._assignee_combo.blockSignals(False)

    def _apply_filters(self):
        term     = self._filter_edit.text().lower().strip()
        assignee = self._assignee_combo.currentData()
        priority = self._priority_combo.currentData()

        filtered = []
        for iss in self._all_issues:
            f = iss.get("fields") or {}
            if term:
                key     = iss.get("key", "").lower()
                summary = f.get("summary", "").lower()
                if term not in key and term not in summary:
                    continue
            if assignee:
                aobj = f.get("assignee") or {}
                uid  = aobj.get("accountId") or aobj.get("name") or ""
                if uid != assignee:
                    continue
            if priority:
                pri = (f.get("priority") or {}).get("name", "")
                if pri != priority:
                    continue
            filtered.append(iss)

        self._render_issues(filtered)
        total    = len(self._all_issues)
        showing  = len(filtered)
        is_filtered = term or assignee or priority
        self._filter_count_lbl.setText(
            f"Showing {showing} of {total}" if is_filtered else ""
        )

    def _clear_filters(self):
        self._filter_edit.blockSignals(True)
        self._assignee_combo.blockSignals(True)
        self._priority_combo.blockSignals(True)
        self._filter_edit.clear()
        self._assignee_combo.setCurrentIndex(0)
        self._priority_combo.setCurrentIndex(0)
        self._filter_edit.blockSignals(False)
        self._assignee_combo.blockSignals(False)
        self._priority_combo.blockSignals(False)
        self._render_issues(self._all_issues)
        self._filter_count_lbl.setText("")

    def _render_issues(self, issues: list):
        for col in self._columns.values():
            col.clear_cards()

        ungrouped = 0
        for issue in issues:
            status = (issue.get("fields", {}).get("status") or {}).get("name", "")
            col    = self._columns.get(status)
            if col is None:
                col = self._columns.get("To Do")
                ungrouped += 1
            if col:
                card = KanbanCard(issue, self._sp_field)
                card.clicked.connect(self._on_card_clicked)
                col.add_card(card)

        total = len(self._all_issues)
        self._status_lbl.setText(
            f"{total} stories"
            + (f" ({ungrouped} in unknown status → To Do)" if ungrouped else "")
        )

    def _on_card_clicked(self, key: str):
        self.story_selected.emit(key)

    def _on_card_dropped(self, key: str, new_status: str):
        self.transition_requested.emit(key, new_status)


# ── Backlog View ───────────────────────────────────────────────────────────────
class BacklogWidget(QWidget):
    """Shows stories not assigned to any sprint (backlog items)."""
    story_selected   = pyqtSignal(str)
    move_to_sprint   = pyqtSignal(str, int)   # (issue_key, sprint_id)
    load_requested   = pyqtSignal()            # ask MainWindow to load backlog

    def __init__(self, parent=None):
        super().__init__(parent)
        self._issues: list = []
        self._sp_field     = ""
        self._sprints: list = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Load bar (project / board selector) ───────────────────────────────
        self._load_bar = QFrame()
        self._load_bar.setStyleSheet(
            f"QFrame {{ background: {PANEL_BG}; border-bottom: 1px solid {BORDER}; }}"
        )
        lb = QHBoxLayout(self._load_bar)
        lb.setContentsMargins(16, 8, 16, 8)
        lb.setSpacing(8)

        lb.addWidget(QLabel("PROJECT"))
        self._bl_project_combo = QComboBox()
        self._bl_project_combo.setMinimumWidth(160)
        self._bl_project_combo.setEnabled(False)
        lb.addWidget(self._bl_project_combo)

        lb.addWidget(QLabel("BOARD"))
        self._bl_board_combo = QComboBox()
        self._bl_board_combo.setMinimumWidth(160)
        self._bl_board_combo.setEnabled(False)
        lb.addWidget(self._bl_board_combo)

        self._bl_load_btn = QPushButton("↺  Load Backlog")
        self._bl_load_btn.setObjectName("toolbar_btn")
        self._bl_load_btn.setEnabled(False)
        self._bl_load_btn.clicked.connect(self.load_requested.emit)
        lb.addWidget(self._bl_load_btn)
        lb.addStretch()

        self._bl_hint = QLabel("Select a project and board, then click Load Backlog.")
        self._bl_hint.setObjectName("dim")
        lb.addWidget(self._bl_hint)
        layout.addWidget(self._load_bar)

        # ── Main content ──────────────────────────────────────────────────────
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 12, 16, 16)
        content_layout.setSpacing(8)

        hdr = QHBoxLayout()
        title = QLabel("◈  BACKLOG")
        title.setObjectName("heading")
        hdr.addWidget(title)
        hdr.addStretch()
        self._count_lbl = QLabel("")
        self._count_lbl.setObjectName("dim")
        hdr.addWidget(self._count_lbl)
        content_layout.addLayout(hdr)

        # Filter + move-to-sprint bar
        fb = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter backlog…")
        self._search.setMaximumWidth(260)
        self._search.textChanged.connect(self._filter)
        fb.addWidget(self._search)
        fb.addStretch()
        fb.addWidget(QLabel("Move selected to sprint:"))
        self._sprint_combo = QComboBox()
        self._sprint_combo.setMinimumWidth(200)
        self._sprint_combo.addItem("— select sprint —", None)
        fb.addWidget(self._sprint_combo)
        self._move_btn = QPushButton("⇧  Move")
        self._move_btn.setObjectName("toolbar_btn")
        self._move_btn.setEnabled(False)
        self._move_btn.clicked.connect(self._on_move_clicked)
        fb.addWidget(self._move_btn)
        fb.addSpacing(12)
        self._export_btn = QPushButton("⬇  Export CSV")
        self._export_btn.setObjectName("toolbar_btn")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._export_csv)
        fb.addWidget(self._export_btn)
        content_layout.addLayout(fb)

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["KEY", "SUMMARY", "ASSIGNEE", "PRIORITY", "PTS", "TYPE", "DUE DATE"]
        )
        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSortingEnabled(True)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        content_layout.addWidget(self._table, 1)
        layout.addWidget(content, 1)
        self._base_url = ""

    def sync_combos(self, project_combo: QComboBox, board_combo: QComboBox):
        """Mirror the Stories-tab project/board combos into the Backlog load bar."""
        self._bl_project_combo.blockSignals(True)
        self._bl_board_combo.blockSignals(True)

        self._bl_project_combo.clear()
        for i in range(project_combo.count()):
            self._bl_project_combo.addItem(project_combo.itemText(i),
                                           project_combo.itemData(i))
        self._bl_project_combo.setCurrentIndex(project_combo.currentIndex())
        self._bl_project_combo.setEnabled(project_combo.count() > 0)

        self._bl_board_combo.clear()
        for i in range(board_combo.count()):
            self._bl_board_combo.addItem(board_combo.itemText(i),
                                         board_combo.itemData(i))
        self._bl_board_combo.setCurrentIndex(board_combo.currentIndex())
        self._bl_board_combo.setEnabled(board_combo.count() > 0)
        self._bl_load_btn.setEnabled(board_combo.count() > 0)

        self._bl_project_combo.blockSignals(False)
        self._bl_board_combo.blockSignals(False)

    def set_base_url(self, url: str):
        self._base_url = url

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        key_item = self._table.item(row, 0)
        if not key_item:
            return
        key = key_item.text()

        selected_rows = list({idx.row() for idx in self._table.selectedIndexes()})
        selected_keys = [
            self._table.item(r, 0).text()
            for r in selected_rows
            if self._table.item(r, 0)
        ]
        if not selected_keys:
            selected_keys = [key]

        menu = QMenu(self)
        open_action = menu.addAction("⎋  Open in Jira")
        open_action.setEnabled(bool(self._base_url) and len(selected_keys) == 1)
        menu.addSeparator()
        copy_key = menu.addAction(
            "⎘  Copy Key" if len(selected_keys) == 1
            else f"⎘  Copy {len(selected_keys)} Keys"
        )
        menu.addSeparator()
        move_action = menu.addAction(
            "⇧  Move to Sprint" if len(selected_keys) == 1
            else f"⇧  Move {len(selected_keys)} Stories to Sprint"
        )
        move_action.setEnabled(self._sprint_combo.currentData() is not None)

        chosen = menu.exec(self._table.viewport().mapToGlobal(pos))
        if chosen == open_action:
            webbrowser.open(f"{self._base_url}/browse/{key}")
        elif chosen == copy_key:
            QApplication.clipboard().setText(", ".join(selected_keys))
        elif chosen == move_action:
            sprint_id = self._sprint_combo.currentData()
            if sprint_id:
                for k in selected_keys:
                    self.move_to_sprint.emit(k, sprint_id)

    def set_sprints(self, sprints: list):
        """Update the sprint combo for move-to-sprint."""
        self._sprints = sprints
        self._sprint_combo.blockSignals(True)
        self._sprint_combo.clear()
        self._sprint_combo.addItem("— select sprint —", None)
        for s in sprints:
            state = s.get("state", "")
            self._sprint_combo.addItem(f"[{state.upper()}] {s['name']}", s["id"])
            if state.lower() == "active":
                self._sprint_combo.setCurrentIndex(self._sprint_combo.count() - 1)
        self._sprint_combo.blockSignals(False)

    def populate(self, issues: list, sp_field: str):
        self._issues   = issues
        self._sp_field = sp_field
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        for iss in issues:
            f       = iss.get("fields", {})
            key     = iss.get("key", "")
            summary = f.get("summary", "")
            aobj    = f.get("assignee") or {}
            assignee = aobj.get("displayName") or aobj.get("name") or "—"
            priority = (f.get("priority") or {}).get("name", "—")
            itype    = (f.get("issuetype") or {}).get("name", "—")
            due      = (f.get("duedate") or "")[:10] or "—"
            pts_raw  = next(
                (f.get(k) for k in ([sp_field] + JiraClient._SP_FALLBACKS)
                 if f.get(k) is not None), None
            )
            try:
                pts = str(int(float(pts_raw))) if pts_raw is not None else "—"
            except (TypeError, ValueError):
                pts = "—"

            row = self._table.rowCount()
            self._table.insertRow(row)
            k_item = QTableWidgetItem(key)
            k_item.setForeground(QColor(ACCENT_CYAN))
            self._table.setItem(row, 0, k_item)
            self._table.setItem(row, 1, QTableWidgetItem(summary))
            a_item = QTableWidgetItem(assignee)
            a_item.setForeground(QColor(TEXT_SEC))
            self._table.setItem(row, 2, a_item)
            self._table.setItem(row, 3, QTableWidgetItem(priority))
            pts_item = QTableWidgetItem(pts)
            pts_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 4, pts_item)
            self._table.setItem(row, 5, QTableWidgetItem(itype))
            due_item = QTableWidgetItem(due)
            due_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 6, due_item)
            self._table.setRowHeight(row, 38)

        self._table.setSortingEnabled(True)
        self._count_lbl.setText(f"{len(issues)} backlog items")
        self._export_btn.setEnabled(bool(issues))

    def _filter(self, text: str):
        term = text.lower()
        for row in range(self._table.rowCount()):
            match = not term or any(
                term in (self._table.item(row, c).text().lower()
                         if self._table.item(row, c) else "")
                for c in range(self._table.columnCount())
            )
            self._table.setRowHidden(row, not match)

    def _on_selection_changed(self):
        has_sel  = bool(self._table.selectedItems())
        has_sprint = self._sprint_combo.currentData() is not None
        self._move_btn.setEnabled(has_sel and has_sprint)

        rows = list({idx.row() for idx in self._table.selectedIndexes()})
        if len(rows) == 1:
            item = self._table.item(rows[0], 0)
            if item:
                self.story_selected.emit(item.text())

    def _on_move_clicked(self):
        sprint_id = self._sprint_combo.currentData()
        if sprint_id is None:
            return
        rows = list({idx.row() for idx in self._table.selectedIndexes()})
        keys = []
        for r in rows:
            it = self._table.item(r, 0)
            if it:
                keys.append(it.text())
        if not keys:
            return
        sprint_name = self._sprint_combo.currentText()
        reply = QMessageBox.question(
            self, "Move to Sprint",
            f"Move {len(keys)} stor{'ies' if len(keys) != 1 else 'y'} to:\n{sprint_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for key in keys:
            self.move_to_sprint.emit(key, sprint_id)

    def _export_csv(self):
        if not self._issues:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Backlog", "backlog.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["key", "summary", "assignee", "priority",
                             "story_points", "issue_type", "due_date"])
                for iss in self._issues:
                    fld     = iss.get("fields", {})
                    aobj    = fld.get("assignee") or {}
                    pts_raw = next(
                        (fld.get(k) for k in ([self._sp_field] + JiraClient._SP_FALLBACKS)
                         if fld.get(k) is not None), None
                    )
                    try:
                        pts = str(int(float(pts_raw))) if pts_raw is not None else ""
                    except (TypeError, ValueError):
                        pts = ""
                    w.writerow([
                        iss.get("key", ""),
                        fld.get("summary", ""),
                        aobj.get("displayName") or aobj.get("name") or "",
                        (fld.get("priority") or {}).get("name", ""),
                        pts,
                        (fld.get("issuetype") or {}).get("name", ""),
                        (fld.get("duedate") or "")[:10],
                    ])
            QMessageBox.information(self, "Exported", f"Backlog exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))


# ── Main window ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SprintMate")
        self.setMinimumSize(1200, 760)
        self.setStyleSheet(STYLESHEET)

        self._settings = {}
        self._client: JiraClient | None = None
        self._boards = []
        self._sprints = []
        self._issues = []
        self._workers = []
        self._users_cache: list = []
        self._reselect_key: str | None = None
        self._sp_field = JiraClient._FIELD_MAP[JiraClient.MODE_SECONDARY]["story_point"]
        self._fl_field = "customfield_10100"
        self._column_prefs: dict[str, set] = {}   # board_id -> set of visible col indices
        self._recent_keys: list[str] = []          # MRU list of viewed issue keys
        self._unsaved_row: int | None = None       # row with pending edits
        self._reports_html_map: dict[int, str] = {}  # reports sub-tab index -> html

        self._build_ui()
        self._settings = self._load_settings()
        self._status("Ready — configure connection to get started.")

        mode = self._settings.get("mode", JiraClient.MODE_SECONDARY)
        url   = self._settings.get("secondary_url") if mode == JiraClient.MODE_SECONDARY else self._settings.get("primary_url")
        token = self._settings.get("secondary_token") if mode == JiraClient.MODE_SECONDARY else self._settings.get("primary_token")
        if url and token:
            self._settings["url"]   = url
            self._settings["token"] = token
            self._client = JiraClient(url, token, mode)
            self.edit_panel._sp_field = self._client.story_point_field_id
            self.edit_panel._fl_field = self._client.feature_link_field_id
            self.edit_panel._base_url = self._client.base_url
            mode_label = self._instance_label(mode)
            self.mode_indicator.setText(f"◈  {mode_label}")
            self.refresh_btn.setEnabled(True)
            self.switch_instance_btn.setEnabled(True)
            self._load_projects()

        self._check_token_expiry()

        # Periodic token expiry check every 4 hours
        self._expiry_timer = QTimer(self)
        self._expiry_timer.setInterval(4 * 60 * 60 * 1000)
        self._expiry_timer.timeout.connect(self._check_token_expiry)
        self._expiry_timer.start()

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(56)
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("◈  SPRINTMATE")
        logo.setObjectName("heading")
        logo.setStyleSheet(f"font-size: 14px; color: {ACCENT_CYAN}; letter-spacing: 3px;")
        tb_layout.addWidget(logo)
        tb_layout.addStretch()

        self.mode_indicator = QLabel("")
        self.mode_indicator.setStyleSheet(
            f"color: {ACCENT_BLUE}; font-size: 11px; letter-spacing: 2px; padding: 0 12px;"
        )
        tb_layout.addWidget(self.mode_indicator)

        self.switch_instance_btn = QPushButton("⇄  Switch Instance")
        self.switch_instance_btn.setObjectName("toolbar_btn")
        self.switch_instance_btn.setEnabled(False)
        self.switch_instance_btn.setToolTip("Switch between Primary and Secondary without opening settings")
        self.switch_instance_btn.clicked.connect(self._switch_instance)
        tb_layout.addWidget(self.switch_instance_btn)

        tb_layout.addSpacing(16)
        self._tab_stories_btn = QPushButton("◈  Stories")
        self._tab_stories_btn.setObjectName("toolbar_btn")
        self._tab_stories_btn.setToolTip("Stories list view  (Alt+1)")
        self._tab_stories_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        tb_layout.addWidget(self._tab_stories_btn)
        self._tab_kanban_btn = QPushButton("⊞  Active Sprint")
        self._tab_kanban_btn.setObjectName("toolbar_btn")
        self._tab_kanban_btn.setToolTip("Active sprint board view  (Alt+2)")
        self._tab_kanban_btn.clicked.connect(lambda: self._switch_to_kanban())
        tb_layout.addWidget(self._tab_kanban_btn)
        self._tab_backlog_btn = QPushButton("☰  Backlog")
        self._tab_backlog_btn.setObjectName("toolbar_btn")
        self._tab_backlog_btn.setToolTip("Backlog view  (Alt+3)")
        self._tab_backlog_btn.clicked.connect(self._switch_to_backlog)
        tb_layout.addWidget(self._tab_backlog_btn)
        self._tab_reports_btn = QPushButton("📊  Reports")
        self._tab_reports_btn.setObjectName("toolbar_btn")
        self._tab_reports_btn.setToolTip("Reports  (Alt+4)")
        self._tab_reports_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(3))
        tb_layout.addWidget(self._tab_reports_btn)

        self.refresh_btn = QPushButton("↺  Refresh")
        self.refresh_btn.setObjectName("toolbar_btn")
        self.refresh_btn.clicked.connect(self._load_sprint_issues)
        self.refresh_btn.setEnabled(False)
        tb_layout.addWidget(self.refresh_btn)

        root.addWidget(topbar)

        # ── Help menu ────────────────────────────────────────────────────
        _help_menu = self.menuBar().addMenu("Menu")
        _cfg_act = QAction("⚙  Configure…", self)
        _cfg_act.triggered.connect(self._open_settings)
        _help_menu.addAction(_cfg_act)
        _help_menu.addSeparator()
        _shortcuts_act = QAction("Keyboard Shortcuts…", self)
        _shortcuts_act.triggered.connect(self._show_shortcut_dialog)
        _help_menu.addAction(_shortcuts_act)
        _help_menu.addSeparator()
        _upd_act = QAction("Check for Updates…", self)
        _upd_act.triggered.connect(self._check_for_updates)
        _help_menu.addAction(_upd_act)
        _help_menu.addSeparator()
        _about_act = QAction("About SprintMate", self)
        _about_act.triggered.connect(self._show_about)
        _help_menu.addAction(_about_act)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(4)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: {DARK_BG}; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT_BLUE}; }}
        """)
        root.addWidget(self.progress)

        self.expiry_banner = QFrame()
        self.expiry_banner.setVisible(False)
        self.expiry_banner.setStyleSheet(f"background: #5A3E00; border-bottom: 1px solid {ACCENT_ORANGE};")
        _bl = QHBoxLayout(self.expiry_banner)
        _bl.setContentsMargins(20, 6, 12, 6)
        self.expiry_banner_lbl = QLabel("")
        self.expiry_banner_lbl.setStyleSheet(f"color: {ACCENT_ORANGE}; font-size: 12px;")
        _bl.addWidget(self.expiry_banner_lbl, 1)
        _db = QPushButton("✕")
        _db.setFixedSize(20, 20); _db.setObjectName("dim")
        _db.clicked.connect(lambda: self.expiry_banner.setVisible(False))
        _bl.addWidget(_db)
        root.addWidget(self.expiry_banner)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setVisible(False)
        root.addWidget(self.tabs, 1)

        stories_tab = QWidget()
        stories_layout = QVBoxLayout(stories_tab)
        stories_layout.setContentsMargins(0, 0, 0, 0)
        stories_layout.setSpacing(0)

        # ── Filter bar: row 1 (selection) + row 2 (actions + filters) ──────
        filterbar = QFrame()
        filterbar.setStyleSheet(f"background-color: {PANEL_BG}; border-bottom: 1px solid {BORDER};")
        fb_outer = QVBoxLayout(filterbar)
        fb_outer.setContentsMargins(20, 6, 20, 6)
        fb_outer.setSpacing(4)

        # Row 1 — board/sprint selection
        fb_row1 = QHBoxLayout()
        fb_row1.setSpacing(10)
        fb_row1.addWidget(QLabel("PROJECT"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(160)
        self.project_combo.setEnabled(False)
        self.project_combo.currentIndexChanged.connect(self._on_project_changed)
        fb_row1.addWidget(self.project_combo)
        fb_row1.addWidget(QLabel("BOARD"))
        self.board_combo = QComboBox()
        self.board_combo.setMinimumWidth(140)
        self.board_combo.setEnabled(False)
        self.board_combo.currentIndexChanged.connect(self._on_board_changed)
        fb_row1.addWidget(self.board_combo)
        fb_row1.addWidget(QLabel("SPRINT"))
        self.sprint_combo = QComboBox()
        self.sprint_combo.setMinimumWidth(200)
        self.sprint_combo.setEnabled(False)
        fb_row1.addWidget(self.sprint_combo)
        self.load_btn = QPushButton("Load Stories")
        self.load_btn.setObjectName("toolbar_btn")
        self.load_btn.clicked.connect(self._load_sprint_issues)
        self.load_btn.setEnabled(False)
        fb_row1.addWidget(self.load_btn)
        fb_row1.addSpacing(12)
        self.sprint_mgr_btn = QPushButton("⊕  Sprint")
        self.sprint_mgr_btn.setObjectName("toolbar_btn")
        self.sprint_mgr_btn.setToolTip("Create, start, rename, or close sprints")
        self.sprint_mgr_btn.setEnabled(False)
        self.sprint_mgr_btn.clicked.connect(self._open_sprint_manager)
        fb_row1.addWidget(self.sprint_mgr_btn)
        fb_row1.addStretch()
        fb_outer.addLayout(fb_row1)

        # Row 2 — action buttons + filters
        fb_row2 = QHBoxLayout()
        fb_row2.setSpacing(6)
        self.new_story_btn = QPushButton("＋  New Story")
        self.new_story_btn.setObjectName("toolbar_btn")
        self.new_story_btn.clicked.connect(self._open_new_story)
        self.new_story_btn.setEnabled(False)
        fb_row2.addWidget(self.new_story_btn)
        self.bulk_create_btn = QPushButton("＋＋  Bulk Create")
        self.bulk_create_btn.setObjectName("toolbar_btn")
        self.bulk_create_btn.setToolTip("Create multiple stories from a CSV file")
        self.bulk_create_btn.clicked.connect(self._open_bulk_create)
        self.bulk_create_btn.setEnabled(False)
        fb_row2.addWidget(self.bulk_create_btn)
        self.import_btn = QPushButton("📄  Import")
        self.import_btn.setObjectName("toolbar_btn")
        self.import_btn.clicked.connect(self._import_comments)
        self.import_btn.setEnabled(False)
        fb_row2.addWidget(self.import_btn)
        self.export_btn = QPushButton("⬇  Export")
        self.export_btn.setObjectName("toolbar_btn")
        self.export_btn.clicked.connect(self._export_stories)
        self.export_btn.setEnabled(False)
        fb_row2.addWidget(self.export_btn)
        self.report_btn    = None   # moved to Reports tab
        self.velocity_btn  = None   # moved to Reports tab
        self.archive_btn = QPushButton("🗄  Archive")
        self.archive_btn.setObjectName("toolbar_btn")
        self.archive_btn.setToolTip("Archive selected story or choose stories to archive")
        self.archive_btn.clicked.connect(self._open_archive)
        self.archive_btn.setEnabled(False)
        fb_row2.addWidget(self.archive_btn)
        self.bulk_edit_btn = QPushButton("✎  Bulk Edit")
        self.bulk_edit_btn.setObjectName("toolbar_btn")
        self.bulk_edit_btn.setToolTip("Edit assignee, priority, or story points for multiple stories")
        self.bulk_edit_btn.clicked.connect(self._open_bulk_edit)
        self.bulk_edit_btn.setEnabled(False)
        fb_row2.addWidget(self.bulk_edit_btn)
        fb_row2.addStretch()
        fb_row2.addWidget(QLabel("ASSIGNEE"))
        self.assignee_filter_combo = QComboBox()
        self.assignee_filter_combo.setMinimumWidth(130)
        self.assignee_filter_combo.setEnabled(False)
        self.assignee_filter_combo.setToolTip("Filter stories by assignee")
        self.assignee_filter_combo.currentIndexChanged.connect(self._apply_assignee_filter)
        fb_row2.addWidget(self.assignee_filter_combo)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter stories…")
        self.search_edit.setMinimumWidth(180)
        self.search_edit.textChanged.connect(self._filter_table)
        fb_row2.addWidget(self.search_edit)
        fb_outer.addLayout(fb_row2)

        stories_layout.addWidget(filterbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 8, 16)
        left_layout.setSpacing(8)

        count_row = QHBoxLayout()
        self.story_count_lbl = QLabel("No stories loaded")
        self.story_count_lbl.setObjectName("dim")
        count_row.addWidget(self.story_count_lbl)
        count_row.addStretch()
        self.velocity_lbl = QLabel("")
        self.velocity_lbl.setObjectName("dim")
        self.velocity_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_row.addWidget(self.velocity_lbl)
        count_row.addStretch()
        # ── Persistent sprint label ───────────────────────────────────────────
        self.sprint_lbl = QLabel("")
        self.sprint_lbl.setObjectName("dim")
        self.sprint_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        count_row.addWidget(self.sprint_lbl)
        left_layout.addLayout(count_row)

        # ── Sprint progress bar ───────────────────────────────────────────────
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(4)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {BORDER};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: {ACCENT_GREEN};
                border-radius: 2px;
            }}
        """)
        left_layout.addWidget(self._progress_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "KEY", "SUMMARY", "ASSIGNEE", "STATUS", "DUE DATE",
            "PTS", "PRIORITY", "TYPE", "FEATURE LINK"
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(COL_KEY,         QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(COL_SUMMARY,     QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(COL_ASSIGNEE,    QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(COL_STATUS,      QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(COL_DUE_DATE,    QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(COL_STORY_PTS,   QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(COL_PRIORITY,    QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(COL_ISSUE_TYPE,  QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(COL_FEATURE_LNK, QHeaderView.ResizeMode.ResizeToContents)
        hh.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        hh.customContextMenuRequested.connect(self._show_column_menu)
        self.table.setSortingEnabled(True)
        hh.setSortIndicatorShown(True)
        hh.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.itemSelectionChanged.connect(self._on_story_selected)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        # ── Row right-click context menu ──────────────────────────────────────
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_row_context_menu)
        self._apply_default_columns()
        left_layout.addWidget(self.table)

        quick_bar = QFrame()
        quick_bar.setStyleSheet(f"background: {PANEL_BG}; border-top: 1px solid {BORDER};")
        _qbl = QHBoxLayout(quick_bar)
        _qbl.setContentsMargins(8, 4, 8, 4)
        self.quick_add_edit = QLineEdit()
        self.quick_add_edit.setPlaceholderText("＋ Quick-add story summary… (Enter to create)")
        self.quick_add_edit.setEnabled(False)
        self.quick_add_edit.returnPressed.connect(self._quick_add_story)
        _qbl.addWidget(self.quick_add_edit, 1)
        self.quick_add_type_combo = QComboBox()
        self.quick_add_type_combo.setMinimumWidth(110)
        self.quick_add_type_combo.setMaximumWidth(140)
        self.quick_add_type_combo.setEnabled(False)
        self.quick_add_type_combo.setToolTip("Issue type for quick-add")
        _qbl.addWidget(self.quick_add_type_combo)
        # Rank buttons
        self._rank_up_btn = QPushButton("↑ Rank Up")
        self._rank_up_btn.setObjectName("toolbar_btn")
        self._rank_up_btn.setFixedHeight(28)
        self._rank_up_btn.setToolTip("Move selected story up one position in the sprint ranking")
        self._rank_up_btn.setEnabled(False)
        self._rank_up_btn.clicked.connect(lambda: self._rank_selected(-1))
        _qbl.addWidget(self._rank_up_btn)
        self._rank_down_btn = QPushButton("↓ Rank Down")
        self._rank_down_btn.setObjectName("toolbar_btn")
        self._rank_down_btn.setFixedHeight(28)
        self._rank_down_btn.setToolTip("Move selected story down one position in the sprint ranking")
        self._rank_down_btn.setEnabled(False)
        self._rank_down_btn.clicked.connect(lambda: self._rank_selected(1))
        _qbl.addWidget(self._rank_down_btn)
        self._recent_btn = QPushButton("🕐")
        self._recent_btn.setObjectName("toolbar_btn")
        self._recent_btn.setFixedHeight(28)
        self._recent_btn.setFixedWidth(32)
        self._recent_btn.setToolTip("Recently viewed stories")
        self._recent_btn.clicked.connect(self._show_recent_menu)
        _qbl.addWidget(self._recent_btn)
        left_layout.addWidget(quick_bar)

        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 16, 16, 16)
        self.edit_panel = StoryEditPanel()
        self.edit_panel.saved.connect(self._on_save_story)
        self.edit_panel.changed.connect(self._mark_unsaved_row)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.edit_panel)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: transparent; }}")
        right_layout.addWidget(scroll)
        splitter.addWidget(right)

        splitter.setSizes([680, 480])
        stories_layout.addWidget(splitter, 1)
        self.tabs.addTab(stories_tab, "◈  STORIES")

        # ── Kanban tab ────────────────────────────────────────────────────────
        self.kanban_widget = KanbanBoardWidget()
        self.kanban_widget.story_selected.connect(self._on_kanban_story_selected)
        self.kanban_widget.transition_requested.connect(self._on_kanban_transition)
        self.kanban_widget.new_story_requested.connect(
            lambda: self.new_story_btn.click() if self.new_story_btn.isEnabled() else None
        )
        self.kanban_widget.load_requested.connect(self._on_kanban_load_requested)
        self.tabs.addTab(self.kanban_widget, "⊞  ACTIVE SPRINT")

        # ── Backlog tab ───────────────────────────────────────────────────────
        backlog_outer = QWidget()
        backlog_outer_layout = QVBoxLayout(backlog_outer)
        backlog_outer_layout.setContentsMargins(0, 0, 0, 0)
        backlog_outer_layout.setSpacing(0)

        self.backlog_widget = BacklogWidget()
        self.backlog_widget.story_selected.connect(self._on_backlog_story_selected)
        self.backlog_widget.move_to_sprint.connect(self._on_backlog_move_to_sprint)
        self.backlog_widget.load_requested.connect(self._on_backlog_load_requested)
        backlog_outer_layout.addWidget(self.backlog_widget, 1)
        self.tabs.addTab(backlog_outer, "☰  BACKLOG")

        # ── Reports tab ───────────────────────────────────────────────────────
        reports_outer = QWidget()
        reports_outer_layout = QVBoxLayout(reports_outer)
        reports_outer_layout.setContentsMargins(0, 0, 0, 0)
        reports_outer_layout.setSpacing(0)

        # ── Reports toolbar ───────────────────────────────────────────────────
        reports_tb = QFrame()
        reports_tb.setStyleSheet(f"background: {PANEL_BG}; border-bottom: 1px solid {BORDER};")
        rtb = QHBoxLayout(reports_tb)
        rtb.setContentsMargins(16, 6, 16, 6)
        rtb.setSpacing(8)

        rtb.addWidget(QLabel("SPRINT"))
        self._rpt_sprint_combo = QComboBox()
        self._rpt_sprint_combo.setMinimumWidth(200)
        self._rpt_sprint_combo.setEnabled(False)
        rtb.addWidget(self._rpt_sprint_combo)

        self._rpt_gen_btn = QPushButton("📊  Sprint Report")
        self._rpt_gen_btn.setObjectName("toolbar_btn")
        self._rpt_gen_btn.setEnabled(False)
        self._rpt_gen_btn.clicked.connect(self._reports_generate_sprint)
        rtb.addWidget(self._rpt_gen_btn)

        self._rpt_people_btn = QPushButton("👤  People Report")
        self._rpt_people_btn.setObjectName("toolbar_btn")
        self._rpt_people_btn.setEnabled(False)
        self._rpt_people_btn.clicked.connect(self._reports_generate_people)
        rtb.addWidget(self._rpt_people_btn)

        self._rpt_velocity_btn = QPushButton("📈  Velocity")
        self._rpt_velocity_btn.setObjectName("toolbar_btn")
        self._rpt_velocity_btn.setEnabled(False)
        self._rpt_velocity_btn.clicked.connect(self._reports_generate_velocity)
        rtb.addWidget(self._rpt_velocity_btn)

        self._rpt_burndown_btn = QPushButton("📉  Burndown")
        self._rpt_burndown_btn.setObjectName("toolbar_btn")
        self._rpt_burndown_btn.setEnabled(False)
        self._rpt_burndown_btn.clicked.connect(self._reports_generate_burndown)
        rtb.addWidget(self._rpt_burndown_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {BORDER};")
        rtb.addWidget(sep)

        rtb.addWidget(QLabel("COMPARE"))
        self.compare_combo = QComboBox()
        self.compare_combo.setMinimumWidth(180)
        self.compare_combo.setEnabled(False)
        self.compare_combo.setToolTip("Select a sprint to compare against the loaded sprint")
        rtb.addWidget(self.compare_combo)
        self.compare_btn = QPushButton("⇆  Compare")
        self.compare_btn.setObjectName("toolbar_btn")
        self.compare_btn.setEnabled(False)
        self.compare_btn.clicked.connect(self._compare_sprints)
        rtb.addWidget(self.compare_btn)

        rtb.addStretch()
        self._rpt_save_btn = QPushButton("⬇  Save HTML")
        self._rpt_save_btn.setObjectName("toolbar_btn")
        self._rpt_save_btn.setEnabled(False)
        self._rpt_save_btn.clicked.connect(self._reports_save_html)
        rtb.addWidget(self._rpt_save_btn)
        reports_outer_layout.addWidget(reports_tb)

        # ── Reports sub-tabs ──────────────────────────────────────────────────
        self._reports_tabs = QTabWidget()
        self._reports_tabs.setDocumentMode(True)
        self._reports_tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background: {DARK_BG}; }}
            QTabBar::tab {{
                background: {PANEL_BG}; color: {TEXT_SEC};
                padding: 6px 18px; border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {ACCENT_CYAN}; background: {DARK_BG};
                border-bottom: 2px solid {ACCENT_CYAN};
            }}
            QTabBar::tab:hover {{ color: {TEXT_PRI}; }}
        """)
        self._reports_tabs.currentChanged.connect(self._on_reports_tab_changed)

        _browser_style = (
            f"QTextBrowser {{ background: {DARK_BG}; border: none; color: {TEXT_PRI}; }}"
        )

        # Sub-tab 0: Sprint Report
        sprint_rpt_tab = QWidget()
        sprint_rpt_tab.setStyleSheet(f"background: {DARK_BG};")
        srt_layout = QVBoxLayout(sprint_rpt_tab)
        srt_layout.setContentsMargins(12, 10, 12, 8)
        srt_layout.setSpacing(6)

        # Scope bar
        srt_scope = QFrame()
        srt_scope.setStyleSheet(
            f"QFrame {{ background: {PANEL_BG}; border: 1px solid {BORDER}; "
            f"border-radius: 6px; }}"
        )
        srt_scope_layout = QHBoxLayout(srt_scope)
        srt_scope_layout.setContentsMargins(10, 6, 10, 6)
        srt_scope_layout.setSpacing(10)

        self._srt_sprint_rb = QRadioButton("Sprint")
        self._srt_sprint_rb.setChecked(True)
        self._srt_date_rb   = QRadioButton("Date Range")
        srt_scope_layout.addWidget(self._srt_sprint_rb)
        srt_scope_layout.addWidget(self._srt_date_rb)

        srt_scope_layout.addWidget(QLabel("Sprint:"))
        self._srt_sprint_sel = QComboBox()
        self._srt_sprint_sel.setMinimumWidth(200)
        self._srt_sprint_sel.setEnabled(False)
        srt_scope_layout.addWidget(self._srt_sprint_sel)

        self._srt_from = QLineEdit()
        self._srt_from.setPlaceholderText("From  YYYY-MM-DD")
        self._srt_from.setMaximumWidth(130)
        self._srt_from.setEnabled(False)
        self._srt_to = QLineEdit()
        self._srt_to.setPlaceholderText("To  YYYY-MM-DD")
        self._srt_to.setMaximumWidth(130)
        self._srt_to.setEnabled(False)
        srt_scope_layout.addWidget(self._srt_from)
        srt_scope_layout.addWidget(QLabel("→"))
        srt_scope_layout.addWidget(self._srt_to)
        srt_scope_layout.addStretch()

        self._srt_gen_btn = QPushButton("▶  Generate")
        self._srt_gen_btn.setObjectName("save_btn")
        self._srt_gen_btn.setEnabled(False)
        self._srt_gen_btn.clicked.connect(self._reports_generate_sprint)
        srt_scope_layout.addWidget(self._srt_gen_btn)
        srt_layout.addWidget(srt_scope)

        def _srt_toggle():
            use_sprint = self._srt_sprint_rb.isChecked()
            self._srt_sprint_sel.setEnabled(use_sprint and self._srt_sprint_sel.count() > 0)
            self._srt_from.setEnabled(not use_sprint)
            self._srt_to.setEnabled(not use_sprint)
        self._srt_sprint_rb.toggled.connect(_srt_toggle)
        self._srt_date_rb.toggled.connect(_srt_toggle)

        self._rpt_sprint_browser = QTextBrowser()
        self._rpt_sprint_browser.setOpenExternalLinks(True)
        self._rpt_sprint_browser.setStyleSheet(_browser_style)
        _apply_dark_palette(self._rpt_sprint_browser)
        srt_layout.addWidget(self._rpt_sprint_browser, 1)
        self._reports_tabs.addTab(sprint_rpt_tab, "📊  Sprint Report")

        # Sub-tab 1: People Report
        people_rpt_tab = QWidget()
        people_rpt_tab.setStyleSheet(f"background: {DARK_BG};")
        prt_layout = QVBoxLayout(people_rpt_tab)
        prt_layout.setContentsMargins(12, 10, 12, 8)
        prt_layout.setSpacing(6)

        # Scope + people bar
        prt_ctrl = QFrame()
        prt_ctrl.setStyleSheet(
            f"QFrame {{ background: {PANEL_BG}; border: 1px solid {BORDER}; "
            f"border-radius: 6px; }}"
        )
        prt_ctrl_layout = QHBoxLayout(prt_ctrl)
        prt_ctrl_layout.setContentsMargins(10, 6, 10, 6)
        prt_ctrl_layout.setSpacing(10)

        self._prt_sprint_rb = QRadioButton("Sprint")
        self._prt_sprint_rb.setChecked(True)
        self._prt_date_rb   = QRadioButton("Date Range")
        prt_ctrl_layout.addWidget(self._prt_sprint_rb)
        prt_ctrl_layout.addWidget(self._prt_date_rb)

        prt_ctrl_layout.addWidget(QLabel("Sprint:"))
        self._prt_sprint_sel = QComboBox()
        self._prt_sprint_sel.setMinimumWidth(200)
        self._prt_sprint_sel.setEnabled(False)
        prt_ctrl_layout.addWidget(self._prt_sprint_sel)

        self._prt_from = QLineEdit()
        self._prt_from.setPlaceholderText("From  YYYY-MM-DD")
        self._prt_from.setMaximumWidth(130)
        self._prt_from.setEnabled(False)
        self._prt_to = QLineEdit()
        self._prt_to.setPlaceholderText("To  YYYY-MM-DD")
        self._prt_to.setMaximumWidth(130)
        self._prt_to.setEnabled(False)
        prt_ctrl_layout.addWidget(self._prt_from)
        prt_ctrl_layout.addWidget(QLabel("→"))
        prt_ctrl_layout.addWidget(self._prt_to)

        prt_ctrl_layout.addSpacing(12)
        prt_ctrl_layout.addWidget(QLabel("People:"))
        self._prt_people_list = QListWidget()
        self._prt_people_list.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self._prt_people_list.setMaximumHeight(80)
        self._prt_people_list.setMaximumWidth(200)
        prt_ctrl_layout.addWidget(self._prt_people_list)

        self._prt_extra = QLineEdit()
        self._prt_extra.setPlaceholderText("Extra usernames (comma-separated)")
        self._prt_extra.setMaximumWidth(200)
        prt_ctrl_layout.addWidget(self._prt_extra)
        prt_ctrl_layout.addStretch()

        self._prt_gen_btn = QPushButton("▶  Generate")
        self._prt_gen_btn.setObjectName("save_btn")
        self._prt_gen_btn.setEnabled(False)
        self._prt_gen_btn.clicked.connect(self._reports_generate_people)
        prt_ctrl_layout.addWidget(self._prt_gen_btn)
        prt_layout.addWidget(prt_ctrl)

        def _prt_toggle():
            use_sprint = self._prt_sprint_rb.isChecked()
            self._prt_sprint_sel.setEnabled(use_sprint and self._prt_sprint_sel.count() > 0)
            self._prt_from.setEnabled(not use_sprint)
            self._prt_to.setEnabled(not use_sprint)
        self._prt_sprint_rb.toggled.connect(_prt_toggle)
        self._prt_date_rb.toggled.connect(_prt_toggle)

        self._rpt_people_browser = QTextBrowser()
        self._rpt_people_browser.setOpenExternalLinks(True)
        self._rpt_people_browser.setStyleSheet(_browser_style)
        _apply_dark_palette(self._rpt_people_browser)
        prt_layout.addWidget(self._rpt_people_browser, 1)
        self._reports_tabs.addTab(people_rpt_tab, "👤  People Report")

        # Sub-tab 2: Velocity
        velocity_tab = QWidget()
        velocity_tab.setStyleSheet(f"background: {DARK_BG};")
        vel_layout = QVBoxLayout(velocity_tab)
        vel_layout.setContentsMargins(16, 16, 16, 16)
        vel_layout.setSpacing(12)

        vel_heading = QLabel("◈  VELOCITY HISTORY")
        vel_heading.setObjectName("heading")
        vel_layout.addWidget(vel_heading)

        # QSvgWidget for the bar chart — scales with the widget
        try:
            from PyQt6.QtSvgWidgets import QSvgWidget
            self._rpt_vel_svg = QSvgWidget()
            self._rpt_vel_svg.setMinimumHeight(260)
            self._rpt_vel_svg.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self._rpt_vel_svg.setStyleSheet(f"background: {PANEL_BG}; border-radius: 8px;")
            self._rpt_vel_svg_available = True
        except ImportError:
            self._rpt_vel_svg = QLabel(
                "Install PyQt6-Qt6-Svg for the velocity chart.\n"
                "pip install PyQt6-Qt6-Svg\n\n"
                "The table below is still available."
            )
            self._rpt_vel_svg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._rpt_vel_svg.setStyleSheet(f"color: {TEXT_SEC}; padding: 40px;")
            self._rpt_vel_svg_available = False
        vel_layout.addWidget(self._rpt_vel_svg, 1)

        # Table below the chart
        self._rpt_vel_table = QTableWidget()
        self._rpt_vel_table.setColumnCount(6)
        self._rpt_vel_table.setHorizontalHeaderLabels(
            ["Sprint", "Total Pts", "Done Pts", "Stories", "Done", "Completion"]
        )
        hh = self._rpt_vel_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, 6):
            hh.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self._rpt_vel_table.verticalHeader().setVisible(False)
        self._rpt_vel_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._rpt_vel_table.setShowGrid(False)
        self._rpt_vel_table.setMaximumHeight(220)
        self._rpt_vel_table.setStyleSheet(
            f"QTableWidget {{ background: {PANEL_BG}; border: 1px solid {BORDER}; "
            f"border-radius: 6px; }} "
            f"QHeaderView::section {{ background: {CARD_BG}; color: {TEXT_SEC}; "
            f"padding: 6px 12px; border: none; font-size: 10px; "
            f"text-transform: uppercase; letter-spacing: 1px; }}"
        )
        vel_layout.addWidget(self._rpt_vel_table)
        self._reports_tabs.addTab(velocity_tab, "📈  Velocity")

        # Sub-tab 3: Compare
        compare_tab = QWidget()
        compare_tab.setStyleSheet(f"background: {DARK_BG};")
        cmp_layout = QVBoxLayout(compare_tab)
        cmp_layout.setContentsMargins(0, 0, 0, 0)
        self._rpt_compare_browser = QTextBrowser()
        self._rpt_compare_browser.setOpenExternalLinks(True)
        self._rpt_compare_browser.setStyleSheet(
            f"QTextBrowser {{ background: {DARK_BG}; border: none; color: {TEXT_PRI}; }}"
        )
        _apply_dark_palette(self._rpt_compare_browser)
        cmp_layout.addWidget(self._rpt_compare_browser)
        self._reports_tabs.addTab(compare_tab, "⇆  Compare")

        # Sub-tab 4: Burndown
        burndown_tab = QWidget()
        burndown_tab.setStyleSheet(f"background: {DARK_BG};")
        bd_layout = QVBoxLayout(burndown_tab)
        bd_layout.setContentsMargins(16, 16, 16, 16)
        bd_layout.setSpacing(12)

        bd_heading = QLabel("◈  BURNDOWN CHART")
        bd_heading.setObjectName("heading")
        bd_layout.addWidget(bd_heading)

        self._rpt_burndown_browser = QTextBrowser()
        self._rpt_burndown_browser.setOpenExternalLinks(False)
        self._rpt_burndown_browser.setStyleSheet(
            f"QTextBrowser {{ background: {DARK_BG}; border: none; color: {TEXT_PRI}; }}"
        )
        _apply_dark_palette(self._rpt_burndown_browser)
        bd_layout.addWidget(self._rpt_burndown_browser, 1)
        self._reports_tabs.addTab(burndown_tab, "📉  Burndown")

        self._reports_html      = ""   # tracks HTML for the active sub-tab
        self._reports_html_map  = {}   # sub-tab index → html string
        reports_outer_layout.addWidget(self._reports_tabs, 1)

        self.tabs.addTab(reports_outer, "📊  REPORTS")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        version_lbl = QLabel(f"◈  v{APP_VERSION}")
        version_lbl.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 11px; letter-spacing: 1px; padding: 0 12px;"
        )
        self.status_bar.addPermanentWidget(version_lbl)

        self._setup_shortcuts()

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(
            lambda: self.edit_panel.save_btn.click() if self.edit_panel.save_btn.isEnabled() else None
        )
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(
            lambda: self.new_story_btn.click() if self.new_story_btn.isEnabled() else None
        )
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(
            lambda: self.load_btn.click() if self.load_btn.isEnabled() else None
        )
        QShortcut(QKeySequence("Ctrl+I"), self).activated.connect(
            lambda: self.import_btn.click() if self.import_btn.isEnabled() else None
        )
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(
            lambda: self.export_btn.click() if self.export_btn.isEnabled() else None
        )
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(
            lambda: self.search_edit.setFocus()
        )
        QShortcut(QKeySequence("Ctrl+C"), self.table).activated.connect(
            self._copy_row_short
        )
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(
            self._copy_row_full
        )
        QShortcut(QKeySequence("Ctrl+Up"), self).activated.connect(
            lambda: self._navigate_story(-1)
        )
        QShortcut(QKeySequence("Ctrl+Down"), self).activated.connect(
            lambda: self._navigate_story(1)
        )
        QShortcut(QKeySequence("Ctrl+Shift+M"), self).activated.connect(
            self._copy_row_markdown
        )

        # ? — shortcut reference card
        QShortcut(QKeySequence("?"), self).activated.connect(self._show_shortcut_dialog)
        # N — New story (when stories are loaded)
        QShortcut(QKeySequence("N"), self.table).activated.connect(
            lambda: self.new_story_btn.click() if self.new_story_btn.isEnabled() else None
        )
        # R — Refresh
        QShortcut(QKeySequence("R"), self.table).activated.connect(
            lambda: self.refresh_btn.click() if self.refresh_btn.isEnabled() else None
        )
        # S — Save (story edit panel)
        QShortcut(QKeySequence("S"), self.table).activated.connect(
            lambda: self.edit_panel.save_btn.click() if self.edit_panel.save_btn.isEnabled() else None
        )
        # Escape — clear table selection
        QShortcut(QKeySequence("Escape"), self.table).activated.connect(
            lambda: self.table.clearSelection()
        )
        # Delete — open archive picker for the selected row
        QShortcut(QKeySequence("Delete"), self.table).activated.connect(
            self._delete_selected_shortcut
        )
        # Arrow keys — navigate rows (Up/Down already work natively in QTableWidget;
        # we add these as aliases for Ctrl+Up / Ctrl+Down when table has focus)
        QShortcut(QKeySequence(Qt.Key.Key_Up), self.table).activated.connect(
            lambda: self._navigate_story(-1)
        )
        QShortcut(QKeySequence(Qt.Key.Key_Down), self.table).activated.connect(
            lambda: self._navigate_story(1)
        )
        # Alt+1/2/3 — switch tabs
        QShortcut(QKeySequence("Alt+1"), self).activated.connect(
            lambda: self.tabs.setCurrentIndex(0)
        )
        QShortcut(QKeySequence("Alt+2"), self).activated.connect(
            lambda: self._switch_to_kanban()
        )
        QShortcut(QKeySequence("Alt+3"), self).activated.connect(
            self._switch_to_backlog
        )
        QShortcut(QKeySequence("Alt+4"), self).activated.connect(
            lambda: self.tabs.setCurrentIndex(3)
        )

    def _delete_selected_shortcut(self):
        """Delete key: open the archive picker pre-selecting the current row."""
        issue = self._selected_issue()
        if not issue:
            return
        key = issue.get("key", "")
        reply = QMessageBox.question(
            self, "Archive Story",
            f"Archive  {key}?\n\nArchived issues become read-only and are removed from boards.\n"
            "They can be restored from Jira administration.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._busy(True)
        self._status(f"Archiving {key}…")

        def _do():
            return self._client.archive_issues([key])

        def _on_done(result):
            self._busy(False)
            errors = result.get("errors", []) if isinstance(result, dict) else []
            if not errors:
                self._status(f"✓ Archived {key}.")
                self._issues = [i for i in self._issues if i.get("key") != key]
                self._populate_table(self._issues)
                self._update_velocity_bar()
                self._populate_assignee_filter()
                self.story_count_lbl.setText(f"{len(self._issues)} stories")
            else:
                QMessageBox.warning(self, "Archive Failed", "\n".join(str(e) for e in errors))
                self._status("⚠ Archive had errors.")

        self._spawn(_do, on_result=_on_done,
                    on_error=lambda e: (self._busy(False),
                                        self._status("✗ Archive failed."),
                                        QMessageBox.critical(self, "Archive Failed", str(e))))

    # ── Inline editing ────────────────────────────────────────────────────────
    def _on_cell_double_clicked(self, row: int, col: int):
        """Inline-edit story points, assignee, status, or due date on double-click."""
        key_item = self.table.item(row, COL_KEY)
        if not key_item:
            return
        key = key_item.text()
        issue = next((i for i in self._issues if i.get("key") == key), None)
        if not issue:
            return

        if col == COL_STORY_PTS:
            self._inline_edit_pts(row, key, issue)
        elif col == COL_ASSIGNEE:
            self._inline_edit_assignee(row, key, issue)
        elif col == COL_STATUS:
            self._inline_edit_status(row, key, issue)
        elif col == COL_DUE_DATE:
            self._inline_edit_due_date(row, key, issue)

    def _inline_edit_pts(self, row: int, key: str, issue: dict):
        """Pop a combo in-line to change story points without opening the full edit panel."""
        f = issue.get("fields", {})
        pts_raw = next(
            (f.get(k) for k in ([self._sp_field] + JiraClient._SP_FALLBACKS)
             if f.get(k) is not None), None
        )
        try:
            current_pts = int(float(pts_raw)) if pts_raw is not None else None
        except (TypeError, ValueError):
            current_pts = None

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Edit Story Points — {key}")
        dlg.setFixedSize(280, 140)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        lbl = QLabel(f"Story points for  <b>{key}</b>:")
        lbl.setStyleSheet(f"color: {TEXT_PRI};")
        layout.addWidget(lbl)
        combo = QComboBox()
        combo.addItem("— Not set —", None)
        for v in FIBONACCI:
            label = str(v)
            if v in (13, 21):
                label += "  — consider splitting"
            combo.addItem(label, v)
        # Pre-select current value
        for i in range(combo.count()):
            if combo.itemData(i) == current_pts:
                combo.setCurrentIndex(i)
                break
        layout.addWidget(combo)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Save")
        btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("save_btn")
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new_pts = combo.currentData()
        sp = self._sp_field
        fields_payload = {sp: new_pts}

        self._busy(True)
        self._status(f"Updating story points for {key}…")

        def _do():
            self._client.update_issue(key, fields_payload)

        def _on_done(_):
            self._busy(False)
            pts_str = str(new_pts) if new_pts is not None else "—"
            self._status(f"✓ {key} story points set to {pts_str}.")
            # Update local cache
            f = issue.get("fields", {})
            f[sp] = new_pts
            self._load_sprint_issues(reselect_key=key)

        self._spawn(
            _do,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status(f"✗ Failed to update {key} story points."),
                QMessageBox.critical(self, "Update Failed", str(e)),
            ),
        )

    def _inline_edit_assignee(self, row: int, key: str, issue: dict):
        """Pop a combo in-line to reassign a story without opening the full edit panel."""
        if not self._users_cache:
            self._status("Loading users for inline edit…")
            self._refresh_users_cache(on_done=lambda _: self._inline_edit_assignee(row, key, issue))
            return

        f = issue.get("fields", {})
        aobj = f.get("assignee") or {}
        current_uid = aobj.get("name") or aobj.get("accountId") or None

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Reassign — {key}")
        dlg.setFixedSize(320, 150)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        lbl = QLabel(f"Assignee for  <b>{key}</b>:")
        lbl.setStyleSheet(f"color: {TEXT_PRI};")
        layout.addWidget(lbl)
        combo = QComboBox()
        combo.addItem("— Unassigned —", None)
        for m in self._users_cache:
            uid  = m.get("name") or m.get("accountId")
            name = m.get("displayName", "?")
            combo.addItem(name, uid)
        for i in range(combo.count()):
            if combo.itemData(i) == current_uid:
                combo.setCurrentIndex(i)
                break
        layout.addWidget(combo)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Reassign")
        btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("save_btn")
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new_uid  = combo.currentData()
        new_name = combo.currentText()
        fields_payload = {"assignee": {"name": new_uid} if new_uid else None}

        self._busy(True)
        self._status(f"Reassigning {key}…")

        def _do():
            self._client.update_issue(key, fields_payload)

        def _on_done(_):
            self._busy(False)
            self._status(f"✓ {key} assigned to {new_name}.")
            self._load_sprint_issues(reselect_key=key)

        self._spawn(
            _do,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status(f"✗ Failed to reassign {key}."),
                QMessageBox.critical(self, "Reassign Failed", str(e)),
            ),
        )

    def _inline_edit_status(self, row: int, key: str, issue: dict):
        """Pop a transition combo in-line to change status without opening the full panel."""
        if not self._client:
            return
        self._busy(True)
        self._status(f"Fetching transitions for {key}…")

        def _do():
            return self._client.get_issue_transitions(key)

        def _on_transitions(transitions):
            self._busy(False)
            if not transitions:
                QMessageBox.information(self, "No Transitions", f"No transitions available for {key}.")
                return
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Change Status — {key}")
            dlg.setFixedSize(300, 140)
            dlg.setStyleSheet(self.styleSheet())
            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(10)
            lbl = QLabel(f"Transition  <b>{key}</b>  to:")
            lbl.setStyleSheet(f"color: {TEXT_PRI};")
            layout.addWidget(lbl)
            combo = QComboBox()
            for t in transitions:
                name = t.get("to", {}).get("name", t.get("name", ""))
                combo.addItem(name, t["id"])
            layout.addWidget(combo)
            btns = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            btns.button(QDialogButtonBox.StandardButton.Ok).setText("Apply")
            btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("save_btn")
            btns.accepted.connect(dlg.accept)
            btns.rejected.connect(dlg.reject)
            layout.addWidget(btns)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
            tid   = combo.currentData()
            tname = combo.currentText()
            self._busy(True)
            self._status(f"Transitioning {key} → {tname}…")
            self._spawn(
                self._client.transition_issue, key, tid,
                on_result=lambda _: (
                    self._busy(False),
                    self._status(f"✓ {key} → {tname}"),
                    self._load_sprint_issues(reselect_key=key),
                ),
                on_error=lambda e: (
                    self._busy(False),
                    self._status(f"✗ Transition failed: {e}"),
                    QMessageBox.critical(self, "Transition Failed", str(e)),
                ),
            )

        self._spawn(
            _do,
            on_result=_on_transitions,
            on_error=lambda e: (
                self._busy(False),
                self._status(f"✗ Could not fetch transitions: {e}"),
            ),
        )

    def _inline_edit_due_date(self, row: int, key: str, issue: dict):
        """Pop a date picker in-line to change due date without opening the full panel."""
        f       = issue.get("fields", {})
        current = (f.get("duedate") or "")[:10]
        dlg     = QDialog(self)
        dlg.setWindowTitle(f"Set Due Date — {key}")
        dlg.setFixedSize(300, 160)
        dlg.setStyleSheet(self.styleSheet())
        layout  = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        lbl = QLabel(f"Due date for  <b>{key}</b>:")
        lbl.setStyleSheet(f"color: {TEXT_PRI};")
        layout.addWidget(lbl)
        picker = QDateEdit()
        picker.setCalendarPopup(True)
        picker.setDisplayFormat("yyyy-MM-dd")
        if current:
            try:
                picker.setDate(QDate.fromString(current, "yyyy-MM-dd"))
            except Exception:
                picker.setDate(QDate.currentDate())
        else:
            picker.setDate(QDate.currentDate())
        layout.addWidget(picker)
        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear Date")
        clear_btn.setObjectName("danger")
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Save")
        btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("save_btn")
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        cleared = [False]
        clear_btn.clicked.connect(lambda: (cleared.__setitem__(0, True), dlg.accept()))

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new_date = None if cleared[0] else picker.date().toString("yyyy-MM-dd")
        self._busy(True)
        self._status(f"Updating due date for {key}…")
        self._spawn(
            self._client.update_issue, key, {"duedate": new_date},
            on_result=lambda _: (
                self._busy(False),
                self._status(f"✓ {key} due date set to {new_date or 'none'}."),
                self._load_sprint_issues(reselect_key=key),
            ),
            on_error=lambda e: (
                self._busy(False),
                self._status(f"✗ Failed to update due date: {e}"),
                QMessageBox.critical(self, "Update Failed", str(e)),
            ),
        )

    # ── Sprint manager ────────────────────────────────────────────────────────
    def _open_sprint_manager(self):
        board_id   = self.board_combo.currentData()
        board_name = self.board_combo.currentText()
        if not board_id or not self._client:
            return
        dlg = SprintManagerDialog(
            board_id   = board_id,
            board_name = board_name,
            sprints    = list(self._sprints),
            client     = self._client,
            parent     = self,
        )
        dlg.sprint_changed.connect(self._on_sprint_manager_changed)
        dlg.exec()

    def _on_sprint_manager_changed(self):
        """Reload the sprint list after any create/start/close operation."""
        bid = self.board_combo.currentData()
        if not bid or not self._client:
            return
        self._busy(True)
        self._status("Reloading sprints…")
        self._spawn(
            self._client.get_sprints, bid,
            on_result=self._on_sprints_loaded,
            on_error=lambda e: (self._busy(False), self._status(f"⚠ {e}")),
        )

    # ── Velocity history ──────────────────────────────────────────────────────
    def _open_velocity_history(self):
        board_id = self.board_combo.currentData()
        if not board_id or not self._client:
            return
        dlg = VelocityHistoryDialog(board_id, self._client, self)
        dlg.exec()

    # ── Story ranking ─────────────────────────────────────────────────────────
    def _rank_selected(self, delta: int):
        """Move the selected story up (delta=-1) or down (delta=1) one rank slot."""
        visible = [r for r in range(self.table.rowCount()) if not self.table.isRowHidden(r)]
        if not visible:
            return
        current = self.table.currentRow()
        if current not in visible:
            return
        idx = visible.index(current)
        target_idx = idx + delta
        if target_idx < 0 or target_idx >= len(visible):
            return
        target_row = visible[target_idx]

        key_item    = self.table.item(current, COL_KEY)
        target_item = self.table.item(target_row, COL_KEY)
        if not key_item or not target_item:
            return
        key        = key_item.text()
        target_key = target_item.text()

        self._busy(True)
        self._status(f"Ranking {key}…")

        rank_before = target_key if delta < 0 else ""
        rank_after  = target_key if delta > 0 else ""

        def _do():
            self._client.rank_issue(key, rank_before_key=rank_before, rank_after_key=rank_after)

        def _on_done(_):
            self._busy(False)
            self._status(f"✓ {key} re-ranked.")
            self._load_sprint_issues(reselect_key=key)

        self._spawn(
            _do,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status(f"⚠ Ranking not supported or failed: {e}"),
                QMessageBox.warning(
                    self, "Rank Failed",
                    f"Could not re-rank {key}.\n\n"
                    "Ranking requires the board to have ranking enabled "
                    "and the Agile rank field to be writable.\n\n"
                    f"Detail: {e}",
                ),
            ),
        )

    # ── Backlog move-to-sprint ────────────────────────────────────────────────
    def _on_backlog_move_to_sprint(self, key: str, sprint_id: int):
        """Move a backlog story into the given sprint."""
        if not self._client:
            return
        self._busy(True)
        self._status(f"Moving {key} to sprint…")

        def _do():
            self._client.move_to_sprint(key, sprint_id)

        def _on_done(_):
            self._busy(False)
            self._status(f"✓ {key} moved to sprint.")
            # Remove from backlog display
            for row in range(self.backlog_widget._table.rowCount()):
                it = self.backlog_widget._table.item(row, 0)
                if it and it.text() == key:
                    self.backlog_widget._table.removeRow(row)
                    self.backlog_widget._issues = [
                        i for i in self.backlog_widget._issues if i.get("key") != key
                    ]
                    n = len(self.backlog_widget._issues)
                    self.backlog_widget._count_lbl.setText(f"{n} backlog items")
                    break

        self._spawn(
            _do,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status(f"✗ Failed to move {key}: {e}"),
                QMessageBox.critical(self, "Move Failed", str(e)),
            ),
        )
    def _on_kanban_load_requested(self):
        """User clicked Load from the Kanban toolbar — sync selection and load."""
        kb = self.kanban_widget
        proj_idx   = kb._kb_project_combo.currentIndex()
        board_idx  = kb._kb_board_combo.currentIndex()
        sprint_idx = kb._kb_sprint_combo.currentIndex()

        if proj_idx >= 0:
            self.project_combo.blockSignals(True)
            self.project_combo.setCurrentIndex(proj_idx)
            self.project_combo.blockSignals(False)
        if board_idx >= 0:
            self.board_combo.blockSignals(True)
            self.board_combo.setCurrentIndex(board_idx)
            self.board_combo.blockSignals(False)
        if sprint_idx >= 0:
            self.sprint_combo.blockSignals(True)
            self.sprint_combo.setCurrentIndex(sprint_idx)
            self.sprint_combo.blockSignals(False)

        self.load_btn.click()

    def _switch_to_kanban(self):
        self.tabs.setCurrentIndex(1)
        # Always keep the load toolbar in sync with current Stories selections
        self.kanban_widget.sync_combos(
            self.project_combo, self.board_combo, self.sprint_combo
        )
        if self._issues:
            self.kanban_widget.populate(self._issues, self._sp_field)

    def _on_kanban_story_selected(self, key: str):
        """When a Kanban card is clicked, switch to Stories tab and select that row."""
        self.tabs.setCurrentIndex(0)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == key:
                self.table.selectRow(row)
                self.table.scrollToItem(item)
                break

    def _on_kanban_transition(self, key: str, new_status_name: str):
        """Card was dragged to a new column — find and apply the matching transition.

        Matching strategy:
        1. Exact match on the transition's *target* status name.
        2. Case-insensitive exact match on the target status name.
        3. Fuzzy: target status name starts-with or contains the requested name.
        4. Fuzzy: the *transition* name itself contains the requested name.
        """
        if not self._client:
            return
        self._busy(True)
        self._status(f"Transitioning {key} → {new_status_name}…")

        def _do():
            transitions = self._client.get_issue_transitions(key)
            target_lc   = new_status_name.lower()

            def _score(t):
                to_name   = (t.get("to") or {}).get("name", "")
                tr_name   = t.get("name", "")
                to_lc     = to_name.lower()
                tr_lc     = tr_name.lower()
                if to_lc == target_lc:
                    return 4
                if to_lc.startswith(target_lc) or target_lc in to_lc:
                    return 3
                if tr_lc == target_lc:
                    return 2
                if tr_lc.startswith(target_lc) or target_lc in tr_lc:
                    return 1
                return 0

            scored = sorted(transitions, key=_score, reverse=True)
            best   = scored[0] if scored and _score(scored[0]) > 0 else None
            if not best:
                raise RuntimeError(
                    f'No transition matching "{new_status_name}" found for {key}.\n'
                    f'Available transitions: {", ".join(t.get("name","?") for t in transitions)}'
                )
            self._client.transition_issue(key, best["id"])

        def _on_done(_):
            self._busy(False)
            self._status(f"✓ {key} → {new_status_name}")
            self._spawn(
                self._client.get_sprint_issues,
                self.board_combo.currentData(),
                self.sprint_combo.currentData(),
                on_result=lambda issues: (
                    setattr(self, '_issues', issues),
                    self._populate_table(issues),
                    self._update_velocity_bar(),
                    self.kanban_widget.refresh(issues, self._sp_field),
                ),
            )

        self._spawn(
            _do,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status(f"✗ Transition failed: {e}"),
                QMessageBox.warning(self, "Transition Failed", str(e)),
                self.kanban_widget.refresh(self._issues, self._sp_field),
            ),
        )

    def _switch_to_backlog(self):
        self.tabs.setCurrentIndex(2)
        self.backlog_widget.sync_combos(self.project_combo, self.board_combo)

    def _on_backlog_load_requested(self):
        """User clicked Load Backlog from within BacklogWidget — sync selections and load."""
        kb = self.backlog_widget

        proj_idx  = kb._bl_project_combo.currentIndex()
        board_idx = kb._bl_board_combo.currentIndex()

        if proj_idx >= 0:
            self.project_combo.blockSignals(True)
            self.project_combo.setCurrentIndex(proj_idx)
            self.project_combo.blockSignals(False)

        if board_idx >= 0:
            self.board_combo.blockSignals(True)
            self.board_combo.setCurrentIndex(board_idx)
            self.board_combo.blockSignals(False)

        self._load_backlog()

    # ── Backlog helpers ───────────────────────────────────────────────────────
    def _load_backlog(self):
        """Fetch issues not in any sprint for the current project.

        Tries `sprint is EMPTY` first (standard DC). Falls back to
        `sprint not in openSprints() AND sprint not in closedSprints()` if the
        first form is rejected (some older instances don't support it).
        """
        project_key = self.project_combo.currentData()
        if not project_key or not self._client:
            return
        self._busy(True)
        self._status("Loading backlog…")

        def _fetch(jql: str) -> list:
            sp      = self._sp_field
            fields  = ",".join([
                "summary", "assignee", "status", "priority", "issuetype",
                "duedate", sp, "comment",
            ])
            encoded = urllib.parse.quote(jql)
            all_issues: list = []
            start = 0
            max_results = 100
            while True:
                url = (
                    f"{self._client.base_url}/rest/api/{self._client.api_version}/search"
                    f"?jql={encoded}&maxResults={max_results}&startAt={start}&fields={fields}"
                )
                req = urllib.request.Request(url, headers=self._client.headers)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                batch = data.get("issues", [])
                all_issues.extend(batch)
                if len(batch) < max_results:
                    break
                start += max_results
            return all_issues

        def _do():
            base = f'project = "{project_key}" AND statusCategory != Done'
            try:
                return _fetch(f"{base} AND sprint is EMPTY ORDER BY priority DESC, updated DESC")
            except Exception as e1:
                # Fallback for instances where 'sprint is EMPTY' isn't supported
                try:
                    return _fetch(
                        f"{base} AND sprint not in openSprints() "
                        f"AND sprint not in closedSprints() "
                        f"ORDER BY priority DESC, updated DESC"
                    )
                except Exception as e2:
                    raise RuntimeError(
                        f"Could not load backlog.\n"
                        f"Primary JQL failed: {e1}\n"
                        f"Fallback JQL failed: {e2}"
                    )

        def _on_done(issues):
            self._busy(False)
            self._status(f"✓ Loaded {len(issues)} backlog items.")
            self.backlog_widget.populate(issues, self._sp_field)

        self._spawn(
            _do,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status("✗ Failed to load backlog."),
                QMessageBox.critical(self, "Backlog Load Failed", str(e)),
            ),
        )

    def _on_backlog_story_selected(self, key: str):
        """Load the selected backlog story into the edit panel on the Stories tab."""
        # Try to find the issue in the sprint; if not there, we still select in the backlog
        issue = next((i for i in self._issues if i.get("key") == key), None)
        if issue:
            self.tabs.setCurrentIndex(0)
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text() == key:
                    self.table.selectRow(row)
                    self.table.scrollToItem(item)
                    break

    def _selected_issue(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        key_item = self.table.item(row, 0)
        if not key_item:
            return None
        key = key_item.text()
        return next((iss for iss in self._issues if iss.get("key") == key), None)

    def _copy_row_short(self):
        row = self.table.currentRow()
        if row < 0:
            return
        parts = []
        for col in range(self.table.columnCount()):
            if not self.table.isColumnHidden(col):
                item = self.table.item(row, col)
                parts.append(item.text() if item else "")
        QApplication.clipboard().setText(",".join(parts))
        self._status("✓ Row copied to clipboard.")

    def _copy_row_full(self):
        issue = self._selected_issue()
        if not issue:
            return
        sp_field = self._sp_field
        fl_field = self.edit_panel._fl_field
        fields   = issue.get("fields") or {}

        assignee_obj = fields.get("assignee") or {}
        assignee = assignee_obj.get("displayName") or assignee_obj.get("name") or ""
        status       = (fields.get("status")    or {}).get("name", "")
        issue_type   = (fields.get("issuetype") or {}).get("name", "")
        priority     = (fields.get("priority")  or {}).get("name", "")

        pts_raw = next((fields.get(k) for k in ([sp_field] + JiraClient._SP_FALLBACKS) if fields.get(k) is not None), None)
        try:
            story_points = int(float(pts_raw)) if pts_raw is not None else ""
        except (TypeError, ValueError):
            story_points = ""

        feature_link = fields.get(fl_field, "") or ""
        due_date     = fields.get("duedate", "") or ""

        sprint_name  = ""
        sprint_data  = fields.get("customfield_10020") or fields.get("sprint")
        if isinstance(sprint_data, list) and sprint_data:
            sprint_name = sprint_data[-1].get("name", "")
        elif isinstance(sprint_data, dict):
            sprint_name = sprint_data.get("name", "")

        desc = fields.get("description") or ""
        if isinstance(desc, dict):
            desc = self.edit_panel._adf_to_text(desc)
        desc = desc.replace("\n", " ").strip()

        comments_data = (fields.get("comment") or {}).get("comments", [])
        comment_parts = []
        for c in comments_data:
            author = ((c.get("author") or {}).get("displayName") or
                      (c.get("author") or {}).get("name") or "")
            body = c.get("body", "")
            if isinstance(body, dict):
                body = self.edit_panel._adf_to_text(body)
            body = body.replace("\n", " ").strip()
            comment_parts.append(f"[{author}]: {body}")
        comments = " | ".join(comment_parts)

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            issue.get("key", ""), fields.get("summary", ""), assignee,
            status, issue_type, priority, story_points, feature_link,
            due_date, sprint_name, desc, comments,
        ])
        QApplication.clipboard().setText(buf.getvalue().strip())
        self._status("✓ Full issue copied to clipboard.")

    # ── Row context menu ──────────────────────────────────────────────────────
    def _navigate_story(self, delta: int):
        visible = [r for r in range(self.table.rowCount()) if not self.table.isRowHidden(r)]
        if not visible: return
        current = self.table.currentRow()
        if current not in visible:
            next_row = visible[0] if delta > 0 else visible[-1]
        else:
            idx = visible.index(current)
            next_row = visible[max(0, min(len(visible)-1, idx+delta))]
        self.table.selectRow(next_row)
        self.table.scrollTo(self.table.model().index(next_row, 0))

    def _copy_row_markdown(self):
        issue = self._selected_issue()
        if not issue: return
        sp = self._sp_field
        f  = issue.get("fields", {})
        key      = issue["key"]
        summary  = f.get("summary", "")
        assignee = (f.get("assignee") or {}).get("displayName", "—")
        status   = (f.get("status") or {}).get("name", "—")
        pts_raw  = next((f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS) if f.get(k) is not None), None)
        try:
            pts = str(int(float(pts_raw))) if pts_raw is not None else "—"
        except (TypeError, ValueError):
            pts = "—"
        base_url = self.edit_panel._base_url
        key_md = f"[{key}]({base_url}/browse/{key})" if base_url else key
        QApplication.clipboard().setText(f"| {key_md} | {summary} | {assignee} | {status} | {pts} |")
        self._status("✓ Row copied as Markdown.")

    def _show_row_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        key_item = self.table.item(row, 0)
        if not key_item:
            return
        key = key_item.text()

        # Collect all selected keys (for bulk operations)
        selected_rows = list({idx.row() for idx in self.table.selectedIndexes()})
        selected_keys = []
        for r in selected_rows:
            ki = self.table.item(r, 0)
            if ki:
                selected_keys.append(ki.text())
        if not selected_keys:
            selected_keys = [key]

        menu = QMenu(self)
        open_action  = menu.addAction("⎋  Open in Jira")
        copy_key     = menu.addAction("⎘  Copy Key")
        copy_row     = menu.addAction("⎘  Copy Row")
        menu.addSeparator()
        copy_full    = menu.addAction("⎘  Copy Full Issue")
        copy_md      = menu.addAction("⎘  Copy as Markdown")
        menu.addSeparator()
        duplicate    = menu.addAction("⧉  Duplicate Story")

        # ── Bulk status transition (shown when ≥1 stories selected) ──────────
        menu.addSeparator()
        if len(selected_keys) > 1:
            bulk_label = menu.addAction(f"⟳  Transition {len(selected_keys)} stories to…")
            bulk_label.setEnabled(False)
        else:
            bulk_label = None
        status_actions = {}
        for status_name in ["To Do", "In Progress", "In Review", "Done", "Blocked"]:
            act = menu.addAction(f"   → {status_name}")
            status_actions[act] = status_name

        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
        if chosen == open_action:
            if self.edit_panel._base_url:
                webbrowser.open(f"{self.edit_panel._base_url}/browse/{key}")
        elif chosen == copy_key:
            QApplication.clipboard().setText(key)
            self._status(f"✓ Copied {key} to clipboard.")
        elif chosen == copy_row:
            self.table.selectRow(row)
            self._copy_row_short()
        elif chosen == copy_full:
            self.table.selectRow(row)
            self._copy_row_full()
        elif chosen == copy_md:
            self.table.selectRow(row)
            self._copy_row_markdown()
        elif chosen == duplicate:
            self._duplicate_story(key)
        elif chosen in status_actions:
            target_status = status_actions[chosen]
            self._bulk_transition(selected_keys, target_status)

    # ── Bulk status transition ────────────────────────────────────────────────
    def _bulk_transition(self, keys: list, target_status_name: str):
        """Transition multiple issues to the named status via available transitions."""
        if not keys or not self._client:
            return

        n = len(keys)
        self._busy(True)
        self._status(f"Fetching transitions for {n} stor{'ies' if n != 1 else 'y'}…")

        def _do_bulk():
            results = {"ok": [], "failed": [], "no_transition": []}
            for key in keys:
                try:
                    transitions = self._client.get_issue_transitions(key)
                    match = next(
                        (t for t in transitions
                         if t.get("to", {}).get("name", "").lower() == target_status_name.lower()),
                        None,
                    )
                    if not match:
                        results["no_transition"].append(key)
                        continue
                    self._client.transition_issue(key, match["id"])
                    results["ok"].append(key)
                except Exception as e:
                    results["failed"].append(f"{key}: {e}")
            return results

        def _on_done(results):
            self._busy(False)
            ok    = results["ok"]
            fail  = results["failed"]
            no_tr = results["no_transition"]
            parts = [f'✓ {len(ok)} transitioned to "{target_status_name}".']
            if no_tr:
                parts.append(f'⚠ {len(no_tr)} had no "{target_status_name}" transition: {", ".join(no_tr)}')
            if fail:
                parts.append("✗ Failures:\n" + "\n".join(fail[:5]))
            msg = "\n".join(parts)
            if fail or no_tr:
                QMessageBox.warning(self, "Bulk Transition", msg)
            else:
                self._status(msg.split("\n")[0])
            if ok:
                self._load_sprint_issues(reselect_key=ok[-1])

        self._spawn(
            _do_bulk,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status("✗ Bulk transition failed."),
                QMessageBox.critical(self, "Bulk Transition Failed", str(e)),
            ),
        )

    # ── Token storage ─────────────────────────────────────────────────────────
    @staticmethod
    def _save_token(instance: str, token: str) -> bool:
        if not _KEYRING_AVAILABLE:
            return False
        try:
            if token:
                keyring.set_password(_KEYRING_SERVICE, instance, token)
            else:
                try:
                    keyring.delete_password(_KEYRING_SERVICE, instance)
                except keyring.errors.PasswordDeleteError:
                    pass
            return True
        except Exception:
            return False

    @staticmethod
    def _load_token(instance: str, qs_fallback: str = "") -> str:
        if _KEYRING_AVAILABLE:
            try:
                stored = keyring.get_password(_KEYRING_SERVICE, instance)
                if stored is not None:
                    return stored
            except Exception:
                pass
        try:
            return base64.b64decode(qs_fallback.encode()).decode() if qs_fallback else ""
        except Exception:
            return ""

    def _clear_sprint_view(self):
        self.board_combo.blockSignals(True)
        self.board_combo.clear()
        self.board_combo.blockSignals(False)

        self.sprint_combo.blockSignals(True)
        self.sprint_combo.clear()
        self.sprint_combo.blockSignals(False)

        self.table.setRowCount(0)
        self.story_count_lbl.setText("No stories loaded")
        self.velocity_lbl.setText("")
        self.sprint_lbl.setText("")
        self._issues = []
        self._users_cache = []
        self._apply_default_columns()

        self.export_btn.setEnabled(False)
        self.bulk_create_btn.setEnabled(False)
        self._rpt_gen_btn.setEnabled(False)
        self.archive_btn.setEnabled(False)
        self.bulk_edit_btn.setEnabled(False)
        self._rpt_gen_btn.setEnabled(False)
        self._rpt_people_btn.setEnabled(False)
        self._rpt_velocity_btn.setEnabled(False)
        self._rpt_burndown_btn.setEnabled(False)
        self._rpt_save_btn.setEnabled(False)
        self._rpt_sprint_combo.setEnabled(False)
        self._rpt_sprint_combo.clear()
        self._srt_sprint_sel.setEnabled(False)
        self._srt_sprint_sel.clear()
        self._srt_gen_btn.setEnabled(False)
        self._prt_sprint_sel.setEnabled(False)
        self._prt_sprint_sel.clear()
        self._prt_people_list.clear()
        self._prt_gen_btn.setEnabled(False)
        self._rpt_sprint_browser.clear()
        self._rpt_people_browser.clear()
        self._rpt_compare_browser.clear()
        self._rpt_burndown_browser.clear()
        self._reports_html_map.clear()
        self._reports_html = ""
        self._rpt_vel_table.setRowCount(0)
        self._progress_bar.setVisible(False)
        self._progress_bar.setValue(0)
        self.quick_add_edit.clear()
        self.quick_add_type_combo.setEnabled(False)
        self.quick_add_type_combo.clear()
        self.compare_combo.setEnabled(False)
        self.compare_combo.clear()
        self.compare_btn.setEnabled(False)
        self.sprint_mgr_btn.setEnabled(False)
        self.tabs.setTabText(1, "⊞  ACTIVE SPRINT")
        self.kanban_widget.set_sprint_name("")
        self.kanban_widget.clear()
        self.assignee_filter_combo.clear()
        self.edit_panel.current_key = None
        self.edit_panel.title_lbl.setText("Select a story to edit")
        self.edit_panel.key_lbl.setText("")
        self.edit_panel.status_badge.setText("")
        self.edit_panel.save_btn.setEnabled(False)
        self.edit_panel.open_jira_btn.setEnabled(False)
        self.edit_panel._snapshot = {}

    def _save_settings(self):
        qs = QSettings("SprintMate", "SprintMate")
        s  = self._settings

        qs.setValue("mode",                       s.get("mode", ""))
        qs.setValue("secondary_url",               s.get("secondary_url", ""))
        qs.setValue("secondary_token_expiry",      s.get("secondary_token_expiry", ""))
        qs.setValue("secondary_display_name",      s.get("secondary_display_name", ""))
        qs.setValue("secondary_default_project",   s.get("secondary_default_project", ""))
        qs.setValue("secondary_default_board",     s.get("secondary_default_board", ""))
        qs.setValue("secondary_filter_projects",   s.get("secondary_filter_projects", ""))
        qs.setValue("secondary_filter_boards",     s.get("secondary_filter_boards", ""))
        qs.setValue("primary_url",                   s.get("primary_url", ""))
        qs.setValue("primary_token_expiry",          s.get("primary_token_expiry", ""))
        qs.setValue("primary_display_name",          s.get("primary_display_name", ""))
        qs.setValue("primary_default_project",       s.get("primary_default_project", ""))
        qs.setValue("primary_default_board",         s.get("primary_default_board", ""))
        qs.setValue("primary_filter_projects",       s.get("primary_filter_projects", ""))
        qs.setValue("primary_filter_boards",         s.get("primary_filter_boards", ""))

        for instance, key in [("secondary", "secondary_token"), ("primary", "primary_token")]:
            token = s.get(key, "")
            if self._save_token(instance, token):
                qs.remove(key)
            else:
                qs.setValue(key, base64.b64encode(token.encode()).decode() if token else "")

        # Persist recent keys (MRU list)
        qs.setValue("recent_keys", json.dumps(self._recent_keys))

        # Persist column prefs per board (convert sets to sorted lists for JSON)
        col_prefs_serialisable = {
            board_id: sorted(visible)
            for board_id, visible in self._column_prefs.items()
        }
        qs.setValue("column_prefs", json.dumps(col_prefs_serialisable))

    def _load_settings(self) -> dict:
        qs = QSettings("SprintMate", "SprintMate")

        # Restore recent keys
        try:
            self._recent_keys = json.loads(qs.value("recent_keys", "[]"))
        except (json.JSONDecodeError, TypeError):
            self._recent_keys = []

        # Restore column prefs
        try:
            raw = json.loads(qs.value("column_prefs", "{}"))
            self._column_prefs = {bid: set(cols) for bid, cols in raw.items()}
        except (json.JSONDecodeError, TypeError):
            self._column_prefs = {}

        return {
            "mode":                       qs.value("mode", JiraClient.MODE_SECONDARY),
            "secondary_url":               qs.value("secondary_url", ""),
            "secondary_token":             self._load_token("secondary", qs.value("secondary_token", "")),
            "secondary_token_expiry":      qs.value("secondary_token_expiry", ""),
            "secondary_display_name":      qs.value("secondary_display_name", ""),
            "secondary_default_project":   qs.value("secondary_default_project", ""),
            "secondary_default_board":     qs.value("secondary_default_board", ""),
            "secondary_filter_projects":   qs.value("secondary_filter_projects", ""),
            "secondary_filter_boards":     qs.value("secondary_filter_boards", ""),
            "primary_url":                   qs.value("primary_url", ""),
            "primary_token":                 self._load_token("primary", qs.value("primary_token", "")),
            "primary_token_expiry":          qs.value("primary_token_expiry", ""),
            "primary_display_name":          qs.value("primary_display_name", ""),
            "primary_default_project":       qs.value("primary_default_project", ""),
            "primary_default_board":         qs.value("primary_default_board", ""),
            "primary_filter_projects":       qs.value("primary_filter_projects", ""),
            "primary_filter_boards":         qs.value("primary_filter_boards", ""),
        }

    def _check_token_expiry(self):
        warnings = []
        for instance, key in [("Secondary", "secondary_token_expiry"), ("Primary", "primary_token_expiry")]:
            expiry_str = self._settings.get(key, "")
            if not expiry_str:
                continue
            try:
                expiry    = date.fromisoformat(expiry_str)
                days_left = (expiry - date.today()).days
                if days_left < 0:
                    warnings.append(f"⚠  {instance} token has EXPIRED — please regenerate it.")
                elif days_left <= 14:
                    warnings.append(f"⚠  {instance} token expires in {days_left} day(s).")
            except ValueError:
                pass
        if warnings:
            msg = "  |  ".join(warnings)
            self._status(msg)
            self.expiry_banner_lbl.setText(msg)
            self.expiry_banner.setVisible(True)
        else:
            self.expiry_banner.setVisible(False)

    # ── Settings ──────────────────────────────────────────────────────────────
    def _cancel_workers(self):
        for w in list(self._workers):
            try:
                w.result.disconnect()
                w.error.disconnect()
            except Exception:
                pass
            w.quit()
            w.wait()
        self._workers.clear()

    def _open_settings(self):
        dlg = SettingsDialog(self._settings, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._cancel_workers()
            self._settings = dlg.get_settings()
            mode = self._settings.get("mode", JiraClient.MODE_SECONDARY)
            self._client = JiraClient(
                self._settings["url"],
                self._settings["token"],
                mode
            )
            mode_label = self._instance_label(mode)
            self.edit_panel._sp_field = self._client.story_point_field_id
            self.edit_panel._fl_field = self._client.feature_link_field_id
            self.edit_panel._base_url = self._client.base_url
            self._sp_field = self._client.story_point_field_id
            self.mode_indicator.setText(f"◈  {mode_label}")
            self.refresh_btn.setEnabled(True)
            self.switch_instance_btn.setEnabled(True)
            self._save_settings()
            self._check_token_expiry()
            self._load_projects()

    # ── Switch instance ───────────────────────────────────────────────────────
    def _switch_instance(self):
        if not self._settings:
            return
        current_mode = self._settings.get("mode", JiraClient.MODE_SECONDARY)
        new_mode = JiraClient.MODE_PRIMARY if current_mode == JiraClient.MODE_SECONDARY else JiraClient.MODE_SECONDARY

        new_url   = self._settings.get("primary_url")   if new_mode == JiraClient.MODE_PRIMARY else self._settings.get("secondary_url")
        new_token = self._settings.get("primary_token") if new_mode == JiraClient.MODE_PRIMARY else self._settings.get("secondary_token")

        if not new_url or not new_token:
            QMessageBox.warning(
                self, "Instance Not Configured",
                f"No credentials saved for {new_mode}.\nOpen ⚙ Configure to set them up."
            )
            return

        self._cancel_workers()
        self._settings["mode"]  = new_mode
        self._settings["url"]   = new_url
        self._settings["token"] = new_token
        self._client = JiraClient(new_url, new_token, new_mode)
        self.edit_panel._sp_field = self._client.story_point_field_id
        self.edit_panel._fl_field = self._client.feature_link_field_id
        self.edit_panel._base_url = self._client.base_url
        self._sp_field = self._client.story_point_field_id

        mode_label = self._instance_label(new_mode)
        self.mode_indicator.setText(f"◈  {mode_label}")
        self._save_settings()
        self._check_token_expiry()
        self._status(f"Switched to {mode_label} — reloading projects…")
        self._clear_sprint_view()
        self._load_projects()

    # ── Loading helpers ───────────────────────────────────────────────────────
    def _instance_label(self, mode: str) -> str:
        """Return the user-set display name for a mode, falling back to PRIMARY/SECONDARY."""
        key = "primary_display_name" if mode == JiraClient.MODE_PRIMARY else "secondary_display_name"
        return self._settings.get(key, "").strip() or (
            "PRIMARY" if mode == JiraClient.MODE_PRIMARY else "SECONDARY"
        )

    def _busy(self, on: bool):
        self.progress.setVisible(on)

    def _status(self, msg: str):
        self.status_bar.showMessage(msg)

    _MAX_WORKERS = 5

    @staticmethod
    def _error_dialog(parent, title: str, message: str, retry_fn=None):
        """Show an error dialog with an optional Retry button."""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        retry_btn = msg.addButton("↩  Retry", QMessageBox.ButtonRole.AcceptRole) if retry_fn else None
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()
        if retry_fn and msg.clickedButton() == retry_btn:
            retry_fn()

    def _spawn(self, fn, *args, on_result=None, on_error=None, retry_fn=None):
        active = sum(1 for w in self._workers if w.isRunning())
        if active >= self._MAX_WORKERS:
            self._status(f"⚠ Too many background tasks in flight ({active}); please wait.")
            return None
        w = Worker(fn, *args)
        if on_result:
            w.result.connect(on_result)
        if on_error:
            w.error.connect(on_error)
        else:
            def _default_err(e, _retry=retry_fn):
                self._busy(False)
                self._status(f"Error: {e}")
                self._error_dialog(self, "Error", e, retry_fn=_retry)
            w.error.connect(_default_err)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()
        return w

    # ── User cache ────────────────────────────────────────────────────────────
    def _refresh_users_cache(self, on_done=None):
        """Fetch the full user list in the background and cache it."""
        def _on_result(members):
            self._users_cache = sorted(members, key=lambda m: m.get("displayName", "").lower())
            self.edit_panel.set_members(self._users_cache)
            if on_done:
                on_done(self._users_cache)

        self._spawn(
            self._client.search_users, "",
            on_result=_on_result,
            on_error=lambda e: self._status("⚠ Could not load assignees (access restricted)"),
        )

    def _load_projects(self):
        self._busy(True)
        self._status("Loading projects…")
        self._spawn(
            self._client.get_projects,
            on_result=self._on_projects_loaded,
        )

    def _on_projects_loaded(self, projects):
        self._busy(False)
        mode = self._settings.get("mode", JiraClient.MODE_SECONDARY).lower()

        raw_filter = self._settings.get(f"{mode}_filter_projects", "").strip()
        filter_terms = [t.strip().lower() for t in raw_filter.split(",") if t.strip()] if raw_filter else []

        if filter_terms:
            filtered = [
                p for p in projects
                if any(term in p["key"].lower() or term in p["name"].lower() for term in filter_terms)
            ]
            if not filtered:
                self._status(f"⚠ Project filter '{raw_filter}' matched no projects — showing all {len(projects)}.")
                filtered = projects
            else:
                self._status(f"Loaded {len(projects)} projects, filtered to {len(filtered)}.")
        else:
            filtered = projects
            self._status(f"Loaded {len(projects)} projects.")

        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        for p in filtered:
            self.project_combo.addItem(f"{p['key']} — {p['name']}", p["key"])
        default_key = self._settings.get(f"{mode}_default_project", "").lower()
        if default_key:
            for i in range(self.project_combo.count()):
                key_match  = default_key in self.project_combo.itemData(i).lower()
                name_match = default_key in self.project_combo.itemText(i).lower()
                if key_match or name_match:
                    self.project_combo.setCurrentIndex(i)
                    break
        self.project_combo.blockSignals(False)
        self.project_combo.setEnabled(True)
        self.board_combo.setEnabled(True)
        self.sprint_combo.setEnabled(True)
        self.load_btn.setEnabled(True)
        if filtered:
            self._on_project_changed()

    # ── Named error handlers (extracted from lambdas) ─────────────────────────
    def _on_boards_load_error(self, key: str, e: str):
        self._status(f"⚠ Could not load boards for {key} (access restricted)")

    def _on_issue_types_load_error(self, key: str, e: str):
        self._status(f"⚠ Could not load issue types for {key} (access restricted)")

    def _on_project_changed(self):
        key = self.project_combo.currentData()
        if not key or not self._client:
            return
        self._clear_sprint_view()
        self._busy(True)
        self._status(f"Loading boards for {key}…")
        self._spawn(
            self._client.get_boards, key,
            on_result=self._on_boards_loaded,
            on_error=lambda e: self._on_boards_load_error(key, e),
        )
        self._spawn(
            self._client.get_issue_types, key,
            on_result=lambda types: (
                self.edit_panel.set_issue_types(types),
                self._populate_quick_add_types(types),
            ),
            on_error=lambda e: self._on_issue_types_load_error(key, e),
        )
        self._refresh_users_cache()

    def _on_boards_loaded(self, boards):
        self._busy(False)
        mode = self._settings.get("mode", JiraClient.MODE_SECONDARY).lower()

        raw_filter = self._settings.get(f"{mode}_filter_boards", "").strip()
        filter_terms = [t.strip().lower() for t in raw_filter.split(",") if t.strip()] if raw_filter else []

        if filter_terms:
            filtered = [
                b for b in boards
                if any(term in b["name"].lower() for term in filter_terms)
            ]
            if not filtered:
                self._status(f"⚠ Board filter '{raw_filter}' matched no boards — showing all {len(boards)}.")
                filtered = boards
            else:
                self._status(f"Loaded {len(boards)} boards, filtered to {len(filtered)}.")
        else:
            filtered = boards
            self._status(f"Loaded {len(boards)} boards.")

        self._boards = filtered
        self.board_combo.blockSignals(True)
        self.board_combo.clear()
        for b in filtered:
            self.board_combo.addItem(b["name"], b["id"])
        default_board = self._settings.get(f"{mode}_default_board", "").lower()
        if default_board:
            for i in range(self.board_combo.count()):
                if default_board in self.board_combo.itemText(i).lower():
                    self.board_combo.setCurrentIndex(i)
                    break
        self.board_combo.blockSignals(False)
        if filtered:
            self._on_board_changed()
        # Keep backlog widget combos in sync
        self.backlog_widget.sync_combos(self.project_combo, self.board_combo)

    def _on_board_changed(self):
        bid = self.board_combo.currentData()
        if bid is None or not self._client:
            return

        self.sprint_combo.blockSignals(True)
        self.sprint_combo.clear()
        self.sprint_combo.blockSignals(False)

        self.table.setRowCount(0)
        self.story_count_lbl.setText("No stories loaded")
        self._issues = []

        self._busy(True)
        self._status("Loading sprints…")
        self._spawn(
            self._client.get_sprints, bid,
            on_result=self._on_sprints_loaded,
        )

    def _on_sprints_loaded(self, sprints):
        self._busy(False)
        self._sprints = sprints
        self.sprint_combo.clear()
        for s in sprints:
            state = s.get("state", "")
            label = f"[{state.upper()}] {s['name']}"
            self.sprint_combo.addItem(label, s["id"])
            if state.lower() == "active":
                idx = self.sprint_combo.count() - 1
                self.sprint_combo.setItemData(idx, QColor(ACCENT_CYAN), Qt.ItemDataRole.ForegroundRole)
                font = self.sprint_combo.font()
                font.setBold(True)
                self.sprint_combo.setItemData(idx, font, Qt.ItemDataRole.FontRole)
        self._status(f"Loaded {len(sprints)} sprints.")
        self.compare_combo.clear()
        self.compare_combo.addItem("— select sprint —", None)
        for s in sprints:
            self.compare_combo.addItem(f"[{s.get('state','').upper()}] {s['name']}", s['id'])
        self.compare_combo.setEnabled(True)
        self.compare_btn.setEnabled(True)
        self.sprint_mgr_btn.setEnabled(True)
        # Sync Reports tab sprint combo and sub-tab sprint selectors
        self._rpt_sprint_combo.blockSignals(True)
        self._rpt_sprint_combo.clear()
        self._srt_sprint_sel.blockSignals(True)
        self._srt_sprint_sel.clear()
        self._prt_sprint_sel.blockSignals(True)
        self._prt_sprint_sel.clear()
        for s in sprints:
            state = s.get("state", "")
            label = f"[{state.upper()}] {s['name']}"
            sid   = s["id"]
            self._rpt_sprint_combo.addItem(label, sid)
            self._srt_sprint_sel.addItem(label, sid)
            self._prt_sprint_sel.addItem(label, sid)
        # Pre-select active sprint in all three
        for combo in (self._rpt_sprint_combo, self._srt_sprint_sel, self._prt_sprint_sel):
            for i in range(combo.count()):
                if "[ACTIVE]" in combo.itemText(i):
                    combo.setCurrentIndex(i)
                    break
        self._rpt_sprint_combo.blockSignals(False)
        self._srt_sprint_sel.blockSignals(False)
        self._prt_sprint_sel.blockSignals(False)
        self._rpt_sprint_combo.setEnabled(True)
        self._srt_sprint_sel.setEnabled(True)
        self._prt_sprint_sel.setEnabled(True)
        self._srt_gen_btn.setEnabled(True)
        self._prt_gen_btn.setEnabled(True)
        bid = self.board_combo.currentData()
        if bid:
            last_sid = QSettings("SprintMate","SprintMate").value(f"last_sprint_{bid}")
            if last_sid:
                for i in range(self.sprint_combo.count()):
                    if str(self.sprint_combo.itemData(i)) == str(last_sid):
                        self.sprint_combo.setCurrentIndex(i); break
        self.edit_panel.set_sprints(sprints)
        self.backlog_widget.set_sprints(sprints)
        # Keep Kanban toolbar in sync
        self.kanban_widget.sync_combos(
            self.project_combo, self.board_combo, self.sprint_combo
        )

    def _load_sprint_issues(self, reselect_key: str = None):
        bid = self.board_combo.currentData()
        sid = self.sprint_combo.currentData()
        if bid is None or sid is None or not self._client:
            return
        if self.edit_panel.save_btn.isEnabled():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes in the edit panel.\n"
                "Loading stories will discard them. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._reselect_key = reselect_key or self.edit_panel.current_key
        bid_save = self.board_combo.currentData()
        sid_save = self.sprint_combo.currentData()
        if bid_save and sid_save:
            QSettings("SprintMate", "SprintMate").setValue(f"last_sprint_{bid_save}", sid_save)
        mode = self._settings.get("mode", JiraClient.MODE_SECONDARY)
        mode_label = self._instance_label(mode)
        sprint_label = self.sprint_combo.currentText()
        self._busy(True)
        self._status(f"Loading stories from {mode_label} — {sprint_label}…")
        self._spawn(
            self._client.get_sprint_issues, bid, sid,
            on_result=self._on_issues_loaded,
            on_error=lambda e: (
                self._busy(False),
                self._status("✗ Failed to load stories."),
                QMessageBox.critical(self, "Load Failed", str(e)),
            ),
        )

    def _on_issues_loaded(self, issues):
        self._busy(False)
        self._issues = issues
        self._populate_table(issues)
        self._status(f"Loaded {len(issues)} stories.")
        self.story_count_lbl.setText(f"{len(issues)} stories")
        self._update_velocity_bar()
        self._populate_assignee_filter()
        self._populate_assignee_filter()
        # Update persistent sprint label
        project = self.project_combo.currentText().split("—")[0].strip()
        board   = self.board_combo.currentText()
        sprint  = self.sprint_combo.currentText()
        self.sprint_lbl.setText(f"{project}  ◈  {board}  ◈  {sprint}")
        self.new_story_btn.setEnabled(True)
        self.bulk_create_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self._rpt_gen_btn.setEnabled(True)
        self._rpt_people_btn.setEnabled(True)
        self.archive_btn.setEnabled(True)
        self.bulk_edit_btn.setEnabled(True)
        self.quick_add_edit.setEnabled(True)
        # Sync backlog combos with current project/board selection
        self.backlog_widget.sync_combos(self.project_combo, self.board_combo)
        self._rpt_gen_btn.setEnabled(True)
        self._rpt_people_btn.setEnabled(True)
        self._rpt_velocity_btn.setEnabled(True)
        self._rpt_burndown_btn.setEnabled(True)
        self._rpt_save_btn.setEnabled(False)
        # Populate people list for People Report sub-tab
        self._prt_people_list.clear()
        seen = set()
        for iss in issues:
            aobj = (iss.get("fields") or {}).get("assignee") or {}
            name    = aobj.get("name") or aobj.get("accountId") or ""
            display = aobj.get("displayName") or name
            if name and name not in seen:
                seen.add(name)
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, name)
                self._prt_people_list.addItem(item)
        # Select all by default
        self._prt_people_list.selectAll()  # enabled after first generation
        # Update Kanban board title with active sprint name
        sprint_name = self.sprint_combo.currentText()
        self.kanban_widget.set_sprint_name(sprint_name)
        self.kanban_widget.set_base_url(self.edit_panel._base_url)
        self.backlog_widget.set_base_url(self.edit_panel._base_url)
        # Update tab label to show sprint name
        self.tabs.setTabText(1, f"⊞  {sprint_name}" if sprint_name else "⊞  ACTIVE SPRINT")
        # Refresh Kanban only if already visible (avoid re-render on hidden tab)
        if self.tabs.currentIndex() == 1:
            self.kanban_widget.populate(issues, self._sp_field, force=True)
        reselect = self._reselect_key
        if reselect:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text() == reselect:
                    self.table.selectRow(row)
                    self.table.scrollToItem(item)
                    break
            self._reselect_key = None

    def _populate_assignee_filter(self):
        self.assignee_filter_combo.blockSignals(True)
        self.assignee_filter_combo.clear()
        self.assignee_filter_combo.addItem("All assignees", None)
        seen = set()
        for iss in self._issues:
            a = (iss.get("fields", {}).get("assignee") or {})
            name = a.get("displayName") or a.get("name") or ""
            if name and name not in seen:
                seen.add(name)
                self.assignee_filter_combo.addItem(name, name)
        self.assignee_filter_combo.blockSignals(False)
        self.assignee_filter_combo.setEnabled(True)

    def _apply_assignee_filter(self):
        selected = self.assignee_filter_combo.currentData()
        term = self.search_edit.text().lower()
        for row in range(self.table.rowCount()):
            a_item = self.table.item(row, COL_ASSIGNEE)
            a_match = selected is None or (a_item and a_item.text() == selected)
            t_match = not term or any(
                term in (self.table.item(row, c).text().lower() if self.table.item(row, c) else "")
                for c in range(self.table.columnCount()))
            self.table.setRowHidden(row, not (a_match and t_match))

    def _update_velocity_bar(self):
        if not self._issues:
            self.velocity_lbl.setText("")
            self._progress_bar.setVisible(False)
            return
        total_pts = done_pts = in_prog = done_cnt = 0
        sp = self._sp_field
        for iss in self._issues:
            f = iss.get("fields", {})
            status = (f.get("status") or {}).get("name", "")
            pts_raw = next((f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS) if f.get(k) is not None), None)
            try:
                pts = int(float(pts_raw)) if pts_raw is not None else 0
            except (TypeError, ValueError):
                pts = 0
            total_pts += pts
            if status == "Done":
                done_pts += pts; done_cnt += 1
            elif status == "In Progress":
                in_prog += 1
        pct = round(done_pts / total_pts * 100) if total_pts else 0
        self.velocity_lbl.setText(
            f"{total_pts} pts total  ·  {in_prog} in progress  ·  {done_cnt} done ({done_pts} pts)"
        )
        self._progress_bar.setValue(pct)
        # Colour the bar: green when done, amber when mid-sprint, red when behind
        if pct >= 80:
            chunk_colour = ACCENT_GREEN
        elif pct >= 40:
            chunk_colour = "#E3B341"
        else:
            chunk_colour = ACCENT_ORANGE
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {BORDER};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: {chunk_colour};
                border-radius: 2px;
            }}
        """)
        self._progress_bar.setToolTip(
            f"{done_pts} of {total_pts} pts done ({pct}%)  ·  "
            f"{done_cnt} of {len(self._issues)} stories done"
        )
        self._progress_bar.setVisible(True)

    def _mark_unsaved_row(self):
        """Add a dot indicator to the KEY cell of the currently edited row."""
        row = self.table.currentRow()
        if row < 0:
            return
        ki = self.table.item(row, COL_KEY)
        if ki and not ki.text().endswith(" ●"):
            ki.setText(ki.text() + " ●")
            ki.setForeground(QColor("#E3B341"))
        self._unsaved_row = row

    def _show_recent_menu(self):
        """Show a popup menu of recently viewed stories."""
        menu = QMenu(self)
        if not self._recent_keys:
            act = menu.addAction("No recent stories")
            act.setEnabled(False)
        else:
            for key in self._recent_keys:
                issue = next((i for i in self._issues if i.get("key") == key), None)
                summary = ""
                if issue:
                    summary = (issue.get("fields", {}).get("summary", "") or "")[:50]
                label = f"{key}  —  {summary}" if summary else key
                act = menu.addAction(label)
                act.setData(key)
        menu.addSeparator()
        clear = menu.addAction("✕  Clear history")
        chosen = menu.exec(self._recent_btn.mapToGlobal(
            self._recent_btn.rect().bottomLeft()
        ))
        if chosen and chosen.data():
            key = chosen.data()
            for row in range(self.table.rowCount()):
                item = self.table.item(row, COL_KEY)
                if item and item.text().replace(" ●", "") == key:
                    self.table.selectRow(row)
                    self.table.scrollToItem(item)
                    break
        elif chosen == clear:
            self._recent_keys.clear()

    def _open_bulk_edit(self):
        """Open a dialog to bulk-edit assignee, priority, or points for selected rows."""
        selected_rows = list({idx.row() for idx in self.table.selectedIndexes()})
        if not selected_rows:
            QMessageBox.information(self, "Bulk Edit",
                "Select one or more stories in the table first.")
            return
        keys = []
        for r in selected_rows:
            ki = self.table.item(r, COL_KEY)
            if ki:
                keys.append(ki.text().replace(" ●", ""))
        if not keys:
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Bulk Edit — {len(keys)} stories")
        dlg.setMinimumWidth(380)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(10)

        heading = QLabel(f"◈  BULK EDIT  —  {len(keys)} STORIES")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        keys_lbl = QLabel(", ".join(keys[:8]) + ("…" if len(keys) > 8 else ""))
        keys_lbl.setObjectName("dim")
        keys_lbl.setWordWrap(True)
        layout.addWidget(keys_lbl)

        form = QFormLayout()
        form.setSpacing(8)

        assignee_cb = QComboBox()
        assignee_cb.addItem("— No change —", None)
        assignee_cb.addItem("Unassigned", "UNASSIGNED")
        for m in self._users_cache:
            uid  = m.get("name") or m.get("accountId", "")
            name = m.get("displayName", uid)
            assignee_cb.addItem(name, uid)
        form.addRow("Assignee:", assignee_cb)

        priority_cb = QComboBox()
        priority_cb.addItem("— No change —", None)
        for p in PRIORITIES:
            priority_cb.addItem(p, p)
        form.addRow("Priority:", priority_cb)

        points_cb = QComboBox()
        points_cb.addItem("— No change —", None)
        for v in FIBONACCI:
            points_cb.addItem(str(v), v)
        form.addRow("Story Points:", points_cb)

        layout.addLayout(form)

        note = QLabel("Only fields set above will be changed. "
                      "Fields left at '— No change —' are untouched.")
        note.setObjectName("dim")
        note.setWordWrap(True)
        layout.addWidget(note)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Apply to All")
        btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("save_btn")
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        assignee_val = assignee_cb.currentData()
        priority_val = priority_cb.currentData()
        points_val   = points_cb.currentData()

        if assignee_val is None and priority_val is None and points_val is None:
            self._status("Bulk edit: nothing to change.")
            return

        fields_payload: dict = {}
        if assignee_val is not None:
            fields_payload["assignee"] = (
                None if assignee_val == "UNASSIGNED"
                else {"name": assignee_val}
            )
        if priority_val is not None:
            fields_payload["priority"] = {"name": priority_val}
        if points_val is not None:
            fields_payload[self._sp_field] = points_val

        n = len(keys)
        self._busy(True)
        self._status(f"Bulk editing {n} stories…")

        def _do():
            errors = []
            for key in keys:
                try:
                    self._client.update_issue(key, fields_payload)
                except Exception as e:
                    errors.append(f"{key}: {e}")
            return errors

        def _on_done(errors):
            self._busy(False)
            if errors:
                self._status(f"⚠ Bulk edit: {len(errors)} error(s).")
                QMessageBox.warning(self, "Bulk Edit",
                    f"{n - len(errors)} updated, {len(errors)} failed:\n"
                    + "\n".join(errors[:5]))
            else:
                self._status(f"✓ Bulk edit applied to {n} stories.")
            self._load_sprint_issues(reselect_key=keys[-1])

        self._spawn(_do,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status("✗ Bulk edit failed."),
                QMessageBox.critical(self, "Bulk Edit Failed", str(e)),
            ))

    def _show_shortcut_dialog(self):
        """Show the keyboard shortcut reference card."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts")
        dlg.setMinimumWidth(500)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(8)

        heading = QLabel("◈  KEYBOARD SHORTCUTS")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        SHORTCUTS = [
            ("Global", [
                ("Ctrl+L",       "Load Stories"),
                ("Ctrl+N",       "New Story"),
                ("Ctrl+S",       "Save Changes"),
                ("Ctrl+I",       "Import Comments"),
                ("Ctrl+E",       "Export Stories"),
                ("Ctrl+F",       "Focus filter box"),
                ("Ctrl+C",       "Copy selected row (comma-separated)"),
                ("Ctrl+Shift+C", "Copy full issue as CSV row"),
                ("Ctrl+Shift+M", "Copy row as Markdown"),
                ("Alt+1",        "Switch to Stories view"),
                ("Alt+2",        "Switch to Active Sprint board"),
                ("Alt+3",        "Switch to Backlog view"),
                ("?",            "Show this shortcut reference"),
            ]),
            ("Table (when focused)", [
                ("N",       "New Story"),
                ("R",       "Refresh sprint"),
                ("S",       "Save changes"),
                ("Escape",  "Clear selection"),
                ("Delete",  "Quick-archive selected story"),
                ("↑ / ↓",   "Navigate rows"),
            ]),
            ("Inline editing (double-click cell)", [
                ("PTS",      "Open Fibonacci story-points picker"),
                ("ASSIGNEE", "Open team-member picker"),
                ("STATUS",   "Open available transitions picker"),
                ("DUE DATE", "Open calendar date picker"),
            ]),
        ]

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(16)
        cl.setContentsMargins(0, 0, 8, 0)

        for section, items in SHORTCUTS:
            sec_lbl = QLabel(section.upper())
            sec_lbl.setStyleSheet(
                f"color: {ACCENT_CYAN}; font-size: 11px; font-weight: bold; "
                f"letter-spacing: 1px; margin-top: 4px;"
            )
            cl.addWidget(sec_lbl)
            for key, desc in items:
                row_w = QWidget()
                row_l = QHBoxLayout(row_w)
                row_l.setContentsMargins(0, 0, 0, 0)
                key_lbl = QLabel(key)
                key_lbl.setStyleSheet(
                    f"background: {CARD_BG}; color: {TEXT_PRI}; "
                    f"padding: 2px 8px; border-radius: 4px; "
                    f"font-family: monospace; font-size: 12px; "
                    f"border: 1px solid {BORDER}; min-width: 130px;"
                )
                key_lbl.setFixedWidth(160)
                desc_lbl = QLabel(desc)
                desc_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
                row_l.addWidget(key_lbl)
                row_l.addWidget(desc_lbl, 1)
                cl.addWidget(row_w)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.resize(500, 560)
        dlg.exec()

    def _check_quick_add_duplicate(self, summary: str) -> bool:
        """Return True (safe to create) or False (user cancelled) after checking for
        similar stories in the current sprint.

        Matching strategy:
        - Case-insensitive, punctuation-stripped word comparison.
        - Stop words (articles, prepositions, conjunctions) are excluded so that
          "Add a button to the form" and "Add a field to the form" don't false-positive.
        - Minimum 3 meaningful words required before checking (avoids false positives
          on very short summaries like "Fix bug").
        - Threshold: >65% of meaningful words overlap with an existing story.
        """
        _STOP_WORDS = {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "as", "is", "was", "are",
            "be", "been", "it", "its", "this", "that", "we", "i", "my",
        }

        def _words(text: str) -> set:
            cleaned = re.sub(r"[^\w\s]", "", text.lower())
            return {w for w in cleaned.split() if w not in _STOP_WORDS}

        tw = _words(summary)
        if len(tw) < 3:
            return True   # too short to check reliably — skip

        matches = []
        for iss in self._issues:
            existing = (iss.get("fields", {}).get("summary") or "")
            ew = _words(existing)
            if not ew:
                continue
            overlap = len(tw & ew) / max(len(tw), len(ew))
            if overlap > 0.65:
                matches.append(f"{iss['key']}  —  {existing[:70]}")

        if not matches:
            return True

        reply = QMessageBox.question(
            self, "Possible Duplicate",
            "Similar stories already exist in this sprint:\n\n"
            + "\n".join(matches[:5])
            + "\n\nCreate anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _apply_default_columns(self):
        for col, _ in COLS_TOGGLABLE:
            self.table.setColumnHidden(col, col not in COLS_DEFAULT_VISIBLE)

    def _show_column_menu(self, pos):
        menu = QMenu(self)
        for col, label in COLS_TOGGLABLE:
            action = menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(not self.table.isColumnHidden(col))
            action.setData(col)
        chosen = menu.exec(self.table.horizontalHeader().mapToGlobal(pos))
        if chosen:
            col = chosen.data()
            self.table.setColumnHidden(col, not self.table.isColumnHidden(col))
            # Persist column prefs for current board
            board_id = str(self.board_combo.currentData() or "")
            if board_id:
                visible = {c for c, _ in COLS_TOGGLABLE
                           if not self.table.isColumnHidden(c)}
                self._column_prefs[board_id] = visible

    def _populate_table(self, issues):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        # Restore saved column prefs for this board, else apply defaults
        board_id = str(self.board_combo.currentData() or "")
        if board_id and board_id in self._column_prefs:
            visible = self._column_prefs[board_id]
            for col, _ in COLS_TOGGLABLE:
                self.table.setColumnHidden(col, col not in visible)
        else:
            self._apply_default_columns()
        self.search_edit.blockSignals(True)
        self.search_edit.clear()
        self.search_edit.blockSignals(False)
        self.assignee_filter_combo.blockSignals(True)
        self.assignee_filter_combo.clear()
        self.assignee_filter_combo.blockSignals(False)

        sp_field = self._sp_field
        fl_field = self.edit_panel._fl_field

        for issue in issues:
            f = issue.get("fields", {})
            row = self.table.rowCount()
            self.table.insertRow(row)

            key_item = QTableWidgetItem(issue["key"])
            key_item.setForeground(QColor(ACCENT_CYAN))
            # Rich tooltip — description excerpt + latest comment
            desc = ""
            raw_desc = f.get("description") or ""
            if isinstance(raw_desc, dict):
                # ADF — flatten text nodes
                def _adf_text(node):
                    if isinstance(node, dict):
                        if node.get("type") == "text":
                            return node.get("text", "")
                        return "".join(_adf_text(c) for c in node.get("content", []))
                    return ""
                desc = _adf_text(raw_desc)
            elif isinstance(raw_desc, str):
                desc = raw_desc
            desc_preview = (desc[:140] + "…") if len(desc) > 140 else desc
            comments = (f.get("comment") or {}).get("comments", [])
            last_comment = ""
            if comments:
                c = comments[-1]
                author = (c.get("author") or {}).get("displayName", "?")
                body = c.get("body", "")
                if isinstance(body, dict):
                    def _adf_text2(n):
                        if isinstance(n, dict):
                            if n.get("type") == "text": return n.get("text","")
                            return "".join(_adf_text2(x) for x in n.get("content",[]))
                        return ""
                    body = _adf_text2(body)
                last_comment = f"\n💬 {author}: {str(body)[:100]}"
            tooltip = f"{issue['key']}"
            if desc_preview:
                tooltip += f"\n{desc_preview}"
            if last_comment:
                tooltip += last_comment
            key_item.setToolTip(tooltip)
            self.table.setItem(row, COL_KEY, key_item)

            sum_item = QTableWidgetItem(f.get("summary", ""))
            sum_item.setToolTip(tooltip)
            self.table.setItem(row, COL_SUMMARY, sum_item)

            assignee = f.get("assignee")
            aname = assignee.get("displayName", "Unassigned") if assignee else "—"
            a_item = QTableWidgetItem(aname)
            a_item.setForeground(QColor(TEXT_SEC))
            self.table.setItem(row, COL_ASSIGNEE, a_item)

            status = f.get("status", {}).get("name", "")
            s_item = QTableWidgetItem(status)
            s_item.setForeground(QColor(STATUS_COLORS.get(status, TEXT_SEC)))
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, COL_STATUS, s_item)

            due = f.get("duedate", "") or ""
            due_item = QTableWidgetItem(due[:10] if due else "—")
            due_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if due:
                try:
                    _dl = (date.fromisoformat(due[:10]) - date.today()).days
                    if _dl < 0:
                        due_item.setForeground(QColor(ACCENT_ORANGE))
                        due_item.setToolTip(f"Overdue by {abs(_dl)} day(s)")
                    elif _dl <= 3:
                        due_item.setForeground(QColor("#E3B341"))
                        due_item.setToolTip(f"Due in {_dl} day(s)")
                except ValueError:
                    pass
            self.table.setItem(row, COL_DUE_DATE, due_item)

            pts = next((f.get(k) for k in ([sp_field] + JiraClient._SP_FALLBACKS) if f.get(k) is not None), None) or ""
            try:
                pts_val = int(float(pts)) if pts else None
            except (TypeError, ValueError):
                pts_val = None
            pts_item = QTableWidgetItem()
            pts_item.setData(Qt.ItemDataRole.DisplayRole, pts_val if pts_val is not None else "—")
            pts_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, COL_STORY_PTS, pts_item)

            priority = (f.get("priority") or {}).get("name", "—")
            pri_item = QTableWidgetItem(priority)
            pri_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, COL_PRIORITY, pri_item)

            itype = (f.get("issuetype") or {}).get("name", "—")
            self.table.setItem(row, COL_ISSUE_TYPE, QTableWidgetItem(itype))

            fl = f.get(fl_field, "") or ""
            self.table.setItem(row, COL_FEATURE_LNK, QTableWidgetItem(str(fl)))

            self.table.setRowHeight(row, 40)

        self.table.setSortingEnabled(True)

    def _filter_table(self, text: str):
        term = text.lower()
        selected_assignee = self.assignee_filter_combo.currentData()
        highlight_bg = QColor(ACCENT_BLUE).darker(180)
        for row in range(self.table.rowCount()):
            row_matches = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if not item: continue
                cell_text = item.text().lower()
                if term and term in cell_text:
                    row_matches = True
                    item.setBackground(highlight_bg)
                else:
                    item.setBackground(QColor(0, 0, 0, 0))
            text_hidden = bool(term) and not row_matches
            a_item = self.table.item(row, COL_ASSIGNEE)
            a_hidden = selected_assignee is not None and (not a_item or a_item.text() != selected_assignee)
            self.table.setRowHidden(row, text_hidden or a_hidden)

    def _on_story_selected(self):
        rows = self.table.selectedItems()
        if not rows:
            return
        row = self.table.currentRow()
        key_item = self.table.item(row, 0)
        if not key_item:
            return
        key = key_item.text()
        issue = next((i for i in self._issues if i["key"] == key), None)
        if not issue:
            return

        # Clear unsaved indicator from previously selected row
        if self._unsaved_row is not None:
            ki = self.table.item(self._unsaved_row, COL_KEY)
            if ki:
                text = ki.text()
                if text.endswith(" ●"):
                    ki.setText(text[:-2])
            self._unsaved_row = None

        # Track recently viewed (MRU, max 10, no duplicates)
        if key in self._recent_keys:
            self._recent_keys.remove(key)
        self._recent_keys.insert(0, key)
        self._recent_keys = self._recent_keys[:10]

        self.edit_panel.load_issue(issue)
        self._rank_up_btn.setEnabled(True)
        self._rank_down_btn.setEnabled(True)
        # Re-wire attach button to current issue key
        try:
            self.edit_panel.attach_btn.clicked.disconnect()
        except Exception:
            pass
        self.edit_panel.attach_btn.clicked.connect(
            lambda: self._attach_file_to_issue(key)
        )
        # Re-wire clone button
        try:
            self.edit_panel.clone_btn.clicked.disconnect()
        except Exception:
            pass
        self.edit_panel.clone_btn.clicked.connect(
            lambda: self._clone_issue(issue)
        )
        # Re-wire edit/delete comment buttons to current issue
        try:
            self.edit_panel._edit_comment_btn.clicked.disconnect()
        except Exception:
            pass
        try:
            self.edit_panel._delete_comment_btn.clicked.disconnect()
        except Exception:
            pass
        self.edit_panel._edit_comment_btn.clicked.connect(
            lambda: self._edit_comment(key)
        )
        self.edit_panel._delete_comment_btn.clicked.connect(
            lambda: self._delete_comment(key)
        )
        self._spawn(
            self._client.get_issue_transitions, key,
            on_result=self.edit_panel.set_transitions,
        )
        # Use cached user list; fetch only if cache is empty
        if self._users_cache:
            self.edit_panel.set_members(self._users_cache)
        else:
            self._refresh_users_cache()

    # ── Export ────────────────────────────────────────────────────────────────
    def _build_export_filename(self) -> str:
        def slugify(text: str) -> str:
            text = re.sub(r'[^\w\s-]', '', text)
            text = re.sub(r'[\s_]+', '-', text.strip())
            return text

        project  = slugify(self.project_combo.currentText().split("—")[0].strip())
        board    = slugify(self.board_combo.currentText())
        sprint   = slugify(self.sprint_combo.currentText())
        today    = date.today().strftime("%Y-%m-%d")
        return f"{project}-{board}-{sprint}-{today}.csv"

    def _do_export_csv(self, issues: list, path: str):
        sp_field = self._sp_field
        fl_field = self.edit_panel._fl_field

        headers = [
            "key", "summary", "assignee", "status", "issue_type",
            "priority", "story_points", "feature_link", "due_date",
            "sprint", "description", "comments",
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for issue in issues:
                key    = issue.get("key", "")
                fields = issue.get("fields") or {}

                assignee_obj = fields.get("assignee") or {}
                assignee = (assignee_obj.get("displayName") or assignee_obj.get("name") or "")

                status = (fields.get("status") or {}).get("name", "")
                issue_type = (fields.get("issuetype") or {}).get("name", "")
                priority   = (fields.get("priority") or {}).get("name", "")

                pts_raw = next((fields.get(k) for k in ([sp_field] + JiraClient._SP_FALLBACKS) if fields.get(k) is not None), None)
                try:
                    story_points = int(float(pts_raw)) if pts_raw is not None else ""
                except (TypeError, ValueError):
                    story_points = ""

                feature_link = fields.get(fl_field, "") or ""
                due_date     = fields.get("duedate", "") or ""

                sprint_name = ""
                sprint_data = fields.get("customfield_10020") or fields.get("sprint")
                if isinstance(sprint_data, list) and sprint_data:
                    sprint_name = sprint_data[-1].get("name", "")
                elif isinstance(sprint_data, dict):
                    sprint_name = sprint_data.get("name", "")

                desc = fields.get("description") or ""
                if isinstance(desc, dict):
                    desc = self.edit_panel._adf_to_text(desc)
                desc = desc.replace("\n", " ").strip()

                comments_data = (fields.get("comment") or {}).get("comments", [])
                comment_parts = []
                for c in comments_data:
                    author = ((c.get("author") or {}).get("displayName") or
                              (c.get("author") or {}).get("name") or "")
                    body = c.get("body", "")
                    if isinstance(body, dict):
                        body = self.edit_panel._adf_to_text(body)
                    body = body.replace("\n", " ").strip()
                    comment_parts.append(f"[{author}]: {body}")
                comments = " | ".join(comment_parts)

                writer.writerow({
                    "key":          key,
                    "summary":      fields.get("summary", ""),
                    "assignee":     assignee,
                    "status":       status,
                    "issue_type":   issue_type,
                    "priority":     priority,
                    "story_points": story_points,
                    "feature_link": feature_link,
                    "due_date":     due_date,
                    "sprint":       sprint_name,
                    "description":  desc,
                    "comments":     comments,
                })

    def _export_stories(self):
        if not self._issues:
            return
        msg = QMessageBox(self)
        msg.setWindowTitle("Export Stories")
        msg.setText(f"Export all {len(self._issues)} stories, or select specific ones?")
        btn_all    = msg.addButton("All",    QMessageBox.ButtonRole.YesRole)
        btn_select = msg.addButton("Select", QMessageBox.ButtonRole.NoRole)
        msg.addButton("Cancel",              QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(btn_all)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked is btn_all:
            issues_to_export = self._issues
        elif clicked is btn_select:
            dlg = ExportStoriesDialog(self._issues, self)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
            issues_to_export = dlg.get_selected_issues()
            if not issues_to_export:
                return
        else:
            return

        suggested = self._build_export_filename()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Export", suggested, "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            self._do_export_csv(issues_to_export, path)
            QMessageBox.information(
                self, "Export Complete",
                f"✓ Exported {len(issues_to_export)} stor{'ies' if len(issues_to_export) != 1 else 'y'} to:\n{path}"
            )
            self._status(f"✓ Exported {len(issues_to_export)} stories.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"✗ Could not write file:\n{e}")
            self._status("✗ Export failed.")

    def _import_comments(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Comments File", "",
            "Comment Files (*.txt *.md *.csv);;All Files (*)"
        )
        if not path:
            return
        if path.lower().endswith(".csv"):
            try:
                parsed = self._parse_comments_csv(path)
            except RuntimeError as e:
                QMessageBox.critical(self, "File Error", str(e))
                return
        else:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw = f.read()
            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Could not read file:\n{e}")
                return
            parsed = self._parse_comments_file(raw)
        if not parsed:
            QMessageBox.warning(self, "No Entries Found",
                "No valid entries found in the file.\n\n"
                "Text/Markdown format:\n"
                "  PROJECT1-123 - Task Summary - Assignee Name: Your comment here\n\n"
                "CSV format (header row required):\n"
                "  key, summary, assignee, comment")
            return

        loaded_keys = set()
        story_info  = {}
        for issue in self._issues:
            k = issue.get("key", "")
            if not k:
                continue
            f = issue.get("fields", {})
            loaded_keys.add(k)
            assignee = f.get("assignee")
            aname = assignee.get("displayName", "") if assignee else ""
            story_info[k] = (f.get("summary", ""), aname)

        other_client = None
        s = self._settings
        active_mode = s.get("mode", JiraClient.MODE_SECONDARY)
        if active_mode == JiraClient.MODE_SECONDARY and s.get("primary_url") and s.get("primary_token"):
            other_client = JiraClient(s["primary_url"], s["primary_token"], JiraClient.MODE_PRIMARY)
        elif active_mode == JiraClient.MODE_PRIMARY and s.get("secondary_url") and s.get("secondary_token"):
            other_client = JiraClient(s["secondary_url"], s["secondary_token"], JiraClient.MODE_SECONDARY)

        def _best_match(candidates, target_summary, target_assignee):
            target_summary_lc   = target_summary.lower()
            target_assignee_lc  = target_assignee.lower()
            scored = []
            for c in candidates:
                cf = c.get("fields", {})
                csum  = (cf.get("summary") or "").lower()
                cassignee = ((cf.get("assignee") or {}).get("displayName") or
                             (cf.get("assignee") or {}).get("name") or "").lower()
                score = 0
                if csum == target_summary_lc:
                    score += 2
                elif target_summary_lc in csum or csum in target_summary_lc:
                    score += 1
                if target_assignee_lc and target_assignee_lc in cassignee:
                    score += 1
                scored.append((score, c["key"]))
            scored.sort(key=lambda x: -x[0])
            return scored[0][1] if scored and scored[0][0] > 0 else None

        def _sanitise_jql(value: str) -> str:
            value = value.replace("\\", "\\\\").replace('"', '\\"')
            value = value.replace("%", "").replace("*", "").replace("?", "")
            return value

        cross_map = {}
        if other_client:
            for key, entry in parsed.items():
                paired_keys = entry.get("paired_keys") or []
                # Filter to keys that are explicitly provided and not on the active instance
                explicit = [p for p in paired_keys if p in parsed and p not in loaded_keys]
                if explicit:
                    if key in loaded_keys:
                        cross_map[key] = explicit
                    continue

                file_summary  = (entry["summary"] or "").strip()
                file_assignee = (entry["assignee"] or "").strip()
                if not file_summary:
                    continue

                safe_summary = _sanitise_jql(file_summary)
                jql = f'summary ~ "{safe_summary}"'
                if file_assignee:
                    safe_assignee = _sanitise_jql(file_assignee)
                    jql += f' AND assignee = "{safe_assignee}"'
                try:
                    matches = other_client.search_issues_jql(jql, fields="summary,assignee")
                    if not matches:
                        jql_exact = f'summary = "{safe_summary}"'
                        matches = other_client.search_issues_jql(jql_exact, fields="summary,assignee")
                except RuntimeError:
                    matches = []

                if matches:
                    best = _best_match(matches, file_summary, file_assignee)
                    if best:
                        cross_map[key] = [best]

        cross_keys = set(cross_map.keys())
        dlg = ImportCommentsDialog(parsed, loaded_keys, story_info, cross_keys, cross_map, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            to_post = dlg.get_comments()
            if to_post:
                n  = len(to_post)
                nc = sum(1 for k in to_post if cross_map.get(k))
                self._busy(True)
                self.progress.setRange(0, n)
                self.progress.setValue(0)
                self._status(f"Posting {n} comments ({nc} to both instances)…")

                def _on_progress(done, total):
                    self.progress.setValue(done)
                    self._status(f"Posting comments… {done}/{total}")

                def _on_done(result):
                    self.progress.setRange(0, 0)
                    self._busy(False)
                    posted   = result.get("posted", n)          if isinstance(result, dict) else n
                    failures = result.get("cross_failures", []) if isinstance(result, dict) else []

                    primary_failures = [f for f in failures if "(primary)" in f]
                    cross_failures   = [f for f in failures if "(primary)" not in f]
                    succeeded        = posted - len(primary_failures)

                    if not failures:
                        QMessageBox.information(
                            self, "Comments Posted",
                            f"✓ Successfully posted {succeeded} comment{'s' if succeeded != 1 else ''}."
                        )
                        self._status(f"✓ Posted {succeeded} comment{'s' if succeeded != 1 else ''} successfully.")
                    elif primary_failures and succeeded == 0:
                        detail = "\n".join(primary_failures[:10])
                        if len(primary_failures) > 10:
                            detail += f"\n… and {len(primary_failures) - 10} more."
                        QMessageBox.critical(
                            self, "Posting Failed",
                            f"✗ Failed to post all {len(primary_failures)} comment{'s' if len(primary_failures) != 1 else ''}.\n\n{detail}"
                        )
                        self._status(f"✗ All {len(primary_failures)} comments failed to post.")
                    else:
                        lines = [f"✓ Posted {succeeded} of {posted} comment{'s' if posted != 1 else ''} successfully."]
                        if primary_failures:
                            lines.append(f"\n✗ {len(primary_failures)} primary failure{'s' if len(primary_failures) != 1 else ''}:")
                            lines.extend(f"  • {f}" for f in primary_failures[:5])
                            if len(primary_failures) > 5:
                                lines.append(f"  … and {len(primary_failures) - 5} more.")
                        if cross_failures:
                            lines.append(f"\n⚠ {len(cross_failures)} cross-post failure{'s' if len(cross_failures) != 1 else ''}:")
                            lines.extend(f"  • {f}" for f in cross_failures[:5])
                            if len(cross_failures) > 5:
                                lines.append(f"  … and {len(cross_failures) - 5} more.")
                        QMessageBox.warning(self, "Comments Posted with Errors", "\n".join(lines))
                        self._status(f"✓ Posted {succeeded}/{posted} comments. {len(failures)} failure(s).")

                self._spawn(
                    self._post_imported_comments, to_post, cross_map, other_client, _on_progress,
                    on_result=_on_done,
                )

    def _parse_comments_file(self, raw: str) -> dict:
        KEY_RE = r'[A-Z][A-Z0-9]+-\d+'
        result = {}
        SEP = r'\s*(?:[-|~;])\s*'

        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue

            keys_found = re.findall(KEY_RE, line)
            if not keys_found:
                continue

            remainder = re.sub(
                rf'^(?:{KEY_RE}\s*[,\s]\s*)+', '', line
            ).strip()

            match = re.match(
                rf'^(.+?){SEP}(.+?)\s*:\s*(.+)$',
                remainder
            )
            if not match:
                continue

            summary  = match.group(1).strip()
            assignee = match.group(2).strip()
            comment  = match.group(3).strip()
            if not comment:
                continue

            all_keys = list(dict.fromkeys(keys_found[:2]))  # deduplicated, max 2

            for key in all_keys:
                result[key] = {
                    "comment":     comment,
                    "summary":     summary,
                    "assignee":    assignee,
                    "paired_keys": [k for k in all_keys if k != key],
                }

        return result

    def _parse_comments_csv(self, path: str) -> dict:
        KEY_RE = r'^[A-Z][A-Z0-9]+-\d+$'
        result = {}
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    return result
                normalised = {h.strip().lower(): h for h in reader.fieldnames}

                key_col      = normalised.get("key")
                summary_col  = normalised.get("summary")
                assignee_col = normalised.get("assignee")
                comment_col  = normalised.get("comment")
                key2_col = (normalised.get("key2") or normalised.get("key_2") or
                            normalised.get("second_key") or normalised.get("other_key"))

                if not key_col or not comment_col:
                    return result

                for row in reader:
                    raw_key  = (row.get(key_col) or "").strip()
                    summary  = (row.get(summary_col)  or "").strip() if summary_col  else ""
                    assignee = (row.get(assignee_col) or "").strip() if assignee_col else ""
                    comment  = (row.get(comment_col)  or "").strip()

                    if not raw_key or not comment:
                        continue

                    # Support comma-separated keys in the key column
                    all_keys = [
                        k.strip().upper() for k in raw_key.split(",")
                        if re.match(KEY_RE, k.strip().upper())
                    ]

                    # Fall back to legacy key2 column if only one key in key column
                    if len(all_keys) == 1 and key2_col:
                        key2 = (row.get(key2_col) or "").strip().upper()
                        if key2 and re.match(KEY_RE, key2):
                            all_keys.append(key2)

                    all_keys = list(dict.fromkeys(all_keys))  # deduplicate, preserve order

                    if not all_keys:
                        continue

                    for key in all_keys:
                        result[key] = {
                            "comment":     comment,
                            "summary":     summary,
                            "assignee":    assignee,
                            "paired_keys": [k for k in all_keys if k != key],
                        }
        except Exception as e:
            raise RuntimeError(f"Could not read CSV file: {e}")
        return result

    def _post_imported_comments(self, comments: dict,
                                cross_map: dict = None, other_client=None,
                                progress_cb=None):
        cross_map = cross_map or {}
        total = len(comments)
        cross_failures = []
        for i, (key, comment) in enumerate(comments.items(), start=1):
            try:
                self._client.add_comment(key, comment)
            except Exception as e:
                cross_failures.append(f"{key} (primary): {e}")
            else:
                if other_client and key in cross_map:
                    for other_key in cross_map[key]:
                        try:
                            other_client.add_comment(other_key, comment)
                        except Exception as e:
                            cross_failures.append(f"{key} → {other_key}: {e}")
            if progress_cb:
                try:
                    progress_cb(i, total)
                except Exception:
                    pass
        return {"posted": total, "cross_failures": cross_failures}

    # ── Bulk Create ───────────────────────────────────────────────────────────
    @staticmethod
    def _download_bulk_template():
        path, _ = QFileDialog.getSaveFileName(
            None, "Save Bulk Create Template", "sprintmate_bulk_template.csv",
            "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(BulkCreateDialog.TEMPLATE_HEADERS)
                writer.writerow([
                    "Example story summary",
                    "Story",
                    "Medium",
                    "5",
                    "",
                    "",
                    date.today().strftime("%Y-%m-%d"),
                    "Optional description",
                ])
            QMessageBox.information(None, "Template Saved", f"Template saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(None, "Save Failed", str(e))

    def _open_bulk_create(self):
        project_key = self.project_combo.currentData()
        if not project_key or not self._client:
            return

        choice = QMessageBox.question(
            self, "Bulk Create Stories",
            "Do you need the CSV template first?\n\n"
            "Click Yes to download the template, or No to select an existing CSV.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.No,
        )
        if choice == QMessageBox.StandardButton.Cancel:
            return
        if choice == QMessageBox.StandardButton.Yes:
            self._download_bulk_template()
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Select Bulk Create CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return

        rows = []
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    QMessageBox.warning(self, "Empty File", "The CSV file has no header row.")
                    return
                normalised = {h.strip().lower(): h for h in reader.fieldnames}
                for raw_row in reader:
                    rows.append({
                        col: (raw_row.get(normalised.get(col, ""), "") or "")
                        for col in BulkCreateDialog.TEMPLATE_HEADERS
                    })
        except Exception as e:
            QMessageBox.critical(self, "CSV Read Error", str(e))
            return

        if not rows:
            QMessageBox.warning(self, "No Data", "The CSV file contains no data rows.")
            return

        members = self._users_cache or []
        issue_types = [
            {"name": self.edit_panel.issuetype_combo.itemText(i),
             "id":   self.edit_panel.issuetype_combo.itemData(i)}
            for i in range(self.edit_panel.issuetype_combo.count())
        ]

        dlg = BulkCreateDialog(
            rows=rows,
            members=members,
            issue_types=issue_types,
            sprints=self._sprints,
            parent=self,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        valid_rows = dlg.get_valid_rows()
        if not valid_rows:
            return

        self._busy(True)
        self._status(f"Bulk creating {len(valid_rows)} stories…")
        self._spawn(
            self._client.bulk_create_issues,
            project_key,
            valid_rows,
            on_result=self._on_bulk_created,
            on_error=lambda e: (
                self._busy(False),
                self._status("✗ Bulk create failed."),
                QMessageBox.critical(self, "Bulk Create Failed", str(e)),
            ),
        )

    def _on_bulk_created(self, results: list):
        self._busy(False)
        succeeded = [r for r in results if r["key"]]
        failed    = [r for r in results if r["error"]]

        if failed:
            lines = "\n".join(
                f"Row {r['row']} ({r['summary'][:40]}): {r['error']}"
                for r in failed
            )
            QMessageBox.warning(
                self, "Bulk Create — Partial Failure",
                f"✓ {len(succeeded)} created, ✗ {len(failed)} failed:\n\n{lines}"
            )
        else:
            QMessageBox.information(
                self, "Bulk Create Complete",
                f"✓ Successfully created {len(succeeded)} stor"
                f"{'ies' if len(succeeded) != 1 else 'y'}."
            )

        keys = ", ".join(r["key"] for r in succeeded if r["key"])
        self._status(f"✓ Bulk create: {len(succeeded)} succeeded"
                     + (f", {len(failed)} failed" if failed else "")
                     + (f" — {keys}" if keys else ""))
        self._load_sprint_issues()

    # ── New Story ─────────────────────────────────────────────────────────────
    def _open_new_story(self):
        key = self.project_combo.currentData()
        if not key or not self._client:
            return

        def _show_dialog(members):
            dlg = NewStoryDialog(
                project_key=key,
                members=members,
                issue_types=[{"name": self.edit_panel.issuetype_combo.itemText(i),
                            "id": self.edit_panel.issuetype_combo.itemData(i)}
                            for i in range(self.edit_panel.issuetype_combo.count())],
                sprints=self._sprints,
                parent=self,
            )
            if dlg.exec() == QDialog.DialogCode.Accepted:
                vals = dlg.get_values()
                self._busy(True)
                self._status("Creating story…")
                self._spawn(
                    self._client.create_issue,
                    key,
                    vals["summary"],
                    vals["issue_type"],
                    vals["description"],
                    vals["assignee_id"],
                    vals["priority"],
                    vals["story_points"],
                    vals["sprint_id"],
                    vals["due_date"],
                    on_result=self._on_story_created,
                    on_error=lambda e: (
                        self._busy(False),
                        self._status("✗ Failed to create story."),
                        QMessageBox.critical(self, "Create Failed", str(e)),
                    ),
                )

        if self._users_cache:
            _show_dialog(self._users_cache)
        else:
            self._busy(True)
            self._status("Loading users…")

            def _on_users_ready(members):
                self._busy(False)
                _show_dialog(members)

            self._refresh_users_cache(on_done=_on_users_ready)

    def _on_story_created(self, result: dict):
        self._busy(False)
        errors = result.get("errorMessages") or list(result.get("errors", {}).values())
        if errors:
            msg = "\n".join(str(e) for e in errors)
            self._status("✗ Failed to create story.")
            QMessageBox.critical(self, "Create Failed", msg)
            return
        key = result.get("key", "")
        self._status(f"✓ Created {key} successfully.")
        QMessageBox.information(self, "Story Created", f"✓ Successfully created {key}.")
        self._load_sprint_issues()

    # ── Save ──────────────────────────────────────────────────────────────────
    def _on_save_story(self, key: str, fields: dict, comment: str,
                       transition_id, target_sprint):
        # Clear unsaved row indicator
        if self._unsaved_row is not None:
            ki = self.table.item(self._unsaved_row, COL_KEY)
            if ki:
                ki.setText(ki.text().replace(" ●", ""))
                ki.setForeground(QColor(ACCENT_CYAN))
            self._unsaved_row = None
        self._busy(True)
        self._status(f"Saving {key}…")
        self._spawn(
            self._do_save, key, fields, comment, transition_id, target_sprint,
            on_result=lambda result: self._on_saved(key, result),
            on_error=lambda e: (
                self._busy(False),
                self._status(f"\u2717 Failed to save {key}."),
                QMessageBox.critical(self, "Save Failed", str(e)),
            ),
        )

    def _do_save(self, key, fields, comment, transition_id, target_sprint):
        pts_dropped = False
        try:
            self._client.update_issue(key, fields)
        except RuntimeError as e:
            sp = self._client.story_point_field_id
            err_str = str(e)
            if sp in err_str or any(f in err_str for f in JiraClient._SP_FALLBACKS):
                fields_no_pts = {k: v for k, v in fields.items() if k not in ([sp] + JiraClient._SP_FALLBACKS)}
                self._client.update_issue(key, fields_no_pts)
                pts_dropped = True
            else:
                raise
        if transition_id:
            self._client.transition_issue(key, transition_id)
        if target_sprint is not None:
            self._client.move_to_sprint(key, target_sprint)
        if comment:
            self._client.add_comment(key, comment)
        return {"pts_dropped": pts_dropped}

    def _on_saved(self, key: str, result: dict = None):
        self._busy(False)
        if result and result.get("pts_dropped"):
            QMessageBox.warning(
                self, "Story Points Not Saved",
                f"⚠ {key} was updated, but story points were rejected by Jira.\n"
                "This usually means the points field is read-only for this issue type.\n"
                "All other changes were saved successfully."
            )
            self._status(f"⚠ {key} updated — story points were not saved.")
        else:
            self._status(f"✓ {key} updated successfully.")
        self.edit_panel._snapshot = self.edit_panel._snapshot_state()
        self.edit_panel.save_btn.setEnabled(False)
        self.edit_panel.undo_btn.setEnabled(True)
        self.edit_panel.save_btn.setToolTip("No changes to save")
        self._load_sprint_issues(reselect_key=key)

    def _compare_sprints(self):
        cid = self.compare_combo.currentData()
        bid = self.board_combo.currentData()
        if cid is None or not self._issues or not self._client:
            QMessageBox.information(self, "Compare Sprints", "Load a sprint first, then select one to compare.")
            return
        self._busy(True)
        self._status("Loading comparison sprint…")
        self._spawn(self._client.get_sprint_issues, bid, cid,
            on_result=self._on_compare_loaded,
            on_error=lambda e: (self._busy(False), self._status("✗ Compare failed."),
                QMessageBox.critical(self, "Compare Failed", str(e))))

    def _on_compare_loaded(self, compare_issues):
        self._busy(False)
        sp      = self._sp_field
        cmap    = {i["key"]: i for i in compare_issues}
        curmap  = {i["key"]: i for i in self._issues}
        moved_bg   = QColor("#1A3A1A")
        changed_bg = QColor("#1A2A3A")

        def _fld(iss, *path):
            obj = iss.get("fields") or {}
            for p in path:
                obj = (obj or {}).get(p) or {}
            return obj if isinstance(obj, str) else ""

        # Build diff records for export
        self._compare_label   = self.compare_combo.currentText()
        self._compare_records = []   # list of dicts for CSV export

        n_new = n_changed = 0
        for row in range(self.table.rowCount()):
            ki = self.table.item(row, 0)
            if not ki:
                continue
            key = ki.text()
            rec = {"key": key, "change_type": "", "diffs": ""}
            if key not in cmap:
                for col in range(self.table.columnCount()):
                    it = self.table.item(row, col)
                    if it:
                        it.setBackground(moved_bg)
                n_new += 1
                rec["change_type"] = "added"
            else:
                curr, prev = curmap[key], cmap[key]
                diffs = []
                for lbl, *path in [("status", "status", "name"), ("assignee", "assignee", "displayName")]:
                    cv, pv = _fld(curr, *path), _fld(prev, *path)
                    if cv != pv:
                        diffs.append(f"{lbl}: {pv or '—'} → {cv or '—'}")
                try:
                    _cv = (curr.get("fields") or {}).get(sp)
                    _pv = (prev.get("fields") or {}).get(sp)
                    cp  = int(float(_cv)) if _cv is not None else None
                    pp  = int(float(_pv)) if _pv is not None else None
                except (TypeError, ValueError):
                    cp = pp = None
                if cp != pp:
                    diffs.append(f"pts: {pp} → {cp}")
                if diffs:
                    for col in range(self.table.columnCount()):
                        it = self.table.item(row, col)
                        if it:
                            it.setBackground(changed_bg)
                    ki.setToolTip("\n".join(diffs))
                    n_changed += 1
                    rec["change_type"] = "changed"
                    rec["diffs"]       = "; ".join(diffs)
            if rec["change_type"]:
                self._compare_records.append(rec)

        for key in cmap:
            if key not in curmap:
                self._compare_records.append({"key": key, "change_type": "removed", "diffs": ""})

        n_removed = sum(1 for k in cmap if k not in curmap)
        summary = (f"Compare vs {self._compare_label}: "
                   f"{n_new} added, {n_removed} removed, {n_changed} changed. "
                   "Hover KEY for details.")
        self._status(summary)

        # Build a summary HTML for the Compare sub-tab
        rows_html = ""
        for rec in self._compare_records:
            type_colour = {
                "added":   "#3fb950",
                "changed": "#388bfd",
                "removed": "#f78166",
            }.get(rec["change_type"], "#8b949e")
            rows_html += (
                f"<tr>"
                f"<td style='font-weight:600;color:{ACCENT_CYAN};'>{rec['key']}</td>"
                f"<td style='color:{type_colour};font-weight:600;text-transform:uppercase;"
                f"font-size:11px;'>{rec['change_type']}</td>"
                f"<td style='color:#57606a;font-size:12px;'>{rec.get('diffs','')}</td>"
                f"</tr>"
            )
        compare_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:transparent;padding:32px 24px;color:#1f2328;}}
  h1{{font-size:22px;font-weight:700;margin-bottom:4px;}}
  .meta{{color:#57606a;font-size:13px;margin-bottom:24px;}}
  .stat{{display:inline-block;padding:4px 14px;border-radius:20px;
         font-size:12px;font-weight:600;margin-right:8px;margin-bottom:16px;}}
  table{{border-collapse:collapse;width:100%;background:#fff;
         border:1px solid #d0d7de;border-radius:8px;overflow:hidden;}}
  th{{background:#f6f8fa;padding:10px 16px;text-align:left;font-size:10px;
      font-weight:700;text-transform:uppercase;letter-spacing:.6px;
      color:#57606a;border-bottom:1px solid #d0d7de;}}
  td{{padding:10px 16px;border-bottom:1px solid #f0f0f0;vertical-align:top;}}
  tr:last-child td{{border-bottom:none;}}
</style></head><body>
<h1>⇆ Sprint Compare</h1>
<div class="meta">vs {self._compare_label}</div>
<div>
  <span class="stat" style="background:#dcfce7;color:#3fb950;">{n_new} added</span>
  <span class="stat" style="background:#dbeafe;color:#388bfd;">{n_changed} changed</span>
  <span class="stat" style="background:#fff1ee;color:#f78166;">{n_removed} removed</span>
</div>
{"<table><tr><th>Key</th><th>Change</th><th>Details</th></tr>" + rows_html + "</table>"
 if rows_html else "<p style='color:#57606a;'>No differences found.</p>"}
</body></html>"""
        self._rpt_compare_browser.setHtml(self._dark_html(compare_html))
        self._reports_html_map[3] = compare_html  # export uses original
        self._reports_html = compare_html
        self.tabs.setCurrentIndex(3)
        self._reports_tabs.setCurrentIndex(3)
        self._rpt_save_btn.setEnabled(True)

        if self._compare_records:
            reply = QMessageBox.question(
                self, "Compare Complete",
                f"{summary}\n\nExport the diff to CSV?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._export_compare_csv()

    def _export_compare_csv(self):
        """Export the most recent sprint comparison diff to CSV."""
        records = getattr(self, "_compare_records", [])
        if not records:
            return
        label   = getattr(self, "_compare_label", "compare")
        slug    = re.sub(r"[^\w\-]", "-", label)[:40]
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Compare Export",
            f"sprint-compare-{slug}-{date.today()}.csv",
            "CSV Files (*.csv)",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["key", "change_type", "diffs"])
                for r in records:
                    w.writerow([r["key"], r["change_type"], r["diffs"]])
            QMessageBox.information(self, "Exported", f"Compare diff saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _duplicate_story(self, key: str):
        issue = next((i for i in self._issues if i["key"] == key), None)
        if not issue: return
        f = issue.get("fields", {}); sp = self._sp_field
        summary   = f.get("summary", "") + " (copy)"
        issuetype = (f.get("issuetype") or {}).get("id")
        priority  = (f.get("priority") or {}).get("name", "")
        pts_raw   = next((f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS) if f.get(k) is not None), None)
        try: pts = int(float(pts_raw)) if pts_raw is not None else None
        except (TypeError, ValueError): pts = None
        aobj = f.get("assignee") or {}
        aid  = aobj.get("name") or aobj.get("accountId")
        desc = f.get("description") or ""
        if isinstance(desc, dict): desc = self.edit_panel._adf_to_text(desc).strip()
        self._busy(True)
        self._status(f"Duplicating {key}…")
        self._spawn(self._client.create_issue,
            self.project_combo.currentData(), summary, issuetype, desc, aid,
            priority, pts, self.sprint_combo.currentData(), (f.get("duedate") or "")[:10] or None,
            on_result=lambda r: self._on_duplicate_done(r, key),
            on_error=lambda e: (self._busy(False), self._status("✗ Duplicate failed."),
                QMessageBox.critical(self, "Duplicate Failed", str(e))))

    def _on_duplicate_done(self, result, source_key: str):
        self._busy(False)
        new_key = result.get("key", "") if isinstance(result, dict) else ""
        if new_key:
            self._status(f"✓ Duplicated {source_key} → {new_key}.")
            self._load_sprint_issues(reselect_key=new_key)
        else:
            errors = result.get("errorMessages", []) if isinstance(result, dict) else []
            QMessageBox.critical(self, "Duplicate Failed", "\n".join(errors) or "Unknown error.")

    def _populate_quick_add_types(self, issue_types: list):
        self.quick_add_type_combo.blockSignals(True)
        self.quick_add_type_combo.clear()
        for it in issue_types:
            self.quick_add_type_combo.addItem(it.get("name", "?"), it)
        # Default to Story if present, otherwise first type
        for i in range(self.quick_add_type_combo.count()):
            if self.quick_add_type_combo.itemText(i).lower() == "story":
                self.quick_add_type_combo.setCurrentIndex(i)
                break
        self.quick_add_type_combo.blockSignals(False)
        self.quick_add_type_combo.setEnabled(True)

    def _quick_add_story(self):
        summary = self.quick_add_edit.text().strip()
        if not summary or not self._client:
            return
        # Duplicate detection
        if not self._check_quick_add_duplicate(summary):
            return
        # Use the selected type from the quick-add combo
        itype_data = self.quick_add_type_combo.currentData()
        if itype_data:
            itype = itype_data
        else:
            # Fallback: first type from edit panel combo
            types = [self.edit_panel.issuetype_combo.itemData(i)
                     for i in range(self.edit_panel.issuetype_combo.count())
                     if self.edit_panel.issuetype_combo.itemData(i)]
            if not types:
                QMessageBox.warning(self, "Quick Add", "No issue types loaded.")
                return
            itype = {"id": types[0], "name": self.edit_panel.issuetype_combo.itemText(0)}
        self.quick_add_edit.clear()
        self.quick_add_edit.setEnabled(False)
        self._busy(True)
        self._status(f"Creating {itype.get('name', 'story')}…")
        self._spawn(self._client.create_issue,
            self.project_combo.currentData(), summary, itype, "", None, None, None,
            self.sprint_combo.currentData(), None,
            on_result=lambda r: self._on_quick_add_done(r),
            on_error=lambda e: (
                self._busy(False),
                self.quick_add_edit.setEnabled(True),
                self._status("✗ Quick add failed."),
                QMessageBox.critical(self, "Quick Add Failed", str(e)),
            )
        )

    def _on_quick_add_done(self, result):
        self._busy(False)
        self.quick_add_edit.setEnabled(True)
        key = result.get("key", "") if isinstance(result, dict) else ""
        if key:
            self._status(f"✓ Created {key}.")
            self._load_sprint_issues(reselect_key=key)
        else:
            errors = result.get("errorMessages", []) if isinstance(result, dict) else []
            QMessageBox.critical(self, "Quick Add Failed", "\n".join(errors) or "Unknown error.")

    # ── Attach File ───────────────────────────────────────────────────────────
    def _attach_file_to_issue(self, key: str):
        paths, _ = QFileDialog.getOpenFileNames(
            self, f"Attach File(s) to {key}", "",
            "All Files (*)"
        )
        if not paths:
            return
        total = len(paths)
        self._busy(True)
        self._status(f"Attaching {total} file(s) to {key}…")

        def _do_attach():
            results = []
            for path in paths:
                try:
                    self._client.attach_file(key, path)
                    results.append((path, None))
                except Exception as e:
                    results.append((path, str(e)))
            return results

        def _on_done(results):
            self._busy(False)
            import os
            ok  = [r for r in results if r[1] is None]
            err = [r for r in results if r[1] is not None]
            if not err:
                names = ", ".join(os.path.basename(r[0]) for r in ok)
                QMessageBox.information(
                    self, "Attached",
                    f"✓ Successfully attached {len(ok)} file(s) to {key}:\n{names}"
                )
                self._status(f"✓ {len(ok)} file(s) attached to {key}.")
            else:
                lines = [f"✓ {len(ok)} attached successfully."] if ok else []
                lines += [f"✗ {os.path.basename(r[0])}: {r[1]}" for r in err]
                QMessageBox.warning(self, "Attach — Partial Failure", "\n".join(lines))
                self._status(f"⚠ {len(ok)} attached, {len(err)} failed for {key}.")

        self._spawn(_do_attach, on_result=_on_done)

    # ── Sprint Report ─────────────────────────────────────────────────────────
    def _open_sprint_report(self):
        """Legacy — delegates to the Reports tab."""
        self.tabs.setCurrentIndex(3)
        self._reports_tabs.setCurrentIndex(0)
        self._reports_generate_sprint()

    def _open_velocity_history(self):
        """Legacy — delegates to the Reports tab."""
        self.tabs.setCurrentIndex(3)
        self._reports_tabs.setCurrentIndex(2)
        self._reports_generate_velocity()

    def _on_reports_tab_changed(self, idx: int):
        """Update Save HTML button state when switching sub-tabs."""
        html = self._reports_html_map.get(idx, "")
        self._reports_html = html
        self._rpt_save_btn.setEnabled(bool(html))

    def _reports_switch(self):
        self.tabs.setCurrentIndex(3)

    def _reports_get_sprint_issues(self) -> tuple:
        sprint_id    = self._rpt_sprint_combo.currentData()
        sprint_label = self._rpt_sprint_combo.currentText()
        if not sprint_id or not self._client:
            return [], sprint_label, {}
        if sprint_id == self.sprint_combo.currentData() and self._issues:
            detail = {}
            try:
                detail = self._client.get_sprint_detail(sprint_id)
            except Exception:
                pass
            return self._issues, sprint_label, detail
        self._busy(True)
        self._status("Loading sprint for report…")
        try:
            issues = self._client.get_sprint_issues(
                self.board_combo.currentData(), sprint_id
            )
            detail = {}
            try:
                detail = self._client.get_sprint_detail(sprint_id)
            except Exception:
                pass
            return issues, sprint_label, detail
        except Exception as e:
            QMessageBox.critical(self, "Report Error", str(e))
            return [], sprint_label, {}
        finally:
            self._busy(False)

    def _reports_generate_sprint(self):
        if not self._client:
            return
        self.tabs.setCurrentIndex(3)
        self._reports_tabs.setCurrentIndex(0)

        # Determine scope from sub-tab controls
        use_sprint = self._srt_sprint_rb.isChecked()
        if use_sprint:
            sprint_id    = self._srt_sprint_sel.currentData()
            sprint_label = self._srt_sprint_sel.currentText()
            if not sprint_id:
                QMessageBox.warning(self, "No Sprint", "Please select a sprint.")
                return
            # Reuse cached issues if sprint matches loaded sprint
            if sprint_id == self.sprint_combo.currentData() and self._issues:
                issues = self._issues
                sprint_detail = {}
                try:
                    sprint_detail = self._client.get_sprint_detail(sprint_id)
                except Exception:
                    pass
            else:
                self._busy(True)
                self._status("Loading sprint for report…")
                try:
                    issues = self._client.get_sprint_issues(
                        self.board_combo.currentData(), sprint_id
                    )
                    sprint_detail = {}
                    try:
                        sprint_detail = self._client.get_sprint_detail(sprint_id)
                    except Exception:
                        pass
                except Exception as e:
                    self._busy(False)
                    QMessageBox.critical(self, "Report Error", str(e))
                    return
                finally:
                    self._busy(False)
        else:
            # Date range scope
            from_date = self._srt_from.text().strip()
            to_date   = self._srt_to.text().strip()
            if not from_date or not to_date:
                QMessageBox.warning(self, "Date Range", "Please enter both From and To dates.")
                return
            sprint_label  = f"{from_date} → {to_date}"
            sprint_detail = {}
            self._busy(True)
            self._status("Loading issues for date range…")
            try:
                issues = self._client.get_issues_by_date_range(
                    self.project_combo.currentData(), from_date, to_date
                )
            except Exception as e:
                self._busy(False)
                QMessageBox.critical(self, "Report Error", str(e))
                return
            finally:
                self._busy(False)

        if not issues:
            QMessageBox.information(self, "No Stories", "No stories found for the selected scope.")
            return

        self._status("Generating sprint report…")
        dlg = SprintReportDialog(
            issues=issues, sprint_label=sprint_label,
            sp_field=self._sp_field, fl_field=self.edit_panel._fl_field,
            base_url=self.edit_panel._base_url,
            adf_to_text_fn=self.edit_panel._adf_to_text,
            client=self._client, board_id=self.board_combo.currentData() or 0,
            sprint_detail=sprint_detail, parent=self,
        )
        dlg._build_report(issues, sprint_label)
        html = dlg._html
        self._rpt_sprint_browser.setHtml(self._dark_html(html))
        self._reports_html_map[0] = html  # export uses original light HTML
        self._reports_html = html
        self._rpt_save_btn.setEnabled(True)
        self._status(f"✓ Sprint report — {len(issues)} stories.")

    def _reports_generate_people(self):
        if not self._client:
            return
        self.tabs.setCurrentIndex(3)
        self._reports_tabs.setCurrentIndex(1)

        # Scope
        use_sprint = self._prt_sprint_rb.isChecked()
        if use_sprint:
            sprint_id    = self._prt_sprint_sel.currentData()
            sprint_label = self._prt_sprint_sel.currentText()
            if not sprint_id:
                QMessageBox.warning(self, "No Sprint", "Please select a sprint.")
                return
            if sprint_id == self.sprint_combo.currentData() and self._issues:
                issues = self._issues
            else:
                self._busy(True)
                self._status("Loading sprint for people report\u2026")
                try:
                    issues = self._client.get_sprint_issues(
                        self.board_combo.currentData(), sprint_id
                    )
                except Exception as e:
                    self._busy(False)
                    QMessageBox.critical(self, "Report Error", str(e))
                    return
                finally:
                    self._busy(False)
        else:
            from_date = self._prt_from.text().strip()
            to_date   = self._prt_to.text().strip()
            if not from_date or not to_date:
                QMessageBox.warning(self, "Date Range", "Please enter both From and To dates.")
                return
            sprint_label = f"{from_date} \u2192 {to_date}"
            self._busy(True)
            self._status("Loading issues for date range\u2026")
            try:
                issues = self._client.get_issues_by_date_range(
                    self.project_combo.currentData(), from_date, to_date
                )
            except Exception as e:
                self._busy(False)
                QMessageBox.critical(self, "Report Error", str(e))
                return
            finally:
                self._busy(False)

        if not issues:
            QMessageBox.information(self, "No Stories", "No stories found for the selected scope.")
            return

        # Collect selected people
        selected_items = self._prt_people_list.selectedItems()
        assignees = [item.text() for item in selected_items]
        extra = [n.strip() for n in self._prt_extra.text().split(",") if n.strip()]
        assignees = list(dict.fromkeys(assignees + extra))
        if not assignees:
            assignees = sorted({
                (iss.get("fields", {}).get("assignee") or {}).get(
                    "displayName",
                    (iss.get("fields", {}).get("assignee") or {}).get("name", "")
                )
                for iss in issues if iss.get("fields", {}).get("assignee")
            })

        dlg = SprintReportDialog(
            issues=issues, sprint_label=sprint_label,
            sp_field=self._sp_field, fl_field=self.edit_panel._fl_field,
            base_url=self.edit_panel._base_url,
            adf_to_text_fn=self.edit_panel._adf_to_text,
            client=self._client, board_id=self.board_combo.currentData() or 0,
            sprint_detail={}, parent=self,
        )
        dlg._build_people_report(issues, assignees, sprint_label)
        html = dlg._people_html
        self._rpt_people_browser.setHtml(self._dark_html(html))
        self._reports_html_map[1] = html  # export uses original light HTML
        self._reports_html = html
        self._rpt_save_btn.setEnabled(True)
        self._status(f"\u2713 People report \u2014 {len(assignees)} people.")

    def _reports_generate_velocity(self):
        if not self._client:
            return
        self.tabs.setCurrentIndex(3)
        self._reports_tabs.setCurrentIndex(2)
        board_id = self.board_combo.currentData()
        if not board_id:
            return
        self._busy(True)
        self._status("Loading velocity history…")

        def _do():
            return self._client.get_velocity_history(board_id, num_sprints=8)

        def _on_done(data):
            self._busy(False)
            if not data:
                self._status("No closed sprints found.")
                return

            # Build SVG bar chart
            W, H      = 660, 240
            PAD_L, PAD_R, PAD_T, PAD_B = 52, 16, 24, 56
            chart_w   = W - PAD_L - PAD_R
            chart_h   = H - PAD_T - PAD_B
            n         = len(data)
            max_pts   = max((d["total_pts"] for d in data), default=1) or 1
            bar_group = chart_w / n
            bar_w     = max(4, int(bar_group * 0.35))
            gap       = max(2, int(bar_group * 0.06))

            def py(pts):
                return PAD_T + chart_h - round(pts / max_pts * chart_h)

            bars = x_labels = y_ticks = ""
            for i, d in enumerate(data):
                cx  = PAD_L + int(i * bar_group + bar_group / 2)
                bx1 = cx - bar_w - gap // 2
                bh1 = round(d["total_pts"] / max_pts * chart_h)
                by1 = PAD_T + chart_h - bh1
                bx2 = cx + gap // 2
                bh2 = round(d["done_pts"]  / max_pts * chart_h)
                by2 = PAD_T + chart_h - bh2
                bars += (
                    f'<rect x="{bx1}" y="{by1}" width="{bar_w}" height="{bh1}" '
                    f'fill="{ACCENT_BLUE}" rx="3" opacity="0.7"/>'
                    f'<rect x="{bx2}" y="{by2}" width="{bar_w}" height="{bh2}" '
                    f'fill="{ACCENT_GREEN}" rx="3"/>'
                )
                if d["total_pts"]:
                    bars += (
                        f'<text x="{bx1+bar_w//2}" y="{by1-4}" text-anchor="middle" '
                        f'fill="{TEXT_SEC}" font-size="9" font-family="sans-serif">'
                        f'{d["total_pts"]}</text>'
                        f'<text x="{bx2+bar_w//2}" y="{by2-4}" text-anchor="middle" '
                        f'fill="{ACCENT_GREEN}" font-size="9" font-family="sans-serif">'
                        f'{d["done_pts"]}</text>'
                    )
                short = (d["name"][:13] + "…") if len(d["name"]) > 13 else d["name"]
                x_labels += (
                    f'<text x="{cx}" y="{PAD_T+chart_h+14}" text-anchor="middle" '
                    f'fill="{TEXT_SEC}" font-size="9" font-family="sans-serif">{short}</text>'
                )

            for v in range(0, int(max_pts) + 1, max(1, int(max_pts) // 5)):
                yy = py(v)
                y_ticks += (
                    f'<line x1="{PAD_L}" y1="{yy}" x2="{PAD_L+chart_w}" y2="{yy}" '
                    f'stroke="{BORDER}" stroke-width="1"/>'
                    f'<text x="{PAD_L-6}" y="{yy+4}" text-anchor="end" '
                    f'fill="{TEXT_SEC}" font-size="9" font-family="sans-serif">{v}</text>'
                )

            legend = (
                f'<rect x="{PAD_L}" y="{H-20}" width="12" height="10" '
                f'fill="{ACCENT_BLUE}" rx="2" opacity="0.7"/>'
                f'<text x="{PAD_L+16}" y="{H-11}" fill="{TEXT_SEC}" '
                f'font-size="10" font-family="sans-serif">Committed</text>'
                f'<rect x="{PAD_L+96}" y="{H-20}" width="12" height="10" '
                f'fill="{ACCENT_GREEN}" rx="2"/>'
                f'<text x="{PAD_L+112}" y="{H-11}" fill="{TEXT_SEC}" '
                f'font-size="10" font-family="sans-serif">Completed</text>'
            )

            svg = (
                f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                f'xmlns="http://www.w3.org/2000/svg" '
                f'style="background:{PANEL_BG};">'
                f'{y_ticks}{bars}{x_labels}{legend}'
                f'<line x1="{PAD_L}" y1="{PAD_T}" x2="{PAD_L}" '
                f'y2="{PAD_T+chart_h}" stroke="{BORDER}" stroke-width="1"/>'
                f'<line x1="{PAD_L}" y1="{PAD_T+chart_h}" '
                f'x2="{PAD_L+chart_w}" y2="{PAD_T+chart_h}" '
                f'stroke="{BORDER}" stroke-width="1"/>'
                f'</svg>'
            )

            # Render into QSvgWidget or fall back gracefully
            if getattr(self, '_rpt_vel_svg_available', False):
                self._rpt_vel_svg.load(QByteArray(svg.encode()))
            else:
                if hasattr(self._rpt_vel_svg, 'setText'):
                    self._rpt_vel_svg.setText(
                        "PyQt6-Qt6-Svg not installed — chart unavailable.\n"
                        "pip install PyQt6-Qt6-Svg"
                    )

            # Populate table
            self._rpt_vel_table.setSortingEnabled(False)
            self._rpt_vel_table.setRowCount(0)
            for d in data:
                pct = round(d["done_pts"] / d["total_pts"] * 100) if d["total_pts"] else 0
                row = self._rpt_vel_table.rowCount()
                self._rpt_vel_table.insertRow(row)
                self._rpt_vel_table.setItem(row, 0, QTableWidgetItem(d["name"]))
                for c, (val, colour) in enumerate([
                    (d["total_pts"], None),
                    (d["done_pts"],  ACCENT_GREEN),
                    (d["n_total"],   None),
                    (d["n_done"],    ACCENT_GREEN),
                    (f"{pct}%",      None),
                ], 1):
                    it = QTableWidgetItem(str(val))
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if colour:
                        it.setForeground(QColor(colour))
                    self._rpt_vel_table.setItem(row, c, it)
                self._rpt_vel_table.setRowHeight(row, 32)
            self._rpt_vel_table.setSortingEnabled(True)

            # Build exportable HTML for save
            rows = "".join(
                f"<tr><td>{d['name']}</td>"
                f"<td style='text-align:center'>{d['total_pts']}</td>"
                f"<td style='text-align:center;color:#3fb950;font-weight:bold'>{d['done_pts']}</td>"
                f"<td style='text-align:center'>{d['n_total']}</td>"
                f"<td style='text-align:center;color:#3fb950'>{d['n_done']}</td>"
                f"<td style='text-align:center'>"
                f"{round(d['done_pts']/d['total_pts']*100) if d['total_pts'] else 0}%</td></tr>"
                for d in data
            )
            html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:transparent;padding:32px 24px;color:#1f2328;}}
  h1{{font-size:22px;font-weight:700;margin-bottom:4px;}}
  .sub{{color:#57606a;font-size:13px;margin-bottom:24px;}}
  table{{border-collapse:collapse;width:100%;background:#fff;
         border:1px solid #d0d7de;border-radius:8px;overflow:hidden;}}
  th{{background:#f6f8fa;padding:10px 16px;text-align:left;font-size:11px;
      font-weight:700;text-transform:uppercase;letter-spacing:.6px;
      color:#57606a;border-bottom:1px solid #d0d7de;}}
  td{{padding:10px 16px;border-bottom:1px solid #f0f0f0;font-size:13px;}}
  tr:last-child td{{border-bottom:none;}}
</style></head><body>
<h1>📈 Velocity History</h1>
<div class="sub">{len(data)} most recent closed sprints</div>
<table><tr><th>Sprint</th><th>Total Pts</th><th>Done Pts</th>
<th>Stories</th><th>Done</th><th>Completion</th></tr>{rows}</table>
</body></html>"""
            self._reports_html_map[2] = html
            self._reports_html = html
            self._rpt_save_btn.setEnabled(True)
            self._status(f"✓ Velocity — {len(data)} sprints.")

        self._spawn(_do, on_result=_on_done,
                    on_error=lambda e: (
                        self._busy(False),
                        self._status(f"✗ Velocity failed: {e}"),
                    ))

    def _dark_html(self, html: str) -> str:
        """Rewrite an HTML report's colour values for dark in-app display.
        Direct substitution is used instead of CSS cascade because QTextBrowser's
        built-in HTML renderer has limited support for !important and pseudo-selectors.
        The original light-theme HTML is preserved separately for export."""

        # Map of light → dark colour substitutions applied to the HTML string.
        # Order matters — more specific colours first.
        substitutions = [
            # Body / page background
            ('background: #f6f8fa;',          f'background: {DARK_BG};'),
            ('background:#f6f8fa;',            f'background:{DARK_BG};'),
            ('background: transparent;',       f'background: {DARK_BG};'),
            ('background:transparent;',        f'background:{DARK_BG};'),
            # Card / panel surfaces
            ('background: #ffffff;',           f'background: {PANEL_BG};'),
            ('background:#ffffff;',            f'background:{PANEL_BG};'),
            ('background: #fff;',              f'background: {PANEL_BG};'),
            ('background:#fff;',               f'background:{PANEL_BG};'),
            # Table header
            ('background: #f6f8fa;',           f'background: {CARD_BG};'),
            ('background:#f6f8fa;',            f'background:{CARD_BG};'),
            # Row hover (needs to be dark too)
            ('background: #f6f8fa !important', f'background: {CARD_BG} !important'),
            # Text colours
            ('color: #1f2328;',                f'color: {TEXT_PRI};'),
            ('color:#1f2328;',                 f'color:{TEXT_PRI};'),
            ('color: #57606a;',                f'color: {TEXT_SEC};'),
            ('color:#57606a;',                 f'color:{TEXT_SEC};'),
            ('color: #8b949e;',                f'color: {TEXT_DIM};'),
            ('color:#8b949e;',                 f'color:{TEXT_DIM};'),
            # Border colours
            ('border: 1px solid #d0d7de;',     f'border: 1px solid {BORDER};'),
            ('border:1px solid #d0d7de;',      f'border:1px solid {BORDER};'),
            ('border-bottom: 1px solid #d0d7de;', f'border-bottom: 1px solid {BORDER};'),
            ('border-bottom:1px solid #d0d7de;',  f'border-bottom:1px solid {BORDER};'),
            ('border-bottom: 1px solid #f0f0f0;', f'border-bottom: 1px solid {BORDER};'),
            ('border-bottom:1px solid #f0f0f0;',  f'border-bottom:1px solid {BORDER};'),
            # Box shadows — remove them (dark theme doesn't need them)
            ('box-shadow: 0 1px 3px rgba(0,0,0,.04);', ''),
            # Section heading rule colour
            ('background: #d0d7de;',           f'background: {BORDER};'),
            ('background:#d0d7de;',            f'background:{BORDER};'),
        ]

        result = html
        for old, new in substitutions:
            result = result.replace(old, new)

        # Also inject a minimal <style> block for any colours we can't reach
        # via simple substitution (e.g. pseudo-selectors in the report's own CSS)
        extra_css = f"""<style>
body {{ background: {DARK_BG} !important; color: {TEXT_PRI} !important; }}
thead th {{ background: {CARD_BG} !important; color: {TEXT_SEC} !important; }}
tbody tr:hover td {{ background: {CARD_BG} !important; }}
.stat-card, .card, .assignee-card, .table-wrap, .burndown-card {{
    background: {PANEL_BG} !important; border-color: {BORDER} !important;
}}
a {{ color: {ACCENT_CYAN} !important; }}
</style>"""
        if '<head>' in result:
            result = result.replace('<head>', f'<head>{extra_css}', 1)

        return result

    def _reports_generate_burndown(self):
        """Generate a standalone burndown chart in the Burndown sub-tab."""
        if not self._issues or not self._client:
            return
        self.tabs.setCurrentIndex(3)
        self._reports_tabs.setCurrentIndex(4)

        sprint_id    = self.sprint_combo.currentData()
        sprint_label = self.sprint_lbl.text() or self.sprint_combo.currentText()

        sprint_detail = {}
        if sprint_id:
            try:
                sprint_detail = self._client.get_sprint_detail(sprint_id)
            except Exception:
                pass

        # Compute stats from current issues
        sp        = self._sp_field
        total_pts = done_pts = n_done = 0
        for iss in self._issues:
            f      = iss.get("fields", {})
            status = (f.get("status") or {}).get("name", "")
            pts_raw = next(
                (f.get(k) for k in ([sp] + JiraClient._SP_FALLBACKS)
                 if f.get(k) is not None), None
            )
            try:
                pts = int(float(pts_raw)) if pts_raw is not None else 0
            except (TypeError, ValueError):
                pts = 0
            total_pts += pts
            if status == "Done":
                done_pts += pts
                n_done   += 1

        # Reuse SprintReportDialog's burndown SVG builder
        dlg = SprintReportDialog(
            issues=self._issues, sprint_label=sprint_label,
            sp_field=sp, fl_field=self.edit_panel._fl_field,
            base_url=self.edit_panel._base_url,
            adf_to_text_fn=self.edit_panel._adf_to_text,
            client=self._client,
            board_id=self.board_combo.currentData() or 0,
            sprint_detail=sprint_detail, parent=self,
        )
        svg = dlg._build_burndown_svg(total_pts, done_pts, len(self._issues), n_done)

        # Build a minimal HTML wrapper styled to match the app
        start_str = (sprint_detail.get("startDate") or "")[:10]
        end_str   = (sprint_detail.get("endDate")   or "")[:10]
        date_range = f"{start_str} → {end_str}" if start_str and end_str else ""
        pct_done  = round(done_pts / total_pts * 100) if total_pts else 0

        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
         background:transparent; padding:28px 24px; color:#1f2328; margin:0; }}
  h1   {{ font-size:20px; font-weight:700; margin:0 0 4px; }}
  .meta {{ color:#57606a; font-size:12px; margin-bottom:20px; }}
  .card {{ background:#fff; border:1px solid #d0d7de; border-radius:10px;
           padding:20px 24px; box-shadow:0 1px 3px rgba(0,0,0,.04); }}
  .stats {{ display:flex; gap:32px; margin-top:16px; padding-top:14px;
            border-top:1px solid #f0f0f0; font-size:12px; }}
  .stat-lbl {{ color:#57606a; margin-bottom:2px; }}
  .stat-val {{ font-size:20px; font-weight:700; color:#1f2328; }}
  .stat-val.green {{ color:#3fb950; }}
  .stat-val.blue  {{ color:#388bfd; }}
  @media print {{
    body {{ background:#fff; padding:16px; }}
    .card {{ box-shadow:none; }}
  }}
</style></head><body>
<h1>📉 Burndown Chart</h1>
<div class="meta">{sprint_label}{' &nbsp;·&nbsp; ' + date_range if date_range else ''}</div>
<div class="card">
  {svg}
  <div class="stats">
    <div>
      <div class="stat-lbl">Total Points</div>
      <div class="stat-val blue">{total_pts}</div>
    </div>
    <div>
      <div class="stat-lbl">Points Done</div>
      <div class="stat-val green">{done_pts}</div>
    </div>
    <div>
      <div class="stat-lbl">Remaining</div>
      <div class="stat-val">{total_pts - done_pts}</div>
    </div>
    <div>
      <div class="stat-lbl">Completion</div>
      <div class="stat-val {'green' if pct_done >= 80 else 'blue'}">{pct_done}%</div>
    </div>
    <div>
      <div class="stat-lbl">Stories Done</div>
      <div class="stat-val">{n_done} / {len(self._issues)}</div>
    </div>
  </div>
</div>
</body></html>"""

        self._rpt_burndown_browser.setHtml(self._dark_html(html))
        self._reports_html_map[4] = html  # export uses original light HTML
        self._reports_html = html
        self._rpt_save_btn.setEnabled(True)
        self._status(f"✓ Burndown — {total_pts} pts total, {done_pts} done ({pct_done}%).")

    def _reports_save_html(self):
        html = self._reports_html_map.get(self._reports_tabs.currentIndex(), "")
        if not html:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "sprintmate-report.html", "HTML Files (*.html)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                self._status(f"✓ Report saved to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Failed", str(e))

    # ── Archive ───────────────────────────────────────────────────────────────
    def _open_archive(self):
        if not self._issues:
            return

        # Build a picker dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Archive Stories")
        dlg.setMinimumSize(640, 480)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🗄  ARCHIVE STORIES")
        title.setObjectName("heading")
        layout.addWidget(title)

        hint = QLabel(
            "Select stories to archive. Archived issues become read-only and are "
            "removed from boards and search results. They can be restored from Jira admin."
        )
        hint.setObjectName("dim")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        search = QLineEdit()
        search.setPlaceholderText("Search by key or summary…")
        layout.addWidget(search)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["", "KEY", "SUMMARY", "ASSIGNEE", "STATUS"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)
        table.horizontalHeader().setSortIndicatorShown(True)

        checkboxes = []
        for iss in sorted(self._issues, key=lambda i: i.get("key", "")):
            f = iss.get("fields", {})
            key = iss.get("key", "")
            summary = f.get("summary", "")
            status = (f.get("status") or {}).get("name", "—")
            aobj = f.get("assignee") or {}
            assignee = aobj.get("displayName") or aobj.get("name") or "—"
            r = table.rowCount()
            table.insertRow(r)

            cb_item = QTableWidgetItem()
            cb_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            cb_item.setCheckState(Qt.CheckState.Unchecked)
            table.setItem(r, 0, cb_item)

            key_item = QTableWidgetItem(key)
            key_item.setForeground(QColor(ACCENT_CYAN))
            table.setItem(r, 1, key_item)
            table.setItem(r, 2, QTableWidgetItem(summary))
            a_item = QTableWidgetItem(assignee)
            a_item.setForeground(QColor(TEXT_SEC))
            table.setItem(r, 3, a_item)
            s_item = QTableWidgetItem(status)
            s_item.setForeground(QColor(STATUS_COLORS.get(status, TEXT_SEC)))
            table.setItem(r, 4, s_item)
            table.setRowHeight(r, 36)
            checkboxes.append((cb_item, key))

        layout.addWidget(table, 1)

        def _filter(text):
            term = text.lower()
            for row in range(table.rowCount()):
                k = (table.item(row, 1).text() if table.item(row, 1) else "").lower()
                s = (table.item(row, 2).text() if table.item(row, 2) else "").lower()
                a = (table.item(row, 3).text() if table.item(row, 3) else "").lower()
                table.setRowHidden(row, bool(term) and term not in k and term not in s and term not in a)

        search.textChanged.connect(_filter)

        sel_lbl = QLabel("0 stories selected")
        sel_lbl.setObjectName("dim")
        layout.addWidget(sel_lbl)

        def _update_count():
            n = sum(1 for cb, _ in checkboxes if cb.checkState() == Qt.CheckState.Checked)
            sel_lbl.setText(f"{n} stor{'ies' if n != 1 else 'y'} selected")
            archive_btn_dlg.setEnabled(n > 0)

        table.itemChanged.connect(lambda _: _update_count())

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        archive_btn_dlg = btns.button(QDialogButtonBox.StandardButton.Ok)
        archive_btn_dlg.setText("🗄  Archive Selected")
        archive_btn_dlg.setObjectName("save_btn")
        archive_btn_dlg.setEnabled(False)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        keys_to_archive = [key for cb, key in checkboxes if cb.checkState() == Qt.CheckState.Checked]
        if not keys_to_archive:
            return

        confirm = QMessageBox.question(
            self, "Confirm Archive",
            f"Archive {len(keys_to_archive)} stor{'ies' if len(keys_to_archive) != 1 else 'y'}?\n\n"
            "Archived issues become read-only and are removed from boards and search results.\n"
            "They can be restored later from Jira administration.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self._busy(True)
        self._status(f"Archiving {len(keys_to_archive)} issue(s)…")

        def _do_archive():
            return self._client.archive_issues(keys_to_archive)

        def _on_done(result):
            self._busy(False)
            errors = []
            if isinstance(result, dict):
                errors = result.get("errors", []) or result.get("errorMessages", [])
            n_ok = len(keys_to_archive) - len(errors)
            if not errors:
                QMessageBox.information(
                    self, "Archived",
                    f"✓ Successfully archived {n_ok} issue(s).\n\n"
                    "Archived issues are read-only and removed from boards and search results. "
                    "They can be restored from Jira administration."
                )
                self._status(f"✓ Archived {n_ok} issue(s).")
            else:
                detail = "\n".join(str(e) for e in errors[:10])
                QMessageBox.warning(
                    self, "Archive — Partial Result",
                    f"✓ {n_ok} archived.\n✗ {len(errors)} error(s):\n{detail}"
                )
                self._status(f"⚠ Archived {n_ok}, {len(errors)} error(s).")
            # Remove archived keys from the local issue list immediately so they
            # disappear from the table even if Jira's index hasn't caught up yet.
            archived_set = set(keys_to_archive)
            self._issues = [i for i in self._issues if i.get("key") not in archived_set]
            self._populate_table(self._issues)
            self._update_velocity_bar()
            self._populate_assignee_filter()
            self.story_count_lbl.setText(f"{len(self._issues)} stories")
            # Clear edit panel if the selected story was archived
            if self.edit_panel.current_key in archived_set:
                self.edit_panel.current_key = None
                self.edit_panel.title_lbl.setText("Select a story to edit")
                self.edit_panel.key_lbl.setText("")
                self.edit_panel.status_badge.setText("")
                self.edit_panel.save_btn.setEnabled(False)
                self.edit_panel.attach_btn.setEnabled(False)
                self.edit_panel.clone_btn.setEnabled(False)
                self.edit_panel.open_jira_btn.setEnabled(False)
                self.edit_panel.copy_key_btn.setEnabled(False)

        self._spawn(_do_archive, on_result=_on_done,
                    on_error=lambda e: (
                        self._busy(False),
                        self._status("✗ Archive failed."),
                        QMessageBox.critical(self, "Archive Failed", str(e)),
                    ))

    # ── Edit / Delete Comment ─────────────────────────────────────────────────
    def _edit_comment(self, key: str):
        comments = self.edit_panel._comments_data
        if not comments:
            return

        # Show a picker if there are multiple comments
        if len(comments) == 1:
            chosen = comments[0]
        else:
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Edit Comment — {key}")
            dlg.setMinimumSize(560, 360)
            dlg.setStyleSheet(self.styleSheet())
            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(10)
            lbl = QLabel("Select the comment to edit:")
            lbl.setObjectName("subheading")
            layout.addWidget(lbl)
            lst = QListWidget()
            for c in reversed(comments):
                author = (c.get("author") or {}).get("displayName") or "Unknown"
                created = (c.get("created") or "")[:10]
                body = c.get("body", "")
                if isinstance(body, dict):
                    body = self.edit_panel._adf_to_text(body)
                preview = body.strip().replace("\n", " ")[:80] + ("…" if len(body) > 80 else "")
                item = QListWidgetItem(f"[{created}] {author}: {preview}")
                item.setData(Qt.ItemDataRole.UserRole, c)
                lst.addItem(item)
            lst.setCurrentRow(0)
            layout.addWidget(lst, 1)
            btns = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            btns.accepted.connect(dlg.accept)
            btns.rejected.connect(dlg.reject)
            layout.addWidget(btns)
            if dlg.exec() != QDialog.DialogCode.Accepted or not lst.currentItem():
                return
            chosen = lst.currentItem().data(Qt.ItemDataRole.UserRole)

        comment_id = chosen.get("id", "")
        body = chosen.get("body", "")
        if isinstance(body, dict):
            body = self.edit_panel._adf_to_text(body)

        # Edit dialog
        edit_dlg = QDialog(self)
        edit_dlg.setWindowTitle(f"Edit Comment — {key}")
        edit_dlg.setMinimumSize(520, 280)
        edit_dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(edit_dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        lbl = QLabel("Edit comment:")
        lbl.setObjectName("subheading")
        layout.addWidget(lbl)
        editor = QTextEdit()
        editor.setPlainText(body.strip())
        layout.addWidget(editor, 1)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Save Comment")
        btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("save_btn")
        btns.accepted.connect(edit_dlg.accept)
        btns.rejected.connect(edit_dlg.reject)
        layout.addWidget(btns)

        if edit_dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new_text = editor.toPlainText().strip()
        if not new_text:
            QMessageBox.warning(self, "Empty Comment", "Comment text cannot be empty.")
            return

        self._busy(True)
        self._status(f"Updating comment on {key}…")
        self._spawn(
            self._client.edit_comment, key, comment_id, new_text,
            on_result=lambda _: (
                self._busy(False),
                self._status(f"✓ Comment on {key} updated."),
                self._load_sprint_issues(reselect_key=key),
            ),
            on_error=lambda e: (
                self._busy(False),
                self._status("✗ Failed to update comment."),
                QMessageBox.critical(self, "Edit Failed", str(e)),
            ),
        )

    def _delete_comment(self, key: str):
        comments = self.edit_panel._comments_data
        if not comments:
            return

        if len(comments) == 1:
            chosen = comments[0]
        else:
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Delete Comment — {key}")
            dlg.setMinimumSize(560, 360)
            dlg.setStyleSheet(self.styleSheet())
            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(10)
            lbl = QLabel("Select the comment to delete:")
            lbl.setObjectName("subheading")
            layout.addWidget(lbl)
            lst = QListWidget()
            for c in reversed(comments):
                author = (c.get("author") or {}).get("displayName") or "Unknown"
                created = (c.get("created") or "")[:10]
                body = c.get("body", "")
                if isinstance(body, dict):
                    body = self.edit_panel._adf_to_text(body)
                preview = body.strip().replace("\n", " ")[:80] + ("…" if len(body) > 80 else "")
                item = QListWidgetItem(f"[{created}] {author}: {preview}")
                item.setData(Qt.ItemDataRole.UserRole, c)
                lst.addItem(item)
            lst.setCurrentRow(0)
            layout.addWidget(lst, 1)
            btns = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            btns.button(QDialogButtonBox.StandardButton.Ok).setText("Select")
            btns.accepted.connect(dlg.accept)
            btns.rejected.connect(dlg.reject)
            layout.addWidget(btns)
            if dlg.exec() != QDialog.DialogCode.Accepted or not lst.currentItem():
                return
            chosen = lst.currentItem().data(Qt.ItemDataRole.UserRole)

        comment_id = chosen.get("id", "")
        body = chosen.get("body", "")
        if isinstance(body, dict):
            body = self.edit_panel._adf_to_text(body)
        author = (chosen.get("author") or {}).get("displayName") or "Unknown"
        preview = body.strip().replace("\n", " ")[:120]

        confirm = QMessageBox.question(
            self, "Delete Comment",
            f"Permanently delete this comment by {author}?\n\n\"{preview}\"\n\n"
            "This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self._busy(True)
        self._status(f"Deleting comment on {key}…")
        self._spawn(
            self._client.delete_comment, key, comment_id,
            on_result=lambda _: (
                self._busy(False),
                self._status(f"✓ Comment on {key} deleted."),
                self._load_sprint_issues(reselect_key=key),
            ),
            on_error=lambda e: (
                self._busy(False),
                self._status("✗ Failed to delete comment."),
                QMessageBox.critical(self, "Delete Failed", str(e)),
            ),
        )

    # ── Clone Issue ───────────────────────────────────────────────────────────
    def _clone_issue(self, issue: dict):
        f          = issue.get("fields", {})
        src_key    = issue.get("key", "")
        summary    = f.get("summary", "")
        desc_raw   = f.get("description") or {}
        desc_text  = self.edit_panel._adf_to_text(desc_raw) if isinstance(desc_raw, dict) else str(desc_raw or "")
        aobj       = f.get("assignee") or {}
        assignee   = aobj.get("name") or aobj.get("accountId") or ""
        assignee_display = aobj.get("displayName") or assignee
        itype      = (f.get("issuetype") or {}).get("name", "Story")

        # Determine available instances
        s = self._settings
        current_mode  = s.get("mode", JiraClient.MODE_SECONDARY)
        other_mode    = JiraClient.MODE_PRIMARY if current_mode == JiraClient.MODE_SECONDARY else JiraClient.MODE_SECONDARY
        other_url     = s.get(f"{'primary' if other_mode == JiraClient.MODE_PRIMARY else 'secondary'}_url", "")
        other_token   = s.get(f"{'primary' if other_mode == JiraClient.MODE_PRIMARY else 'secondary'}_token", "")
        other_label   = self._instance_label(other_mode)
        current_label = self._instance_label(current_mode)
        has_other     = bool(other_url and other_token)

        # ── Dialog ────────────────────────────────────────────────────────────
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Clone {src_key}")
        dlg.setMinimumSize(560, 520)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title_lbl = QLabel(f"⎘  CLONE  {src_key}")
        title_lbl.setObjectName("heading")
        layout.addWidget(title_lbl)

        # ── Instance selector ─────────────────────────────────────────────────
        inst_grp = QGroupBox("TARGET INSTANCE")
        inst_layout = QHBoxLayout(inst_grp)
        inst_combo = QComboBox()
        inst_combo.addItem(f"Current ({current_label})", userData="current")
        if has_other:
            inst_combo.addItem(other_label, userData="other")
        inst_layout.addWidget(inst_combo)
        layout.addWidget(inst_grp)

        # ── Project selector ──────────────────────────────────────────────────
        proj_grp = QGroupBox("TARGET PROJECT")
        proj_layout = QHBoxLayout(proj_grp)
        proj_combo = QComboBox()
        proj_combo.setMinimumWidth(300)
        proj_combo.addItem("Loading projects…")
        proj_combo.setEnabled(False)
        proj_layout.addWidget(proj_combo)
        layout.addWidget(proj_grp)

        # ── Fields ────────────────────────────────────────────────────────────
        fields_grp = QGroupBox("FIELDS TO CLONE")
        fields_layout = QVBoxLayout(fields_grp)
        fields_layout.setSpacing(8)

        sum_lbl = QLabel("Summary")
        sum_lbl.setObjectName("dim")
        fields_layout.addWidget(sum_lbl)
        sum_edit = QLineEdit(f"[Clone] {summary}")
        fields_layout.addWidget(sum_edit)

        desc_lbl = QLabel("Description")
        desc_lbl.setObjectName("dim")
        fields_layout.addWidget(desc_lbl)
        desc_edit = QTextEdit()
        desc_edit.setPlainText(desc_text)
        desc_edit.setMaximumHeight(100)
        fields_layout.addWidget(desc_edit)

        assignee_lbl = QLabel("Assignee (username)")
        assignee_lbl.setObjectName("dim")
        fields_layout.addWidget(assignee_lbl)
        assignee_edit = QLineEdit(assignee)
        assignee_edit.setPlaceholderText(f"e.g. {assignee_display or 'jsmith'}")
        fields_layout.addWidget(assignee_edit)

        layout.addWidget(fields_grp)

        # ── Status label ──────────────────────────────────────────────────────
        status_lbl = QLabel("")
        status_lbl.setObjectName("dim")
        layout.addWidget(status_lbl)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        clone_ok = btns.button(QDialogButtonBox.StandardButton.Ok)
        clone_ok.setText("⎘  Clone")
        clone_ok.setObjectName("save_btn")
        clone_ok.setEnabled(False)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        # ── Load projects for the selected instance ───────────────────────────
        _project_cache: dict[str, list] = {}

        def _load_projects_for_instance():
            inst = inst_combo.currentData()
            if inst in _project_cache:
                _populate_projects(_project_cache[inst])
                return
            proj_combo.clear()
            proj_combo.addItem("Loading…")
            proj_combo.setEnabled(False)
            clone_ok.setEnabled(False)
            status_lbl.setText("Fetching projects…")
            if inst == "current":
                client = self._client
            else:
                client = JiraClient(other_url, other_token, other_mode)

            worker = Worker(client.get_projects)
            worker.result.connect(lambda r: _on_projects(r, inst))
            worker.error.connect(lambda e: status_lbl.setText(f"⚠ {e}"))
            worker.start()
            dlg._workers = getattr(dlg, "_workers", [])
            dlg._workers.append(worker)

        def _on_projects(projects, inst_key):
            _project_cache[inst_key] = projects
            _populate_projects(projects)

        def _populate_projects(projects):
            proj_combo.clear()
            if not projects:
                proj_combo.addItem("No projects found")
                status_lbl.setText("⚠ No projects available.")
                return
            for p in sorted(projects, key=lambda x: x.get("name", "")):
                proj_combo.addItem(f"{p.get('key','')} — {p.get('name','')}", userData=p.get("key",""))
            proj_combo.setEnabled(True)
            clone_ok.setEnabled(True)
            status_lbl.setText("")

        inst_combo.currentIndexChanged.connect(lambda _: _load_projects_for_instance())
        _load_projects_for_instance()

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        target_project = proj_combo.currentData()
        if not target_project:
            return

        new_summary  = sum_edit.text().strip() or f"[Clone] {summary}"
        new_desc     = desc_edit.toPlainText().strip()
        new_assignee = assignee_edit.text().strip()
        inst         = inst_combo.currentData()
        target_label = proj_combo.currentText()

        # Build the client for the target
        if inst == "current":
            target_client = self._client
        else:
            target_client = JiraClient(other_url, other_token, other_mode)

        self._busy(True)
        self._status(f"Cloning {src_key} → {target_project}…")

        def _do_clone():
            return target_client.clone_issue(
                project_key=target_project,
                summary=new_summary,
                description=new_desc,
                assignee_name=new_assignee,
                issue_type=itype,
            )

        def _on_done(result):
            self._busy(False)
            new_key = result.get("key", "—")
            new_url = f"{target_client.base_url}/browse/{new_key}"

            msg = QMessageBox(self)
            msg.setWindowTitle("Clone Successful")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(
                f"✓ <b>{src_key}</b> cloned successfully.\n\n"
                f"New issue: <b>{new_key}</b>\n"
                f"Project: {target_label}\n"
                f"Instance: {other_label if inst == 'other' else current_label}"
            )
            copy_btn = msg.addButton("Copy Key", QMessageBox.ButtonRole.ActionRole)
            open_btn = msg.addButton("Open in Jira", QMessageBox.ButtonRole.ActionRole)
            msg.addButton(QMessageBox.StandardButton.Ok)
            msg.exec()

            if msg.clickedButton() == copy_btn:
                QApplication.clipboard().setText(new_key)
                self._status(f"✓ Cloned as {new_key} — key copied to clipboard.")
            elif msg.clickedButton() == open_btn:
                webbrowser.open(new_url)
                self._status(f"✓ Cloned as {new_key} — opened in browser.")
            else:
                self._status(f"✓ {src_key} cloned as {new_key}.")

        self._spawn(
            _do_clone,
            on_result=_on_done,
            on_error=lambda e: (
                self._busy(False),
                self._status("✗ Clone failed."),
                QMessageBox.critical(self, "Clone Failed", str(e)),
            ),
        )

    def _check_for_updates(self):
        self._status("Checking for updates…")
        self._spawn(
            self._fetch_remote_version,
            on_result=self._on_update_result,
            on_error=lambda e: QMessageBox.warning(
                self, "Update Check Failed",
                f"Could not reach GitHub:\n{e}"),
        )

    @staticmethod
    def _fetch_remote_version() -> str:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            GITHUB_RAW_URL,
            headers={"User-Agent": f"SprintMate/{APP_VERSION}"},
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace")
                m = re.match(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', line)
                if m:
                    return m.group(1)
        raise RuntimeError("APP_VERSION not found in remote file.")

    def _on_update_result(self, remote_version: str):
        local = APP_VERSION
        self._status(f"Update check complete — remote: {remote_version}  local: {local}")
        if remote_version == local:
            QMessageBox.information(
                self, "Up to Date",
                f"You are running the latest version ({local})."
            )
        else:
            reply = QMessageBox.question(
                self, "Update Available",
                f"A new version is available.\n\n"
                f"  Installed:  {local}\n"
                f"  Available:  {remote_version}\n\n"
                "Open the repository page to download?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                repo_url = "/".join(GITHUB_RAW_URL.split("/")[:5]).replace(
                    "raw.githubusercontent.com", "github.com"
                )
                webbrowser.open(repo_url)

    def _show_about(self):
        repo_url = "/".join(GITHUB_RAW_URL.split("/")[:5]).replace(
            "raw.githubusercontent.com", "github.com"
        )
        QMessageBox.about(
            self, "About SprintMate",
            f"<b>SprintMate</b> v{APP_VERSION}<br><br>"
            "Jira sprint management desktop client.<br><br>"
            f"<a href='{repo_url}'>View on GitHub</a>",
        )

    def closeEvent(self, event):
        in_flight = sum(1 for w in self._workers if w.isRunning())
        if in_flight:
            reply = QMessageBox.question(
                self,
                "Operations In Progress",
                f"{in_flight} background operation(s) are still running.\n"
                "Closing now may leave Jira in an inconsistent state. Close anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        elif self.edit_panel.save_btn.isEnabled():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes in the edit panel.\n"
                "Close and discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        self._cancel_workers()
        self._save_settings()
        event.accept()


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SprintMate")
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(DARK_BG))
    palette.setColor(QPalette.ColorRole.Base, QColor(PANEL_BG))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_PRI))
    app.setPalette(palette)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
