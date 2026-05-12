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
from datetime import date
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QFrame, QScrollArea, QDialog, QDialogButtonBox, QMessageBox,
    QGroupBox, QFormLayout,
    QAbstractItemView, QProgressBar, QStatusBar,
    QTabWidget, QDateEdit, QFileDialog
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QDate, QTimer, QSettings
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

APP_VERSION  = "2.1.1"

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
    MODE_DC = "sentinel"
    MODE_CLOUD = "sentinel"
    MODE_SENTINEL = "Sentinel"
    MODE_ACYD     = "ACyD"

    # mappings
    _FIELD_MAP = {
        MODE_ACYD : {
            "story_point": "customfield_10006",
            "feature_link": "customfield_10000"
        },
        MODE_SENTINEL : {
            "story_point": "customfield_10106",
            "feature_link": "customfield_10100"
        },
    }

    def __init__(self, base_url, token, mode=MODE_SENTINEL, email=""):
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
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            raise RuntimeError(f"HTTP {e.code}: [{method} {url}] {msg}")

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
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()).get("values", [])

    def get_sprint_issues(self, board_id: int, sprint_id: int):
        sp = self.story_point_field_id
        fl = self.feature_link_field_id
        fields = ",".join([
            "summary", "assignee", "status", "priority", "description",
            "comment", "issuetype", sp, fl, "duedate",
            "sprint", "closedSprints", "customfield_10020"
        ])
        url = (f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}"
               f"/issue?maxResults=100&fields={fields}")
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()).get("issues", [])
        
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
        
    def get_priorities(self):
        url = f"{self.base_url}/rest/api/{self.api_version}/priority/search?maxResults=50"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                # v3 returns {values: [...]}, v2 returns a list directly
                if isinstance(result, list):
                    return result
                return result.get("values", [])
        except Exception:
            # Fall back to plain /priority for older DC versions
            try:
                result = self._request("GET", "priority")
                return result if isinstance(result, list) else []
            except Exception:
                return []

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
        encoded = urllib.parse.quote(project_key)
        all_members = []
        start = 0
        max_results = 200

        while True:
            url = (f"{self.base_url}/rest/api/{self.api_version}/"
                f"user/assignable/search?project={encoded}"
                f"&maxResults={max_results}&startAt={start}")
            req = urllib.request.Request(url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read().decode())
                    batch = result if isinstance(result, list) else []
                    if not batch:
                        break
                    all_members.extend(batch)
                    if len(batch) < max_results:
                        break
                    start += max_results
            except urllib.error.HTTPError as e:
                raise RuntimeError(f"HTTP {e.code} [GET {url}]: {e.read().decode()}")
            except Exception:
                break

        return all_members
        
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
        """
        Build the payload and POST a new issue, using the dynamic field IDs
        from the field-map instead of hard-coded ones.
        Argument order matches the _open_new_story call site exactly.
        """
        fields: dict = {
            "project":   {"key": project_key},
            "summary":   summary,
            "issuetype": {"id": issuetype_id},
        }

        if description:
            fields["description"] = description

        # ---- Assignee -------------------------------------------------
        if assignee_id:
            fields["assignee"] = {"name": assignee_id}

        # ---- Priority -------------------------------------------------
        if priority:
            fields["priority"] = {"name": priority}

        # ---- Story points (dynamic) ----------------------------------
        if story_points is not None:
            fields[self.story_point_field_id] = story_points

        # ---- Feature link (dynamic) -----------------------------------
        if feature_link is not None:
            fields[self.feature_link_field_id] = feature_link

        # ---- Due date -------------------------------------------------
        if due_date:
            fields["duedate"] = due_date

        result = self._request("POST", "issue", {"fields": fields})

        # ---- Sprint assignment (Agile API, separate call) -------------
        if sprint_id and result.get("key"):
            try:
                self.move_to_sprint(result["key"], sprint_id)
            except Exception:
                pass  # Story created; sprint move is best-effort

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
        url = f"{self.base_url}/rest/api/{self.api_version}/user/search?query={encoded}&maxResults=20"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
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
            uid = m.get("name") or m.get("accountId")
            self.assignee_combo.addItem(m.get("displayName", "?"), uid)
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


