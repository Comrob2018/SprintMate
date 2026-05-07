"""
SprintMate - PyQt6 Desktop Application
Team sprint story manager — assignees, story points, transitions, and more.
"""

import sys
import json
import base64
import urllib.request
import urllib.parse
import urllib.error
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QFrame, QScrollArea, QDialog, QDialogButtonBox, QMessageBox,
    QGroupBox, QFormLayout,
    QAbstractItemView, QProgressBar, QStatusBar,
    QTabWidget, QDateEdit
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QDate
)
from PyQt6.QtGui import (
    QColor, QPalette
)


# ── Colour palette ────────────────────────────────────────────────────────────
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

    MODE_CLOUD  = "cloud"
    MODE_DC     = "datacenter"

    def __init__(self, base_url: str, token: str, mode: str = MODE_DC, email: str = ""):
        self.base_url = base_url.rstrip("/")
        self.mode = mode
        # API version differs between Cloud and Data Center
        self.api_version = "3" if mode == self.MODE_CLOUD else "2"
        if mode == self.MODE_CLOUD:
            b64 = base64.b64encode(f"{email}:{token}".encode()).decode()
            auth = f"Basic {b64}"
        else:
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
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            raise RuntimeError(f"HTTP {e.code}: {msg}")

    def get_projects(self):
        result = self._request("GET", "project/search?maxResults=100&orderBy=name")
        return result.get("values", [])

    def get_boards(self, project_key: str):
        url = f"{self.base_url}/rest/agile/1.0/board?projectKeyOrId={project_key}"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()).get("values", [])

    def get_sprints(self, board_id: int):
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint?state=active,future&maxResults=20"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()).get("values", [])

    def get_sprint_issues(self, board_id: int, sprint_id: int):
        fields = ",".join([
            "summary", "assignee", "status", "priority", "description",
            "comment", "issuetype", "customfield_10016", "duedate",
            "sprint", "closedSprints", "customfield_10020"
        ])
        url = (f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}"
               f"/issue?maxResults=100&fields={fields}")
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()).get("issues", [])

    def get_issue_transitions(self, issue_key: str):
        return self._request("GET", f"issue/{issue_key}/transitions").get("transitions", [])

    def transition_issue(self, issue_key: str, transition_id: str):
        self._request("POST", f"issue/{issue_key}/transitions", {"transition": {"id": transition_id}})

    def get_issue_types(self, project_key: str):
        result = self._request("GET", f"project/{project_key}")
        return result.get("issueTypes", [])

    def get_priorities(self):
        result = self._request("GET", "priority")
        return result if isinstance(result, list) else []

    def move_to_sprint(self, issue_key: str, sprint_id: int):
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        body = json.dumps({"issues": [issue_key]}).encode()
        req = urllib.request.Request(url, data=body, headers=self.headers, method="POST")
        try:
            urllib.request.urlopen(req, timeout=15)
        except urllib.error.HTTPError as e:
            if e.code not in (200, 201, 204):
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode()}")

    def get_project_members(self, project_key: str):
        try:
            result = self._request("GET", f"user/assignable/search?project={project_key}&maxResults=100")
            return result if isinstance(result, list) else []
        except Exception:
            return []

    def update_issue(self, issue_key: str, fields: dict):
        self._request("PUT", f"issue/{issue_key}", {"fields": fields})

    def add_comment(self, issue_key: str, text: str):
        if self.mode == self.MODE_CLOUD:
            # Cloud API v3 requires ADF body
            body = {"body": {"type": "doc", "version": 1,
                             "content": [{"type": "paragraph",
                                          "content": [{"type": "text", "text": text}]}]}}
        else:
            # Data Center API v2 uses plain string
            body = {"body": text}
        self._request("POST", f"issue/{issue_key}/comment", body)

    def test_connection(self):
        return self._request("GET", "myself")

    def create_issue(self, project_key: str, summary: str, issue_type: str,
                     description: str = "", assignee_id: str = None,
                     priority: str = None, story_points: float = None,
                     sprint_id: int = None, due_date: str = None):
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        if description:
            if self.mode == self.MODE_CLOUD:
                fields["description"] = {
                    "type": "doc", "version": 1,
                    "content": [{"type": "paragraph",
                                 "content": [{"type": "text", "text": description}]}]
                }
            else:
                fields["description"] = description
        if assignee_id:
            fields["assignee"] = {"accountId": assignee_id} if self.mode == self.MODE_CLOUD                                   else {"name": assignee_id}
        if priority:
            fields["priority"] = {"name": priority}
        if story_points is not None:
            fields["customfield_10016"] = story_points
        if due_date:
            fields["duedate"] = due_date
        result = self._request("POST", "issue", {"fields": fields})
        # Move to sprint if specified
        if sprint_id and result.get("key"):
            self.move_to_sprint(result["key"], sprint_id)
        return result

    # ── User management ───────────────────────────────────────────────────────
    def get_project_roles(self, project_key: str):
        return self._request("GET", f"project/{project_key}/role")

    def get_role_members(self, project_key: str, role_id: int):
        return self._request("GET", f"project/{project_key}/role/{role_id}")

    def add_user_to_role(self, project_key: str, role_id: int, account_id: str):
        self._request("POST", f"project/{project_key}/role/{role_id}",
                      {"user": [account_id]})

    def remove_user_from_role(self, project_key: str, role_id: int, account_id: str):
        encoded = urllib.parse.quote(account_id)
        url = (f"{self.base_url}/rest/api/{self.api_version}/"
               f"project/{project_key}/role/{role_id}?user={encoded}")
        req = urllib.request.Request(url, headers=self.headers, method="DELETE")
        try:
            urllib.request.urlopen(req, timeout=15)
        except urllib.error.HTTPError as e:
            if e.code != 204:
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode()}")

    def search_users(self, query: str):
        encoded = urllib.parse.quote(query)
        result = self._request("GET", f"user/search?query={encoded}&maxResults=20")
        return result if isinstance(result, list) else []

    def invite_user(self, email: str, project_key: str, role_id: int):
        """Cloud only – create new user invite via Atlassian API."""
        # For Cloud: invite via /rest/api/3/user (creates account + sends invite email)
        body = {"emailAddress": email, "products": ["jira-software"],
                "applicationKeys": ["jira-software"]}
        try:
            user = self._request("POST", "user", body)
            account_id = user.get("accountId")
            if account_id:
                self.add_user_to_role(project_key, role_id, account_id)
            return user
        except Exception as e:
            raise RuntimeError(f"Invite failed: {e}")


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

        # Summary (required)
        self.summary_edit = QLineEdit()
        self.summary_edit.setPlaceholderText("Story summary (required)…")
        form.addRow("Summary *:", self.summary_edit)

        # Issue type
        self.type_combo = QComboBox()
        for it in issue_types:
            self.type_combo.addItem(it.get("name", "?"), it.get("name"))
        # Default to Story if present
        for i in range(self.type_combo.count()):
            if self.type_combo.itemText(i).lower() == "story":
                self.type_combo.setCurrentIndex(i)
                break
        form.addRow("Issue Type:", self.type_combo)

        # Priority
        self.priority_combo = QComboBox()
        for p in ["Medium", "Highest", "High", "Low", "Lowest"]:
            self.priority_combo.addItem(p, p)
        form.addRow("Priority:", self.priority_combo)

        # Story points (Fibonacci)
        self.points_combo = QComboBox()
        self.points_combo.addItem("— Not set —", None)
        for v in [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]:
            self.points_combo.addItem(str(v), v)
        form.addRow("Story Points:", self.points_combo)

        # Assignee
        self.assignee_combo = QComboBox()
        self.assignee_combo.addItem("— Unassigned —", None)
        for m in members:
            self.assignee_combo.addItem(m.get("displayName", "?"), m.get("accountId"))
        form.addRow("Assignee:", self.assignee_combo)

        # Sprint
        self.sprint_combo = QComboBox()
        self.sprint_combo.addItem("— Backlog (no sprint) —", None)
        for s in sprints:
            state = s.get("state", "")
            self.sprint_combo.addItem(f"[{state.upper()}] {s['name']}", s["id"])
        # Default to active sprint if any
        for i in range(self.sprint_combo.count()):
            if "[ACTIVE]" in self.sprint_combo.itemText(i):
                self.sprint_combo.setCurrentIndex(i)
                break
        form.addRow("Sprint:", self.sprint_combo)

        # Due date
        due_row = QHBoxLayout()
        self.due_check = QPushButton("Set due date")
        self.due_check.setCheckable(True)
        self.due_check.setFixedWidth(110)
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("yyyy-MM-dd")
        self.due_date.setDate(QDate.currentDate())
        self.due_date.setEnabled(False)
        self.due_check.toggled.connect(self.due_date.setEnabled)
        due_row.addWidget(self.due_check)
        due_row.addWidget(self.due_date)
        due_row.addStretch()
        form.addRow("Due Date:", due_row)

        layout.addLayout(form)

        # Description
        desc_grp = QGroupBox("DESCRIPTION")
        desc_layout = QVBoxLayout(desc_grp)
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Optional description…")
        self.desc_edit.setMinimumHeight(90)
        self.desc_edit.setMaximumHeight(140)
        desc_layout.addWidget(self.desc_edit)
        layout.addWidget(desc_grp)

        # Buttons
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
            "due_date":     self.due_date.date().toString("yyyy-MM-dd") if self.due_check.isChecked() else None,
            "description":  self.desc_edit.toPlainText().strip(),
        }


