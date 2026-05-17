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
    QTabWidget, QDateEdit, QFileDialog
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QDate, QTimer, QSettings
)
from PyQt6.QtGui import (
    QColor, QPalette, QKeySequence, QShortcut
)


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
ACCENT_ORG   = "#F78166"
TEXT_PRI     = "#E6EDF3"
TEXT_SEC     = "#8B949E"
TEXT_DIM     = "#484F58"
HOVER_BG     = "#21262D"
SEL_BG       = "#1F3350"

APP_VERSION  = "2.11.7"

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
    color: {ACCENT_ORG};
    border: 1px solid {ACCENT_ORG};
}}
QPushButton#danger:hover {{
    background-color: {ACCENT_ORG};
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
            "sprint", "closedSprints", "customfield_10020"
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
        except Exception:
            return []

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
        for p in ["Medium", "Highest", "High", "Low", "Lowest"]:
            self.priority_combo.addItem(p, p)
        form.addRow("Priority:", self.priority_combo)

        # Story points (Fibonacci) with amber warning for 13 and 21
        FIBONACCI = [0, 1, 3, 5, 8, 13, 21]
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
        self._warn_lbl.setStyleSheet(f"color: {ACCENT_ORG}; font-size: 11px;")
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
        valid_priorities = {"Highest", "High", "Medium", "Low", "Lowest"}
        if raw_pri and raw_pri in valid_priorities:
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
            fg = QColor(TEXT_PRI) if is_valid else QColor(ACCENT_ORG)

            def cell(text, align=Qt.AlignmentFlag.AlignLeft):
                item = QTableWidgetItem(str(text))
                item.setForeground(fg)
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
                status_item.setForeground(QColor(ACCENT_ORG))
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

            cross_key  = (cross_map or {}).get(key, "")
            cross_item = QTableWidgetItem(cross_key if cross_key else "—")
            cross_item.setForeground(QColor(ACCENT_CYAN if cross_key else TEXT_DIM))
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

        self.table.currentRowChanged.connect(self._on_row_changed)

        if unmatched:
            warn = QLabel(f"⚠  {len(unmatched)} keys not found in current sprint will be skipped.")
            warn.setStyleSheet(f"color: {ACCENT_ORG}; font-size: 11px;")
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

    def _on_row_changed(self, row: int):
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
        cross    = self._cross_map.get(key, "")
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
                "url":            settings.get("secondary_url", "https://jira.sde.sp.gc1.myngc.com/"),
                "token":          settings.get("secondary_token", ""),
                "token_expiry":   settings.get("secondary_token_expiry", ""),
                "default_project": settings.get("secondary_default_project", ""),
                "default_board":  settings.get("secondary_default_board", ""),
                "filter_projects": settings.get("secondary_filter_projects", ""),
                "filter_boards":  settings.get("secondary_filter_boards", ""),
            },
            JiraClient.MODE_PRIMARY: {
                "url":            settings.get("primary_url", "https://jira.northgrum.com/"),
                "token":          settings.get("primary_token", ""),
                "token_expiry":   settings.get("primary_token_expiry", ""),
                "default_project": settings.get("primary_default_project", ""),
                "default_board":  settings.get("primary_default_board", ""),
                "filter_projects": settings.get("primary_filter_projects", ""),
                "filter_boards":  settings.get("primary_filter_boards", ""),
            },
        }
        self._set_mode(settings.get("mode", JiraClient.MODE_SECONDARY))

    def _set_mode(self, mode: str):
        if mode:
            if mode.lower() == "ACyD".lower():
                mode = JiraClient.MODE_PRIMARY
            if mode.lower() == "sentinel":
                mode = JiraClient.MODE_SECONDARY
        if hasattr(self, "_mode"):
            self._data[self._mode]["url"]   = self.url_edit.text().strip()
            self._data[self._mode]["token"] = self.token_edit.text().strip()
            self._data[self._mode]["token_expiry"] = self.expiry_edit.text().strip()
            self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()
            self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()
            self._data[self._mode]["filter_projects"] = self.filter_projects_edit.text().strip()
            self._data[self._mode]["filter_boards"]   = self.filter_boards_edit.text().strip()

        self._mode = mode
        is_secondary = mode == JiraClient.MODE_SECONDARY
        self.secondary_btn.setChecked(is_secondary)
        self.primary_btn.setChecked(not is_secondary)
        self.instance_lbl.setText(f"{'SECONDARY' if is_secondary else 'PRIMARY'} INSTANCE")

        self.url_edit.setText(self._data[mode]["url"])
        self.token_edit.setText(self._data[mode]["token"])
        self.expiry_edit.setText(self._data[mode].get("token_expiry", ""))
        self.default_project_edit.setText(self._data[mode]["default_project"])
        self.default_board_edit.setText(self._data[mode].get("default_board", ""))
        self.filter_projects_edit.setText(self._data[mode].get("filter_projects", ""))
        self.filter_boards_edit.setText(self._data[mode].get("filter_boards", ""))
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
        self.status_lbl.setStyleSheet(f"color: {ACCENT_ORG};")

    def _save_and_accept(self):
        self._data[self._mode]["url"]   = self.url_edit.text().strip()
        self._data[self._mode]["token"] = self.token_edit.text().strip()
        self._data[self._mode]["token_expiry"] = self.expiry_edit.text().strip()
        self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()
        self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()
        self._data[self._mode]["filter_projects"] = self.filter_projects_edit.text().strip()
        self._data[self._mode]["filter_boards"]   = self.filter_boards_edit.text().strip()
        self.accept()

    def get_settings(self):
        return {
            "mode":           self._mode,
            "secondary_url":   self._data[JiraClient.MODE_SECONDARY]["url"],
            "secondary_token": self._data[JiraClient.MODE_SECONDARY]["token"],
            "secondary_token_expiry": self._data[JiraClient.MODE_SECONDARY].get("token_expiry", ""),
            "primary_url":       self._data[JiraClient.MODE_PRIMARY]["url"],
            "primary_token":     self._data[JiraClient.MODE_PRIMARY]["token"],
            "primary_token_expiry": self._data[JiraClient.MODE_PRIMARY].get("token_expiry", ""),
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
    saved = pyqtSignal(str, dict, str, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.current_key = None
        self._members = []
        self._sprints = []
        self._transitions = []
        self._current_sprint_id = None
        self._snapshot = {}
        self._sp_field = "customfield_10016"
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
        hdr.addWidget(self.title_lbl, 1)
        hdr.addWidget(self.key_lbl)
        hdr.addWidget(self.copy_key_btn)
        hdr.addWidget(self.open_jira_btn)
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
        PRIORITIES = [
            ("— Keep current —", None),
            ("Highest", "Highest"),
            ("High", "High"),
            ("Medium", "Medium"),
            ("Low", "Low"),
            ("Lowest", "Lowest"),
        ]
        for label, val in PRIORITIES:
            self.priority_combo.addItem(label, val)
        form.addRow("Priority:", self.priority_combo)

        # Fibonacci story points with amber warning for 13 and 21
        FIBONACCI = [0, 1, 3, 5, 8, 13, 21]
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
        self._expand_comment_btn = QPushButton("⤢  Expand")
        self._expand_comment_btn.setFixedHeight(24)
        self._expand_comment_btn.setEnabled(False)
        self._expand_comment_btn.setToolTip("View the selected comment in full")
        self._expand_comment_btn.clicked.connect(self._expand_comment)
        history_layout.addWidget(self._expand_comment_btn)
        layout.addWidget(grp_history)

        # ── Comment ───────────────────────────────────────────────────────────
        grp_comment = QGroupBox("ADD COMMENT")
        comment_layout = QVBoxLayout(grp_comment)
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Type a comment to post…")
        self.comment_edit.setMaximumHeight(80)
        comment_layout.addWidget(self.comment_edit)
        layout.addWidget(grp_comment)

        layout.addStretch()

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
        current = self._snapshot_state()
        is_dirty = (current != self._snapshot)
        self.save_btn.setEnabled(is_dirty)
        if is_dirty:
            self.save_btn.setToolTip("Unsaved changes")
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

        if getattr(self, "_pending_assignee", None):
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
        self._snapshot = self._snapshot_state()
        self.save_btn.setEnabled(False)
        self.save_btn.setToolTip("No changes to save")
        self.copy_key_btn.setEnabled(True)
        self.open_jira_btn.setEnabled(True)

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

        pts = fields.get(self._sp_field) or fields.get("customfield_10016") or fields.get("story_points")
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
        else:
            self.comment_history.setPlainText("")
            self._full_comment_text = ""
            self._expand_comment_btn.setEnabled(False)

    def _copy_key(self):
        if self.current_key:
            QApplication.clipboard().setText(self.current_key)
            self.copy_key_btn.setText("✓")
            QTimer.singleShot(1500, lambda: self.copy_key_btn.setText("⎘"))

    def _expand_comment(self):
        full_text = self._full_comment_text if hasattr(self, "_full_comment_text") else ""
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

    def _adf_to_text(self, node: dict) -> str:
        if not node:
            return ""
        parts = []
        if node.get("type") == "text":
            parts.append(node.get("text", ""))
        for child in node.get("content", []):
            parts.append(self._adf_to_text(child))
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
        self._sp_field = "customfield_10016"
        self._fl_field = "customfield_10100"

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
            mode_label = "SECONDARY" if mode == JiraClient.MODE_SECONDARY else "PRIMARY"
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

        self.connect_btn = QPushButton("⚙  Configure")
        self.connect_btn.setObjectName("toolbar_btn")
        self.connect_btn.clicked.connect(self._open_settings)
        tb_layout.addWidget(self.connect_btn)

        self.refresh_btn = QPushButton("↺  Refresh")
        self.refresh_btn.setObjectName("toolbar_btn")
        self.refresh_btn.clicked.connect(self._load_sprint_issues)
        self.refresh_btn.setEnabled(False)
        tb_layout.addWidget(self.refresh_btn)

        root.addWidget(topbar)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(4)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: {DARK_BG}; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT_BLUE}; }}
        """)
        root.addWidget(self.progress)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setVisible(False)
        root.addWidget(self.tabs, 1)

        stories_tab = QWidget()
        stories_layout = QVBoxLayout(stories_tab)
        stories_layout.setContentsMargins(0, 0, 0, 0)
        stories_layout.setSpacing(0)

        filterbar = QFrame()
        filterbar.setStyleSheet(f"background-color: {PANEL_BG}; border-bottom: 1px solid {BORDER};")
        fb_layout = QHBoxLayout(filterbar)
        fb_layout.setContentsMargins(20, 8, 20, 8)
        fb_layout.setSpacing(12)

        fb_layout.addWidget(QLabel("PROJECT"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(180)
        self.project_combo.setEnabled(False)
        self.project_combo.currentIndexChanged.connect(self._on_project_changed)
        fb_layout.addWidget(self.project_combo)

        fb_layout.addWidget(QLabel("BOARD"))
        self.board_combo = QComboBox()
        self.board_combo.setMinimumWidth(160)
        self.board_combo.setEnabled(False)
        self.board_combo.currentIndexChanged.connect(self._on_board_changed)
        fb_layout.addWidget(self.board_combo)

        fb_layout.addWidget(QLabel("SPRINT"))
        self.sprint_combo = QComboBox()
        self.sprint_combo.setMinimumWidth(200)
        self.sprint_combo.setEnabled(False)
        fb_layout.addWidget(self.sprint_combo)

        self.load_btn = QPushButton("Load Stories")
        self.load_btn.setObjectName("toolbar_btn")
        self.load_btn.clicked.connect(self._load_sprint_issues)
        self.load_btn.setEnabled(False)
        fb_layout.addWidget(self.load_btn)

        self.new_story_btn = QPushButton("＋  New Story")
        self.new_story_btn.setObjectName("toolbar_btn")
        self.new_story_btn.clicked.connect(self._open_new_story)
        self.new_story_btn.setEnabled(False)
        fb_layout.addWidget(self.new_story_btn)

        self.bulk_create_btn = QPushButton("＋＋  Bulk Create")
        self.bulk_create_btn.setObjectName("toolbar_btn")
        self.bulk_create_btn.setToolTip("Create multiple stories from a CSV file")
        self.bulk_create_btn.clicked.connect(self._open_bulk_create)
        self.bulk_create_btn.setEnabled(False)
        fb_layout.addWidget(self.bulk_create_btn)

        self.import_btn = QPushButton("📄  Import")
        self.import_btn.setObjectName("toolbar_btn")
        self.import_btn.clicked.connect(self._import_comments)
        self.import_btn.setEnabled(False)
        fb_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("⬇  Export")
        self.export_btn.setObjectName("toolbar_btn")
        self.export_btn.clicked.connect(self._export_stories)
        self.export_btn.setEnabled(False)
        fb_layout.addWidget(self.export_btn)
        fb_layout.addStretch()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter stories…")
        self.search_edit.textChanged.connect(self._filter_table)
        fb_layout.addWidget(self.search_edit)

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
        # ── Persistent sprint label ───────────────────────────────────────────
        self.sprint_lbl = QLabel("")
        self.sprint_lbl.setObjectName("dim")
        self.sprint_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        count_row.addWidget(self.sprint_lbl)
        left_layout.addLayout(count_row)

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
        # ── Row right-click context menu ──────────────────────────────────────
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_row_context_menu)
        self._apply_default_columns()
        left_layout.addWidget(self.table)

        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 16, 16, 16)
        self.edit_panel = StoryEditPanel()
        self.edit_panel.saved.connect(self._on_save_story)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.edit_panel)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: transparent; }}")
        right_layout.addWidget(scroll)
        splitter.addWidget(right)

        splitter.setSizes([680, 480])
        stories_layout.addWidget(splitter, 1)
        self.tabs.addTab(stories_tab, "◈  STORIES")

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

        pts_raw = fields.get(sp_field) or fields.get("customfield_10016")
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
    def _show_row_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        key_item = self.table.item(row, 0)
        if not key_item:
            return
        key = key_item.text()

        menu = QMenu(self)
        open_action  = menu.addAction("⎋  Open in Jira")
        copy_key     = menu.addAction("⎘  Copy Key")
        copy_row     = menu.addAction("⎘  Copy Row")
        menu.addSeparator()
        copy_full    = menu.addAction("⎘  Copy Full Issue")

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
        self.sprint_lbl.setText("")
        self._issues = []
        self._users_cache = []
        self._apply_default_columns()

        self.export_btn.setEnabled(False)
        self.bulk_create_btn.setEnabled(False)
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
        qs.setValue("secondary_default_project",   s.get("secondary_default_project", ""))
        qs.setValue("secondary_default_board",     s.get("secondary_default_board", ""))
        qs.setValue("secondary_filter_projects",   s.get("secondary_filter_projects", ""))
        qs.setValue("secondary_filter_boards",     s.get("secondary_filter_boards", ""))
        qs.setValue("primary_url",                   s.get("primary_url", ""))
        qs.setValue("primary_token_expiry",          s.get("primary_token_expiry", ""))
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

    def _load_settings(self) -> dict:
        qs = QSettings("SprintMate", "SprintMate")
        return {
            "mode":                       qs.value("mode", JiraClient.MODE_SECONDARY),
            "secondary_url":               qs.value("secondary_url", ""),
            "secondary_token":             self._load_token("secondary", qs.value("secondary_token", "")),
            "secondary_token_expiry":      qs.value("secondary_token_expiry", ""),
            "secondary_default_project":   qs.value("secondary_default_project", ""),
            "secondary_default_board":     qs.value("secondary_default_board", ""),
            "secondary_filter_projects":   qs.value("secondary_filter_projects", ""),
            "secondary_filter_boards":     qs.value("secondary_filter_boards", ""),
            "primary_url":                   qs.value("primary_url", ""),
            "primary_token":                 self._load_token("primary", qs.value("primary_token", "")),
            "primary_token_expiry":          qs.value("primary_token_expiry", ""),
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
            self._status("  |  ".join(warnings))

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
            mode_label = "SECONDARY" if mode == JiraClient.MODE_SECONDARY else "PRIMARY"
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

        mode_label = "SECONDARY" if new_mode == JiraClient.MODE_SECONDARY else "PRIMARY"
        self.mode_indicator.setText(f"◈  {mode_label}")
        self._save_settings()
        self._check_token_expiry()
        self._status(f"Switched to {mode_label} — reloading projects…")
        self._clear_sprint_view()
        self._load_projects()

    # ── Loading helpers ───────────────────────────────────────────────────────
    def _busy(self, on: bool):
        self.progress.setVisible(on)

    def _status(self, msg: str):
        self.status_bar.showMessage(msg)

    _MAX_WORKERS = 5

    def _spawn(self, fn, *args, on_result=None, on_error=None):
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
            w.error.connect(lambda e: (self._busy(False), self._status(f"Error: {e}"),
                                       QMessageBox.critical(self, "Error", e)))
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

    def _on_assignees_load_error(self, e: str):
        self._status("⚠ Could not load assignees (access restricted)")

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
            on_result=lambda types: self.edit_panel.set_issue_types(types),
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
        self.edit_panel.set_sprints(sprints)

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
        mode = self._settings.get("mode", JiraClient.MODE_SECONDARY)
        mode_label = "SECONDARY" if mode == JiraClient.MODE_SECONDARY else "PRIMARY"
        sprint_label = self.sprint_combo.currentText()
        self._busy(True)
        self._status(f"Loading stories from {mode_label} — {sprint_label}…")
        self._spawn(
            self._client.get_sprint_issues, bid, sid,
            on_result=self._on_issues_loaded,
        )

    def _on_issues_loaded(self, issues):
        self._busy(False)
        self._issues = issues
        self._populate_table(issues)
        self._status(f"Loaded {len(issues)} stories.")
        self.story_count_lbl.setText(f"{len(issues)} stories")
        # Update persistent sprint label
        project = self.project_combo.currentText().split("—")[0].strip()
        board   = self.board_combo.currentText()
        sprint  = self.sprint_combo.currentText()
        self.sprint_lbl.setText(f"{project}  ◈  {board}  ◈  {sprint}")
        self.new_story_btn.setEnabled(True)
        self.bulk_create_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        reselect = getattr(self, "_reselect_key", None)
        if reselect:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text() == reselect:
                    self.table.selectRow(row)
                    self.table.scrollToItem(item)
                    break
            self._reselect_key = None

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

    def _populate_table(self, issues):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self._apply_default_columns()
        self.search_edit.blockSignals(True)
        self.search_edit.clear()
        self.search_edit.blockSignals(False)

        status_colors = {
            "To Do":       TEXT_SEC,
            "In Progress": ACCENT_BLUE,
            "Done":        ACCENT_GREEN,
            "In Review":   ACCENT_CYAN,
            "Blocked":     ACCENT_ORG,
        }
        sp_field = self._sp_field
        fl_field = self.edit_panel._fl_field

        for issue in issues:
            f = issue.get("fields", {})
            row = self.table.rowCount()
            self.table.insertRow(row)

            key_item = QTableWidgetItem(issue["key"])
            key_item.setForeground(QColor(ACCENT_CYAN))
            self.table.setItem(row, COL_KEY, key_item)

            self.table.setItem(row, COL_SUMMARY, QTableWidgetItem(f.get("summary", "")))

            assignee = f.get("assignee")
            aname = assignee.get("displayName", "Unassigned") if assignee else "—"
            a_item = QTableWidgetItem(aname)
            a_item.setForeground(QColor(TEXT_SEC))
            self.table.setItem(row, COL_ASSIGNEE, a_item)

            status = f.get("status", {}).get("name", "")
            s_item = QTableWidgetItem(status)
            s_item.setForeground(QColor(status_colors.get(status, TEXT_SEC)))
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, COL_STATUS, s_item)

            due = f.get("duedate", "") or ""
            due_item = QTableWidgetItem(due[:10] if due else "—")
            due_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, COL_DUE_DATE, due_item)

            pts = f.get(sp_field) or f.get("customfield_10016") or f.get("story_points") or ""
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
        highlight_bg = QColor(ACCENT_BLUE).darker(180)
        for row in range(self.table.rowCount()):
            row_matches = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if not item:
                    continue
                cell_text = item.text().lower()
                if term and term in cell_text:
                    row_matches = True
                    item.setBackground(highlight_bg)
                else:
                    item.setBackground(QColor(0, 0, 0, 0))
            self.table.setRowHidden(row, bool(term) and not row_matches)

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

        self.edit_panel.load_issue(issue)
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

                pts_raw = fields.get(sp_field) or fields.get("customfield_10016")
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
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Could not read file:\n{e}")
            return

        if path.lower().endswith(".csv"):
            parsed = self._parse_comments_csv(path)
        else:
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
                paired = entry.get("paired_key")
                if paired and paired in parsed:
                    if key in loaded_keys and paired not in loaded_keys:
                        cross_map[key] = paired
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
                matches = other_client.search_issues_jql(jql, fields="summary,assignee")

                if not matches:
                    jql_exact = f'summary = "{safe_summary}"'
                    matches = other_client.search_issues_jql(jql_exact, fields="summary,assignee")

                if matches:
                    best = _best_match(matches, file_summary, file_assignee)
                    if best:
                        cross_map[key] = best

        cross_keys = set(cross_map.keys())
        dlg = ImportCommentsDialog(parsed, loaded_keys, story_info, cross_keys, cross_map, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            to_post = dlg.get_comments()
            if to_post:
                n  = len(to_post)
                nc = len({k for k in to_post if k in cross_keys})
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

            paired_key = keys_found[1] if len(keys_found) >= 2 else None

            for key in keys_found[:2]:
                result[key] = {
                    "comment":    comment,
                    "summary":    summary,
                    "assignee":   assignee,
                    "paired_key": paired_key if paired_key != key else keys_found[0],
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
                    key     = (row.get(key_col)      or "").strip().upper()
                    summary = (row.get(summary_col)   or "").strip() if summary_col  else ""
                    assignee= (row.get(assignee_col)  or "").strip() if assignee_col else ""
                    comment = (row.get(comment_col)   or "").strip()
                    key2    = (row.get(key2_col)      or "").strip().upper() if key2_col else ""

                    if key2 and not re.match(KEY_RE, key2):
                        key2 = ""

                    if not key or not comment:
                        continue

                    paired = key2 or None
                    result[key] = {
                        "comment":    comment,
                        "summary":    summary,
                        "assignee":   assignee,
                        "paired_key": paired,
                    }
                    if paired:
                        result[paired] = {
                            "comment":    comment,
                            "summary":    summary,
                            "assignee":   assignee,
                            "paired_key": key,
                        }
        except Exception:
            pass
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
                    other_key = cross_map[key]
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
        self._busy(True)
        self._status(f"Saving {key}…")
        self._spawn(
            self._do_save, key, fields, comment, transition_id, target_sprint,
            on_result=lambda result: self._on_saved(key, result),
        )

    def _do_save(self, key, fields, comment, transition_id, target_sprint):
        pts_dropped = False
        try:
            self._client.update_issue(key, fields)
        except RuntimeError as e:
            sp = self._client.story_point_field_id
            err_str = str(e)
            if sp in err_str or "customfield_10016" in err_str:
                fields_no_pts = {k: v for k, v in fields.items() if k not in (sp, "customfield_10016")}
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
        self.edit_panel.save_btn.setToolTip("No changes to save")
        self._load_sprint_issues(reselect_key=key)

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