# ------------------IMPORT DIALOG CLASS------------------------------
class ImportCommentsDialog(QDialog):
    def __init__(self, parsed: dict, loaded_keys: set, story_info: dict,
                 cross_keys=None, cross_map=None, parent=None):
        """
        parsed      : {issue_key: comment_text} from the file
        loaded_keys : set of issue keys currently in the story table
        story_info  : {issue_key: (summary, assignee)} from the story table
        cross_keys  : set of keys that have a cross-instance match
        cross_map   : {active_key: other_instance_key}
        """
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

        # ── Preview table ────────────────────────────────────────────
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

        # ── Detail pane (Option B) ────────────────────────────────────
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

        # ── Footer ────────────────────────────────────────────────────
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

    def get_cross_posts(self) -> dict:
        return {k: v for k, v in self._cross_map.items() if k in self._to_post}

    def get_comments(self) -> dict:
        return self._to_post
    
# ── Worker threads ────────────────────────────────────────────────────────────
class Worker(QThread):
    result   = pyqtSignal(object)
    error    = pyqtSignal(str)
    progress = pyqtSignal(int, int)   # (n_done, n_total) — optional; only emitted by functions that support it

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

        # Instance toggle
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(0)

        toggle_style = f"""
            QPushButton {{ border: 1px solid {BORDER}; border-radius: 0; padding: 6px 24px; font-size: 12px; }}
            QPushButton:checked {{ background-color: {ACCENT_BLUE}; color: #fff; border-color: {ACCENT_BLUE}; font-weight: bold; }}
            QPushButton:first-child {{ border-radius: 6px 0 0 6px; }}
            QPushButton:last-child  {{ border-radius: 0 6px 6px 0; }}
        """
        self.sentinel_btn = QPushButton("◈  SENTINEL")
        self.sentinel_btn.setCheckable(True)
        self.sentinel_btn.setFixedHeight(34)
        self.sentinel_btn.setStyleSheet(toggle_style)

        self.acyd_btn = QPushButton("◈  ACYD")
        self.acyd_btn.setCheckable(True)
        self.acyd_btn.setFixedHeight(34)
        self.acyd_btn.setStyleSheet(toggle_style)

        self.sentinel_btn.clicked.connect(lambda: self._set_mode(JiraClient.MODE_SENTINEL))
        self.acyd_btn.clicked.connect(lambda: self._set_mode(JiraClient.MODE_ACYD))

        mode_layout.addWidget(self.sentinel_btn)
        mode_layout.addWidget(self.acyd_btn)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Per-instance form
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
        self.expiry_edit = QDateEdit()
        self.expiry_edit.setCalendarPopup(True)
        self.expiry_edit.setDisplayFormat("yyyy-MM-dd")
        self.expiry_edit.setDate(QDate.currentDate().addYears(1))
        self.expiry_clear_btn = QPushButton("Clear")
        self.expiry_clear_btn.setFixedWidth(70)
        self.expiry_clear_btn.clicked.connect(
            lambda: self.expiry_edit.setDate(QDate.currentDate().addYears(1))
        )
        expiry_row.addWidget(self.expiry_edit)
        expiry_row.addWidget(self.expiry_clear_btn)
        expiry_row.addStretch()
        form.addRow("Token Expiry:", expiry_row)

        self.default_project_edit = QLineEdit()
        self.default_project_edit.setPlaceholderText("e.g. MDT  (auto-selects on connect)")
        form.addRow("Default Project:", self.default_project_edit)
        
        self.default_board_edit = QLineEdit()
        self.default_board_edit.setPlaceholderText("e.g. MDT board  (auto-selects on connect)")
        form.addRow("Default Board:", self.default_board_edit)
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
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        # Internal store for both instances
        self._data = {
            JiraClient.MODE_SENTINEL: {
                "url":           settings.get("sentinel_url", "https://jira.sde.sp.gc1.myngc.com/"),
                "token":         settings.get("sentinel_token", ""),
                "token_expiry":  settings.get("sentinel_token_expiry", ""),
                "default_project": settings.get("sentinel_default_project", ""),
                "default_board": settings.get("sentinel_default_board", ""),
            },
            JiraClient.MODE_ACYD: {
                "url":           settings.get("acyd_url", "https://jira.northgrum.com/"),
                "token":         settings.get("acyd_token", ""),
                "token_expiry":  settings.get("acyd_token_expiry", ""),
                "default_project": settings.get("acyd_default_project", ""),
                "default_board": settings.get("acyd_default_board", ""),
            },
        }
        self._set_mode(settings.get("mode", JiraClient.MODE_SENTINEL))

    def _set_mode(self, mode: str):
        # Save current fields before switching
        if hasattr(self, "_mode"):
            self._data[self._mode]["url"]   = self.url_edit.text().strip()
            self._data[self._mode]["token"] = self.token_edit.text().strip()
            self._data[self._mode]["token_expiry"] = self.expiry_edit.date().toString("yyyy-MM-dd")
            self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()
            self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()

        self._mode = mode
        is_sentinel = mode == JiraClient.MODE_SENTINEL
        self.sentinel_btn.setChecked(is_sentinel)
        self.acyd_btn.setChecked(not is_sentinel)
        self.instance_lbl.setText(f"{'SENTINEL' if is_sentinel else 'ACYD'} INSTANCE")

        # Load saved values for this instance
        self.url_edit.setText(self._data[mode]["url"])
        self.token_edit.setText(self._data[mode]["token"])
        expiry_str = self._data[mode].get("token_expiry", "")
        if expiry_str:
            parts = expiry_str.split("-")
            self.expiry_edit.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
        else:
            self.expiry_edit.setDate(QDate.currentDate().addYears(1))
        self.default_project_edit.setText(self._data[mode]["default_project"])
        self.default_board_edit.setText(self._data[mode].get("default_board", ""))
        self.status_lbl.setText("")

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

    def _save_and_accept(self):
        self._data[self._mode]["url"]   = self.url_edit.text().strip()
        self._data[self._mode]["token"] = self.token_edit.text().strip()
        self._data[self._mode]["token_expiry"] = self.expiry_edit.date().toString("yyyy-MM-dd")
        self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()
        self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()
        self.accept()

    def get_settings(self):
        return {
            "mode":           self._mode,
            "sentinel_url":   self._data[JiraClient.MODE_SENTINEL]["url"],
            "sentinel_token": self._data[JiraClient.MODE_SENTINEL]["token"],
            "sentinel_token_expiry": self._data[JiraClient.MODE_SENTINEL].get("token_expiry", ""),
            "acyd_url":       self._data[JiraClient.MODE_ACYD]["url"],
            "acyd_token":     self._data[JiraClient.MODE_ACYD]["token"],
            "acyd_token_expiry": self._data[JiraClient.MODE_ACYD].get("token_expiry", ""),
            # Active instance shortcuts
            "url":   self._data[self._mode]["url"],
            "token": self._data[self._mode]["token"],
            "sentinel_default_project": self._data[JiraClient.MODE_SENTINEL]["default_project"],
            "acyd_default_project":     self._data[JiraClient.MODE_ACYD]["default_project"],
            "sentinel_default_board": self._data[JiraClient.MODE_SENTINEL].get("default_board", ""),
            "acyd_default_board":     self._data[JiraClient.MODE_ACYD].get("default_board", ""),
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
        self._snapshot = {}         # field values at load time (for dirty detection)
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
        #self.assignee_combo.setMinimumWidth(1000)
        form.addRow("Assignee:", self.assignee_combo)
        
        self.feature_link_edit = QLineEdit()
        self.feature_link_edit.setPlaceholderText("Feature link URL or ID…")
        form.addRow("Feature Link:", self.feature_link_edit)

        # Issue type
        self.issuetype_combo = QComboBox()
        #self.issuetype_combo.setMinimumWidth(160)
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
        FIBONACCI = [None, 0, 1, 3, 5, 8, 13, 21]
        self.points_combo = QComboBox()
        #self.points_combo.setMinimumWidth(140)
        self.points_combo.addItem("— Not set —", None)
        for v in FIBONACCI[1:]:
            self.points_combo.addItem(str(v), v)
        form.addRow("Story Points:", self.points_combo)

        # Sprint
        self.sprint_combo = QComboBox()
        #self.sprint_combo.setMinimumWidth(200)
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
        #self.transition_combo.setMinimumWidth(200)
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
        self.comment_history = QTextEdit()
        self.comment_history.setReadOnly(True)
        self.comment_history.setMaximumHeight(120)
        self.comment_history.setPlaceholderText("No comments yet.")
        self.comment_history.setStyleSheet(
            f"background: {DARK_BG}; border: none; color: {TEXT_SEC}; font-size: 12px;"
        )
        history_layout.addWidget(self.comment_history)
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

        # Save button
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

    def _clear_due_date(self):
        self._due_set = False
        self.due_date.setStyleSheet(f"color: {TEXT_DIM};")
        self.due_date.setDate(QDate.currentDate())
        self._check_dirty()

    def _snapshot_state(self) -> dict:
        """Capture a hashable snapshot of all editable field values."""
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
        """Enable/disable Save based on whether anything changed from the loaded snapshot."""
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
        if members and "to" in members[0]:
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
        self.current_key = issue["key"]
        fields = issue.get("fields", {})

        self.key_lbl.setText(self.current_key)
        self.title_lbl.setText(fields.get("summary", ""))
        status = fields.get("status", {}).get("name", "")
        self.status_badge.setText(f"◈  {status.upper()}")

        # Assignee
        assignee = fields.get("assignee")
        if assignee:
            self._pending_assignee = (
                assignee.get("name") or assignee.get("key") or assignee.get("accountId")
            )
            # Try to set immediately in case members are already loaded
            for i in range(self.assignee_combo.count()):
                if self.assignee_combo.itemData(i) == self._pending_assignee:
                    self.assignee_combo.setCurrentIndex(i)
                    break
            else:
                # Not found — add them manually so they always appear
                display = assignee.get("displayName", self._pending_assignee)
                self.assignee_combo.insertItem(1, display, self._pending_assignee)
                self.assignee_combo.setCurrentIndex(1)
        else:
            self._pending_assignee = None
            self.assignee_combo.setCurrentIndex(0)

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
        pts = fields.get(getattr(self, "_sp_field", "customfield_10016")) or fields.get("customfield_10016") or fields.get("story_points")
        self.points_combo.setCurrentIndex(0)
        if pts is not None:
            pts_int = int(pts)
            for i in range(self.points_combo.count()):
                if self.points_combo.itemData(i) == pts_int:
                    self.points_combo.setCurrentIndex(i)
                    break

        fl_field = getattr(self, "_fl_field", "customfield_10100")
        fl_value = fields.get(fl_field) or ""
        if isinstance(fl_value, dict):
            fl_value = fl_value.get("url", "") or fl_value.get("id", "")
        self.feature_link_edit.setText(str(fl_value) if fl_value else "")

        # Sprint
        sprint_field = fields.get("customfield_10020") or []
        if isinstance(sprint_field, list) and sprint_field:
            current_sprint = sprint_field[-1]
            self._current_sprint_id = current_sprint.get("id")
        else:
            self._current_sprint_id = None
        self.sprint_combo.setCurrentIndex(0)

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

        # Status transitions
        self.transition_combo.setCurrentIndex(0)

        # Description
        desc = fields.get("description") or {}
        plain = self._adf_to_text(desc) if isinstance(desc, dict) else (desc or "")
        self.desc_edit.setPlainText(plain)

        self.comment_edit.clear()

        # Populate comment history from already-fetched data (no extra API call)
        comments_data = fields.get("comment", {})
        if isinstance(comments_data, dict):
            all_comments = comments_data.get("comments", [])
        else:
            all_comments = []
        recent = all_comments[-5:]  # show up to 5 most recent
        if recent:
            lines = []
            for c in reversed(recent):
                author = (c.get("author") or {})
                name = author.get("displayName") or author.get("name") or "Unknown"
                created = (c.get("created") or "")[:10]
                body = c.get("body") or {}
                text = self._adf_to_text(body) if isinstance(body, dict) else str(body)
                text = text.strip().replace("\n", " ")
                if len(text) > 200:
                    text = text[:200] + "…"
                lines.append(f"[{created}] {name}: {text}")
            self.comment_history.setPlainText("\n\n".join(lines))
        else:
            self.comment_history.setPlainText("")

        # Capture baseline snapshot so Save only enables when something actually changes
        self._snapshot = self._snapshot_state()
        self.save_btn.setEnabled(False)
        self.save_btn.setToolTip("No changes to save")

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
        fields["assignee"] = {"name": aid} if aid else None

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
            fields[getattr(self, "_sp_field", "customfield_10016")] = pts
        
        fl_field = getattr(self, "_fl_field", "customfield_10100")
        fl_val = self.feature_link_edit.text().strip()
        if fl_val:
            fields[fl_field] = fl_val

        # Due date
        if self._due_set:
            fields["duedate"] = self.due_date.date().toString("yyyy-MM-dd")
        else:
            fields["duedate"] = None

        # Description
        desc_text = self.desc_edit.toPlainText().strip()
        if desc_text:
            fields["description"] = desc_text

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
        self._settings = self._load_settings()
        self._status("Ready — configure connection to get started.")

        # Auto-connect if credentials exist
        mode = self._settings.get("mode", JiraClient.MODE_SENTINEL)
        url   = self._settings.get("sentinel_url") if mode == JiraClient.MODE_SENTINEL else self._settings.get("acyd_url")
        token = self._settings.get("sentinel_token") if mode == JiraClient.MODE_SENTINEL else self._settings.get("acyd_token")
        if url and token:
            self._settings["url"]   = url
            self._settings["token"] = token
            self._client = JiraClient(url, token, mode)
            self.edit_panel._sp_field = self._client.story_point_field_id
            self.edit_panel._fl_field = self._client.feature_link_field_id
            mode_label = "SENTINEL" if mode == JiraClient.MODE_SENTINEL else "ACYD"
            self.mode_indicator.setText(f"◈  {mode_label}")
            self.refresh_btn.setEnabled(True)
            self.switch_instance_btn.setEnabled(True)
            self._load_projects()

        self._check_token_expiry()

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
        
        self.mode_indicator = QLabel("")
        self.mode_indicator.setStyleSheet(
            f"color: {ACCENT_BLUE}; font-size: 11px; letter-spacing: 2px; padding: 0 12px;"
        )
        tb_layout.addWidget(self.mode_indicator)

        self.switch_instance_btn = QPushButton("⇄  Switch Instance")
        self.switch_instance_btn.setObjectName("toolbar_btn")
        self.switch_instance_btn.setEnabled(False)
        self.switch_instance_btn.setToolTip("Switch between Sentinel and ACyD without opening settings")
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

        self.import_btn = QPushButton("📄  Import Comments")
        self.import_btn.setObjectName("toolbar_btn")
        self.import_btn.clicked.connect(self._import_comments)
        self.import_btn.setEnabled(False)
        fb_layout.addWidget(self.import_btn)
        fb_layout.addStretch()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter stories…")
        #self.search_edit.setMinimumWidth(200)
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
        version_lbl = QLabel(f"◈  v{APP_VERSION}")
        version_lbl.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 11px; letter-spacing: 1px; padding: 0 12px;"
        )
        self.status_bar.addPermanentWidget(version_lbl)

    # ── Persist settings ──────────────────────────────────────────────────────
    @staticmethod
    def _encode_token(token: str) -> str:
        return base64.b64encode(token.encode()).decode() if token else ""

    @staticmethod
    def _decode_token(encoded: str) -> str:
        try:
            return base64.b64decode(encoded.encode()).decode() if encoded else ""
        except Exception:
            return ""
        
    def _clear_sprint_view(self):
        """Reset boards, sprints, story table, and edit panel."""
        self.board_combo.blockSignals(True)
        self.board_combo.clear()
        self.board_combo.blockSignals(False)

        self.sprint_combo.blockSignals(True)
        self.sprint_combo.clear()
        self.sprint_combo.blockSignals(False)

        self.table.setRowCount(0)
        self.story_count_lbl.setText("No stories loaded")
        self._issues = []

        self.edit_panel.current_key = None
        self.edit_panel.title_lbl.setText("Select a story to edit")
        self.edit_panel.key_lbl.setText("")
        self.edit_panel.status_badge.setText("")
        self.edit_panel.save_btn.setEnabled(False)
        self.edit_panel._snapshot = {}

    def _save_settings(self):
        qs = QSettings("SprintMate", "SprintMate")
        s  = self._settings
        qs.setValue("mode",                     s.get("mode", ""))
        qs.setValue("sentinel_url",             s.get("sentinel_url", ""))
        qs.setValue("sentinel_token",           self._encode_token(s.get("sentinel_token", "")))
        qs.setValue("sentinel_token_expiry",    s.get("sentinel_token_expiry", ""))
        qs.setValue("sentinel_default_project", s.get("sentinel_default_project", ""))
        qs.setValue("sentinel_default_board",   s.get("sentinel_default_board", ""))
        qs.setValue("acyd_url",                 s.get("acyd_url", ""))
        qs.setValue("acyd_token",               self._encode_token(s.get("acyd_token", "")))
        qs.setValue("acyd_token_expiry",        s.get("acyd_token_expiry", ""))
        qs.setValue("acyd_default_project",     s.get("acyd_default_project", ""))
        qs.setValue("acyd_default_board",       s.get("acyd_default_board", ""))

    def _load_settings(self) -> dict:
        qs = QSettings("SprintMate", "SprintMate")
        return {
            "mode":                     qs.value("mode", JiraClient.MODE_SENTINEL),
            "sentinel_url":             qs.value("sentinel_url", ""),
            "sentinel_token":           self._decode_token(qs.value("sentinel_token", "")),
            "sentinel_token_expiry":    qs.value("sentinel_token_expiry", ""),
            "sentinel_default_project": qs.value("sentinel_default_project", ""),
            "sentinel_default_board":   qs.value("sentinel_default_board", ""),
            "acyd_url":                 qs.value("acyd_url", ""),
            "acyd_token":               self._decode_token(qs.value("acyd_token", "")),
            "acyd_token_expiry":        qs.value("acyd_token_expiry", ""),
            "acyd_default_project":     qs.value("acyd_default_project", ""),
            "acyd_default_board":       qs.value("acyd_default_board", ""),
        }

    def _check_token_expiry(self):
        warnings = []
        for instance, key in [("Sentinel", "sentinel_token_expiry"), ("ACyD", "acyd_token_expiry")]:
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
    def _open_settings(self):
        dlg = SettingsDialog(self._settings, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._settings = dlg.get_settings()
            mode = self._settings.get("mode", JiraClient.MODE_SENTINEL)
            self._client = JiraClient(
                self._settings["url"],
                self._settings["token"],
                mode
            )
            mode_label = "SENTINEL" if mode == JiraClient.MODE_SENTINEL else "ACYD"
            self.edit_panel._sp_field = self._client.story_point_field_id
            self.edit_panel._fl_field = self._client.feature_link_field_id
            self._sp_field = self._client.story_point_field_id
            self.mode_indicator.setText(f"◈  {mode_label}")
            self.refresh_btn.setEnabled(True)
            self.switch_instance_btn.setEnabled(True)
            self._save_settings()
            self._check_token_expiry()
            self._load_projects()

    # ── Switch instance (topbar shortcut) ────────────────────────────────────
    def _switch_instance(self):
        """Toggle between Sentinel and ACyD without opening the settings dialog."""
        if not self._settings:
            return
        current_mode = self._settings.get("mode", JiraClient.MODE_SENTINEL)
        new_mode = JiraClient.MODE_ACYD if current_mode == JiraClient.MODE_SENTINEL else JiraClient.MODE_SENTINEL

        new_url   = self._settings.get("acyd_url")     if new_mode == JiraClient.MODE_ACYD else self._settings.get("sentinel_url")
        new_token = self._settings.get("acyd_token")   if new_mode == JiraClient.MODE_ACYD else self._settings.get("sentinel_token")

        if not new_url or not new_token:
            QMessageBox.warning(
                self, "Instance Not Configured",
                f"No credentials saved for {new_mode}.\nOpen ⚙ Configure to set them up."
            )
            return

        self._settings["mode"]  = new_mode
        self._settings["url"]   = new_url
        self._settings["token"] = new_token
        self._client = JiraClient(new_url, new_token, new_mode)
        self.edit_panel._sp_field = self._client.story_point_field_id
        self.edit_panel._fl_field = self._client.feature_link_field_id
        self._sp_field = self._client.story_point_field_id

        mode_label = "SENTINEL" if new_mode == JiraClient.MODE_SENTINEL else "ACYD"
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
        mode = self._settings.get("mode", JiraClient.MODE_SENTINEL)
        default_key = self._settings.get(f"{mode}_default_project", "")
        if default_key:
            for i in range(self.project_combo.count()):
                if self.project_combo.itemData(i) == default_key:
                    self.project_combo.setCurrentIndex(i)
                    break
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
        self._clear_sprint_view()
        self._busy(True)
        self._status(f"Loading boards for {key}…")
        self._spawn(
            self._client.get_boards, key,
            on_result=self._on_boards_loaded,
            on_error=lambda e: self._status(f"⚠ Could not load boards for {key} (access restricted)"),
        )
        self._spawn(
            self._client.get_project_members, key,
            on_result=lambda members: self.edit_panel.set_members(members),
            on_error=lambda e: self._status(f"⚠ Could not load assignees for {key} (access restricted)"),
        )
        self._spawn(
            self._client.get_issue_types, key,
            on_result=lambda types: self.edit_panel.set_issue_types(types),
            on_error=lambda e: self._status(f"⚠ Could not load issue types for {key} (access restricted)"),
        )


    def _on_boards_loaded(self, boards):
        self._busy(False)
        self._boards = boards
        self.board_combo.blockSignals(True)
        self.board_combo.clear()
        for b in boards:
            self.board_combo.addItem(b["name"], b["id"])
        mode = self._settings.get("mode", JiraClient.MODE_SENTINEL)
        default_board = self._settings.get(f"{mode}_default_board", "").lower()
        if default_board:
            for i in range(self.board_combo.count()):
                if default_board in self.board_combo.itemText(i).lower():
                    self.board_combo.setCurrentIndex(i)
                    break
        self.board_combo.blockSignals(False)
        self._status(f"Loaded {len(boards)} boards.")
        if boards:
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
        self._status(f"Loaded {len(sprints)} sprints.")
        self.edit_panel.set_sprints(sprints)

    def _load_sprint_issues(self, reselect_key: str = None):
        bid = self.board_combo.currentData()
        sid = self.sprint_combo.currentData()
        if bid is None or sid is None or not self._client:
            return
        # Remember which row was active so we can restore it after reload
        self._reselect_key = reselect_key or self.edit_panel.current_key
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
        self.import_btn.setEnabled(True)
        # Re-select the previously active row if we have one
        reselect = getattr(self, "_reselect_key", None)
        if reselect:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text() == reselect:
                    self.table.selectRow(row)
                    self.table.scrollToItem(item)
                    break
            self._reselect_key = None

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

            sp_field = getattr(self, "_sp_field", "customfield_10016")
            pts = f.get(sp_field) or f.get("customfield_10016") or f.get("story_points") or ""
            pts_item = QTableWidgetItem(str(int(pts)) if pts else "—")
            pts_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, pts_item)

            status = f.get("status", {}).get("name", "")
            s_item = QTableWidgetItem(status)
            s_item.setForeground(QColor(status_colors.get(status, TEXT_SEC)))
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, s_item)

            self.table.setRowHeight(row, 40)

    # New method
    def _on_members_loaded(self, members: list):
        self.edit_panel.set_members(members)


    # Updated to also check assignee column
    def _filter_table(self, text: str):
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = any(
                text in (self.table.item(row, col).text().lower() if self.table.item(row, col) else "")
                for col in range(self.table.columnCount())
            ) if text else True
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
            self._spawn(
                self._client.get_issue_transitions, key,
                on_result=self.edit_panel.set_transitions,  # ← Fix: route directly
            )

    def _import_comments(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Comments File", "",
            "Text/Markdown Files (*.txt *.md);;All Files (*)"
        )
        if not path:
            return
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
                "Expected format:\n"
                "MDT-123 - Task Summary - Assignee Name: Your comment here")
            return

        # Build story_info from the loaded sprint table
        loaded_keys = set()
        story_info  = {}  # {key: (summary, assignee)}
        for row in range(self.table.rowCount()):
            key_item      = self.table.item(row, 0)
            summary_item  = self.table.item(row, 1)
            assignee_item = self.table.item(row, 2)
            if key_item:
                k = key_item.text()
                loaded_keys.add(k)
                story_info[k] = (
                    summary_item.text()  if summary_item  else "",
                    assignee_item.text() if assignee_item else "",
                )

        # Build other-instance client if settings available
        other_client = None
        s = self._settings
        active_mode = s.get("mode", JiraClient.MODE_SENTINEL)
        if active_mode == JiraClient.MODE_SENTINEL and s.get("acyd_url") and s.get("acyd_token"):
            other_client = JiraClient(s["acyd_url"], s["acyd_token"], JiraClient.MODE_ACYD)
        elif active_mode == JiraClient.MODE_ACYD and s.get("sentinel_url") and s.get("sentinel_token"):
            other_client = JiraClient(s["sentinel_url"], s["sentinel_token"], JiraClient.MODE_SENTINEL)

        # Cross-instance matching by summary + assignee from the file itself.
        # Uses fuzzy contains-search (summary ~ "...") to tolerate minor casing/
        # punctuation differences. Falls back to exact match only when the contains
        # search returns nothing.
        # cross_map: {active_key: other_instance_key}
        cross_map = {}
        if other_client:
            for key, entry in parsed.items():
                file_summary  = (entry["summary"] or "").strip()
                file_assignee = (entry["assignee"] or "").strip()
                if not file_summary:
                    continue

                def _best_match(candidates, target_summary, target_assignee):
                    """Return the best-matching issue key, preferring assignee match."""
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

                # Try fuzzy contains-search first
                safe_summary = file_summary.replace('"', '\\"')
                jql = f'summary ~ "{safe_summary}"'
                if file_assignee:
                    safe_assignee = file_assignee.replace('"', '\\"')
                    jql += f' AND assignee = "{safe_assignee}"'
                matches = other_client.search_issues_jql(jql, fields="summary,assignee")

                # Fall back to exact match if contains search returned nothing
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
                # Switch progress bar to bounded mode so we see per-comment progress
                self.progress.setRange(0, n)
                self.progress.setValue(0)
                self._status(f"Posting {n} comments ({nc} to both instances)…")

                def _on_progress(done, total):
                    self.progress.setValue(done)
                    self._status(f"Posting comments… {done}/{total}")

                def _on_done(result):
                    self.progress.setRange(0, 0)   # back to indeterminate
                    self._busy(False)
                    posted   = result.get("posted", n)          if isinstance(result, dict) else n
                    failures = result.get("cross_failures", []) if isinstance(result, dict) else []
                    msg = f"✓ Posted {posted} comment{'s' if posted != 1 else ''} successfully."
                    if failures:
                        msg += f"  ⚠ {len(failures)} cross-post failure(s)"
                    self._status(msg)

                self._spawn(
                    self._post_imported_comments, to_post, cross_map, other_client, _on_progress,
                    on_result=_on_done,
                )

    def _parse_comments_file(self, raw: str) -> dict:
        """
        Parse file with format:
            KEY-123 - Task Summary - Assignee Name: comment text
            KEY-123 | Task Summary | Assignee Name: comment text
        Returns {issue_key: {"comment": str, "summary": str, "assignee": str}}
        """
        import re
        result = {}
        SEP = r'\s*(?:[-|~;])\s*'
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            # Accept either ' - ' or ' | ' as field separator
            match = re.match(
                rf'^([A-Z][A-Z0-9]+-\d+){SEP}(.+?){SEP}(.+?)\s*:\s*(.+)$',
                line
            )
            if match:
                key      = match.group(1).strip()
                summary  = match.group(2).strip()
                assignee = match.group(3).strip()
                comment  = match.group(4).strip()
                if comment:
                    result[key] = {
                        "comment":  comment,
                        "summary":  summary,
                        "assignee": assignee,
                    }
        return result

    def _post_imported_comments(self, comments: dict,
                                cross_map: dict = None, other_client=None,
                                progress_cb=None):
        """Post comments one by one, calling progress_cb(done, total) after each."""
        cross_map = cross_map or {}
        total = len(comments)
        cross_failures = []
        for i, (key, comment) in enumerate(comments.items(), start=1):
            self._client.add_comment(key, comment)
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
        try:
            self._client.update_issue(key, fields)
        except RuntimeError as e:
            sp = self._client.story_point_field_id
            if sp in str(e) or "customfield_10016" in str(e):
                fields_no_pts = {k: v for k, v in fields.items() if k not in (sp, "customfield_10016")}
                self._client.update_issue(key, fields_no_pts)
            else:
                raise
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
        # Reset dirty state so save button disables until next edit
        self.edit_panel._snapshot = self.edit_panel._snapshot_state()
        self.edit_panel.save_btn.setEnabled(False)
        self.edit_panel.save_btn.setToolTip("No changes to save")
        # Refresh and re-select the saved story
        self._load_sprint_issues(reselect_key=key)


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