# ── Worker threads ────────────────────────────────────────────────────────────
class Worker(QThread):
    result = pyqtSignal(object)
    error  = pyqtSignal(str)

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
        self.setWindowTitle("Jira Connection Settings")
        self.setMinimumWidth(500)
        self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("⚙  SPRINTMATE — CONNECTION SETTINGS")
        title.setObjectName("heading")
        layout.addWidget(title)

        # Mode toggle
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(0)
        mode_lbl = QLabel("Mode: ")
        mode_lbl.setObjectName("dim")
        mode_layout.addWidget(mode_lbl)

        self.cloud_btn = QPushButton("☁  Jira Cloud")
        self.cloud_btn.setCheckable(True)
        self.cloud_btn.setFixedHeight(32)

        self.dc_btn = QPushButton("🏢  Data Center / Server")
        self.dc_btn.setCheckable(True)
        self.dc_btn.setFixedHeight(32)

        # Style the toggle group
        toggle_style = f"""
            QPushButton {{ border: 1px solid {BORDER}; border-radius: 0; padding: 4px 14px; }}
            QPushButton:checked {{ background-color: {ACCENT_BLUE}; color: #fff; border-color: {ACCENT_BLUE}; }}
            QPushButton:first-child {{ border-radius: 6px 0 0 6px; }}
            QPushButton:last-child  {{ border-radius: 0 6px 6px 0; }}
        """
        self.cloud_btn.setStyleSheet(toggle_style)
        self.dc_btn.setStyleSheet(toggle_style)
        self.cloud_btn.clicked.connect(lambda: self._set_mode("cloud"))
        self.dc_btn.clicked.connect(lambda: self._set_mode("datacenter"))

        mode_layout.addWidget(self.cloud_btn)
        mode_layout.addWidget(self.dc_btn)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Form
        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.url_edit = QLineEdit(settings.get("url", ""))
        self.form.addRow("Jira URL:", self.url_edit)

        # Cloud-only: email row
        self.email_lbl = QLabel("Email:")
        self.email_edit = QLineEdit(settings.get("email", ""))
        self.email_edit.setPlaceholderText("you@company.com")
        self.form.addRow(self.email_lbl, self.email_edit)

        # Token row (label changes per mode)
        self.token_lbl = QLabel("Token:")
        self.token_edit = QLineEdit(settings.get("token", ""))
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.form.addRow(self.token_lbl, self.token_edit)

        layout.addLayout(self.form)

        self.hint_lbl = QLabel("")
        self.hint_lbl.setObjectName("dim")
        self.hint_lbl.setWordWrap(True)
        layout.addWidget(self.hint_lbl)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._test)
        layout.addWidget(self.test_btn)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("dim")
        layout.addWidget(self.status_lbl)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        # Apply saved mode (default to datacenter)
        self._set_mode(settings.get("mode", JiraClient.MODE_DC))

    def _set_mode(self, mode: str):
        self._mode = mode
        is_cloud = mode == JiraClient.MODE_CLOUD
        self.cloud_btn.setChecked(is_cloud)
        self.dc_btn.setChecked(not is_cloud)

        # Show/hide email row
        self.email_lbl.setVisible(is_cloud)
        self.email_edit.setVisible(is_cloud)

        if is_cloud:
            self.url_edit.setPlaceholderText("https://yourteam.atlassian.net")
            self.token_lbl.setText("API Token:")
            self.token_edit.setPlaceholderText("Token from id.atlassian.com → Security → API tokens")
            self.hint_lbl.setText("☁  Cloud: uses email + API token (Basic auth, REST API v3)")
        else:
            self.url_edit.setPlaceholderText("https://jira.yourcompany.com")
            self.token_lbl.setText("Personal Access Token:")
            self.token_edit.setPlaceholderText("Token from Profile → Personal Access Tokens")
            self.hint_lbl.setText("🏢  Data Center/Server: uses Bearer PAT (REST API v2) — no email needed")

    def _test(self):
        self.status_lbl.setText("Testing…")
        self.status_lbl.setStyleSheet(f"color: {TEXT_SEC};")
        try:
            s = self.get_settings()
            client = JiraClient(s["url"], s["token"], s["mode"], s.get("email", ""))
            info = client.test_connection()
            name = info.get("displayName", "unknown")
            self.status_lbl.setText(f"✓ Connected as {name}")
            self.status_lbl.setStyleSheet(f"color: {ACCENT_GREEN};")
        except Exception as e:
            self.status_lbl.setText(f"✗ {str(e)[:100]}")
            self.status_lbl.setStyleSheet(f"color: {ACCENT_ORG};")

    def get_settings(self):
        return {
            "url":   self.url_edit.text().strip(),
            "email": self.email_edit.text().strip(),
            "token": self.token_edit.text().strip(),
            "mode":  self._mode,
        }


# ── Story edit panel ──────────────────────────────────────────────────────────
class StoryEditPanel(QFrame):
    saved = pyqtSignal(str, dict, str, object, object)   # issue_key, fields, comment, transition_id, target_sprint

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.current_key = None
        self._members = []
        self._sprints = []          # available sprints for move-to-sprint
        self._transitions = []      # available status transitions
        self._current_sprint_id = None
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
        hdr.addWidget(self.title_lbl, 1)
        hdr.addWidget(self.key_lbl)
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
        self.assignee_combo.setMinimumWidth(200)
        form.addRow("Assignee:", self.assignee_combo)

        # Issue type
        self.issuetype_combo = QComboBox()
        self.issuetype_combo.setMinimumWidth(160)
        form.addRow("Issue Type:", self.issuetype_combo)

        # Priority
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

        # Fibonacci story points
        FIBONACCI = [None, 0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        self.points_combo = QComboBox()
        self.points_combo.setMinimumWidth(140)
        self.points_combo.addItem("— Not set —", None)
        for v in FIBONACCI[1:]:
            self.points_combo.addItem(str(v), v)
        form.addRow("Story Points:", self.points_combo)

        # Sprint
        self.sprint_combo = QComboBox()
        self.sprint_combo.setMinimumWidth(200)
        form.addRow("Sprint:", self.sprint_combo)

        # Due date
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
        self.transition_combo.setMinimumWidth(200)
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

        # ── Comment ───────────────────────────────────────────────────────────
        grp_comment = QGroupBox("ADD COMMENT")
        comment_layout = QVBoxLayout(grp_comment)
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Type a comment to post…")
        self.comment_edit.setMaximumHeight(80)
        comment_layout.addWidget(self.comment_edit)
        layout.addWidget(grp_comment)

        layout.addStretch()

        # Save button
        self.save_btn = QPushButton("▶  SAVE CHANGES")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

    def _clear_due_date(self):
        self._due_set = False
        self.due_date.setStyleSheet(f"color: {TEXT_DIM};")
        self.due_date.setDate(QDate.currentDate())

    def set_members(self, members: list):
        self._members = members
        self.assignee_combo.clear()
        self.assignee_combo.addItem("— Unassigned —", None)
        for m in members:
            self.assignee_combo.addItem(m.get("displayName", "?"), m.get("accountId"))

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
        self.current_key = issue["key"]
        fields = issue.get("fields", {})

        self.key_lbl.setText(self.current_key)
        self.title_lbl.setText(fields.get("summary", ""))
        status = fields.get("status", {}).get("name", "")
        self.status_badge.setText(f"◈  {status.upper()}")

        # Assignee
        assignee = fields.get("assignee")
        self.assignee_combo.setCurrentIndex(0)
        if assignee:
            aid = assignee.get("accountId")
            for i in range(self.assignee_combo.count()):
                if self.assignee_combo.itemData(i) == aid:
                    self.assignee_combo.setCurrentIndex(i)
                    break

        # Issue type
        itype = fields.get("issuetype", {})
        itype_id = itype.get("id")
        self.issuetype_combo.setCurrentIndex(0)
        for i in range(self.issuetype_combo.count()):
            if self.issuetype_combo.itemData(i) == itype_id:
                self.issuetype_combo.setCurrentIndex(i)
                break

        # Priority
        priority = fields.get("priority", {})
        pname = priority.get("name") if priority else None
        self.priority_combo.setCurrentIndex(0)
        for i in range(self.priority_combo.count()):
            if self.priority_combo.itemData(i) == pname:
                self.priority_combo.setCurrentIndex(i)
                break

        # Story points
        pts = fields.get("customfield_10016") or fields.get("story_points")
        self.points_combo.setCurrentIndex(0)
        if pts is not None:
            pts_int = int(pts)
            for i in range(self.points_combo.count()):
                if self.points_combo.itemData(i) == pts_int:
                    self.points_combo.setCurrentIndex(i)
                    break

        # Sprint — find current sprint from customfield_10020
        sprint_field = fields.get("customfield_10020") or []
        if isinstance(sprint_field, list) and sprint_field:
            current_sprint = sprint_field[-1]
            self._current_sprint_id = current_sprint.get("id")
        else:
            self._current_sprint_id = None
        self.sprint_combo.setCurrentIndex(0)  # default to "Keep current"

        # Due date
        duedate = fields.get("duedate")
        if duedate:
            self._due_set = True
            parts = duedate.split("-")
            self.due_date.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
            self.due_date.setStyleSheet(f"color: {TEXT_PRI};")
        else:
            self._due_set = False
            self.due_date.setDate(QDate.currentDate())
            self.due_date.setStyleSheet(f"color: {TEXT_DIM};")

        # Status transitions — reset; caller will populate via set_transitions
        self.transition_combo.setCurrentIndex(0)

        # Description
        desc = fields.get("description") or {}
        plain = self._adf_to_text(desc) if isinstance(desc, dict) else (desc or "")
        self.desc_edit.setPlainText(plain)

        self.comment_edit.clear()
        self.save_btn.setEnabled(True)

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

        # Assignee
        aid = self.assignee_combo.currentData()
        fields["assignee"] = {"accountId": aid} if aid else None

        # Issue type
        itype_id = self.issuetype_combo.currentData()
        if itype_id:
            fields["issuetype"] = {"id": itype_id}

        # Priority
        pname = self.priority_combo.currentData()
        if pname:
            fields["priority"] = {"name": pname}

        # Story points
        pts = self.points_combo.currentData()
        if pts is not None:
            fields["customfield_10016"] = pts

        # Due date
        if self._due_set:
            fields["duedate"] = self.due_date.date().toString("yyyy-MM-dd")
        else:
            fields["duedate"] = None

        # Description
        desc_text = self.desc_edit.toPlainText().strip()
        if desc_text:
            fields["description"] = {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": desc_text}]}]
            }

        # Sprint move target (None = no change)
        target_sprint = self.sprint_combo.currentData()

        # Status transition ID (None = no transition)
        transition_id = self.transition_combo.currentData()

        comment = self.comment_edit.toPlainText().strip()
        self.saved.emit(self.current_key, fields, comment, transition_id, target_sprint)


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

        self._build_ui()
        self._status("Ready — configure connection to get started.")

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Top bar
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

        # Progress bar (above tabs)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(4)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: {DARK_BG}; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT_BLUE}; }}
        """)
        root.addWidget(self.progress)

        # ── Tabs ──────────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setVisible(False)
        root.addWidget(self.tabs, 1)

        # ── Tab 1: Stories ────────────────────────────────────────────────────
        stories_tab = QWidget()
        stories_layout = QVBoxLayout(stories_tab)
        stories_layout.setContentsMargins(0, 0, 0, 0)
        stories_layout.setSpacing(0)

        # Filter bar
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

        fb_layout.addStretch()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter stories…")
        self.search_edit.setMinimumWidth(200)
        self.search_edit.textChanged.connect(self._filter_table)
        fb_layout.addWidget(self.search_edit)

        stories_layout.addWidget(filterbar)

        # Main split
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Left – story table
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 8, 16)
        left_layout.setSpacing(8)

        count_row = QHBoxLayout()
        self.story_count_lbl = QLabel("No stories loaded")
        self.story_count_lbl.setObjectName("dim")
        count_row.addWidget(self.story_count_lbl)
        count_row.addStretch()
        left_layout.addLayout(count_row)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["KEY", "SUMMARY", "ASSIGNEE", "PTS", "STATUS"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.itemSelectionChanged.connect(self._on_story_selected)
        left_layout.addWidget(self.table)

        splitter.addWidget(left)

        # Right – edit panel
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

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    # ── Settings ──────────────────────────────────────────────────────────────
    def _open_settings(self):
        dlg = SettingsDialog(self._settings, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._settings = dlg.get_settings()
            self._client = JiraClient(
                self._settings["url"],
                self._settings["token"],
                self._settings.get("mode", JiraClient.MODE_DC),
                self._settings.get("email", ""),
            )
            self.refresh_btn.setEnabled(True)
            self._load_projects()

    # ── Loading helpers ───────────────────────────────────────────────────────
    def _busy(self, on: bool):
        self.progress.setVisible(on)

    def _status(self, msg: str):
        self.status_bar.showMessage(msg)

    def _spawn(self, fn, *args, on_result=None, on_error=None):
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

    def _load_projects(self):
        self._busy(True)
        self._status("Loading projects…")
        self._spawn(
            self._client.get_projects,
            on_result=self._on_projects_loaded,
        )

    def _on_projects_loaded(self, projects):
        self._busy(False)
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        for p in projects:
            self.project_combo.addItem(f"{p['key']} — {p['name']}", p["key"])
        self.project_combo.blockSignals(False)
        # Enable all controls now that we have a valid connection
        self.project_combo.setEnabled(True)
        self.board_combo.setEnabled(True)
        self.sprint_combo.setEnabled(True)
        self.load_btn.setEnabled(True)
        self._status(f"Loaded {len(projects)} projects.")
        if projects:
            self._on_project_changed()

    def _on_project_changed(self):
        key = self.project_combo.currentData()
        if not key or not self._client:
            return
        self._busy(True)
        self._status(f"Loading boards for {key}…")
        self._spawn(
            self._client.get_boards, key,
            on_result=self._on_boards_loaded,
        )
        self._spawn(
            self._client.get_project_members, key,
            on_result=lambda members: self.edit_panel.set_members(members),
        )
        self._spawn(
            self._client.get_issue_types, key,
            on_result=lambda types: self.edit_panel.set_issue_types(types),
        )


    def _on_boards_loaded(self, boards):
        self._busy(False)
        self._boards = boards
        self.board_combo.blockSignals(True)
        self.board_combo.clear()
        for b in boards:
            self.board_combo.addItem(b["name"], b["id"])
        self.board_combo.blockSignals(False)
        self._status(f"Loaded {len(boards)} boards.")
        if boards:
            self._on_board_changed()

    def _on_board_changed(self):
        bid = self.board_combo.currentData()
        if bid is None or not self._client:
            return
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
        self._status(f"Loaded {len(sprints)} sprints.")
        self.edit_panel.set_sprints(sprints)

    def _load_sprint_issues(self):
        bid = self.board_combo.currentData()
        sid = self.sprint_combo.currentData()
        if bid is None or sid is None or not self._client:
            return
        self._busy(True)
        self._status("Loading stories…")
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
        self.new_story_btn.setEnabled(True)

    def _populate_table(self, issues):
        self.table.setRowCount(0)
        status_colors = {
            "To Do": TEXT_SEC,
            "In Progress": ACCENT_BLUE,
            "Done": ACCENT_GREEN,
            "In Review": ACCENT_CYAN,
            "Blocked": ACCENT_ORG,
        }
        for issue in issues:
            f = issue.get("fields", {})
            row = self.table.rowCount()
            self.table.insertRow(row)

            key_item = QTableWidgetItem(issue["key"])
            key_item.setForeground(QColor(ACCENT_CYAN))
            self.table.setItem(row, 0, key_item)

            self.table.setItem(row, 1, QTableWidgetItem(f.get("summary", "")))

            assignee = f.get("assignee")
            aname = assignee.get("displayName", "Unassigned") if assignee else "—"
            a_item = QTableWidgetItem(aname)
            a_item.setForeground(QColor(TEXT_SEC))
            self.table.setItem(row, 2, a_item)

            pts = f.get("customfield_10016") or f.get("story_points") or ""
            pts_item = QTableWidgetItem(str(int(pts)) if pts else "—")
            pts_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, pts_item)

            status = f.get("status", {}).get("name", "")
            s_item = QTableWidgetItem(status)
            s_item.setForeground(QColor(status_colors.get(status, TEXT_SEC)))
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, s_item)

            self.table.setRowHeight(row, 40)

    def _filter_table(self, text: str):
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = any(
                text in (self.table.item(row, col).text().lower() if self.table.item(row, col) else "")
                for col in range(self.table.columnCount())
            )
            self.table.setRowHidden(row, not match)

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
        if issue:
            self.edit_panel.load_issue(issue)
            # Load available transitions for this issue
            self._spawn(
                self._client.get_issue_transitions, key,
                on_result=lambda t: self.edit_panel.set_transitions(t),
            )

    # ── New Story ─────────────────────────────────────────────────────────────
    def _open_new_story(self):
        key = self.project_combo.currentData()
        if not key or not self._client:
            return
        dlg = NewStoryDialog(
            project_key=key,
            members=self.edit_panel._members,
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
            )

    def _on_story_created(self, result: dict):
        self._busy(False)
        key = result.get("key", "")
        self._status(f"✓ Created {key} successfully.")
        self._load_sprint_issues()

    # ── Save ──────────────────────────────────────────────────────────────────
    def _on_save_story(self, key: str, fields: dict, comment: str,
                       transition_id, target_sprint):
        self._busy(True)
        self._status(f"Saving {key}…")
        self._spawn(
            self._do_save, key, fields, comment, transition_id, target_sprint,
            on_result=lambda _: self._on_saved(key),
        )

    def _do_save(self, key, fields, comment, transition_id, target_sprint):
        self._client.update_issue(key, fields)
        if transition_id:
            self._client.transition_issue(key, transition_id)
        if target_sprint is not None:
            self._client.move_to_sprint(key, target_sprint)
        if comment:
            self._client.add_comment(key, comment)
        return True

    def _on_saved(self, key: str):
        self._busy(False)
        self._status(f"✓ {key} updated successfully.")
        # Refresh
        self._load_sprint_issues()


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
