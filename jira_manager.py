"""
Jira Team Story Manager - PyQt6 Desktop Application
Manages team stories by project + sprint with assignee, story points, and comment updates.
"""

import sys
import json
import base64
import urllib.request
import urllib.parse
import urllib.error
from functools import partial

from PyQt6.QtWidgets import (
QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
QFrame, QScrollArea, QDialog, QDialogButtonBox, QMessageBox,
QStackedWidget, QDoubleSpinBox, QGroupBox, QFormLayout,
QSizePolicy, QAbstractItemView, QProgressBar, QStatusBar
)
from PyQt6.QtCore import (
Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation,
QEasingCurve, pyqtProperty, QObject
)
from PyQt6.QtGui import (
QFont, QColor, QPalette, QPixmap, QPainter, QBrush,
QLinearGradient, QIcon, QCursor, QFontDatabase
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
font-family: ‘Consolas’, ‘Courier New’, monospace;
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
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
background-color: {CARD_BG};
border: 1px solid {BORDER};
border-radius: 6px;
color: {TEXT_PRI};
padding: 6px 10px;
selection-background-color: {ACCENT_BLUE};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
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
font-family: ‘Consolas’, monospace;
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
"""

# ── Jira API client ───────────────────────────────────────────────────────────

class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        token = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        self.headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        }

   
    def _request(self, method: str, path: str, body=None):
        url = f"{self.base_url}/rest/api/3/{path}"
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
        url = (f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}"
            f"/issue?maxResults=100&fields=summary,assignee,story_points,"
            f"status,priority,description,comment,issuetype,customfield_10016")
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()).get("issues", [])

    def get_project_members(self, project_key: str):
        try:
            result = self._request("GET", f"user/assignable/search?project={project_key}&maxResults=100")
            return result if isinstance(result, list) else []
        except Exception:
            return []

    def update_issue(self, issue_key: str, fields: dict):
        self._request("PUT", f"issue/{issue_key}", {"fields": fields})

    def add_comment(self, issue_key: str, text: str):
        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]
            }
        }
        self._request("POST", f"issue/{issue_key}/comment", body)

    def test_connection(self):
        return self._request("GET", "myself")


# ── Worker threads ────────────────────────────────────────────────────────────

class Worker(QThread):
    result = pyqtSignal(object)
    error  = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn, self._args, self._kwargs = fn, args, kwargs

    def run(self):
        try:
            self.result.emit(self._fn(*self._args, self._kwargs))
        except Exception as e:
            self.error.emit(str(e))
    

# ── Settings dialog ───────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Jira Connection Settings")
        self.setMinimumWidth(480)
        self.setStyleSheet(STYLESHEET)


        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("⚙  CONNECTION SETTINGS")
        title.setObjectName("heading")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.url_edit = QLineEdit(settings.get("url", ""))
        self.url_edit.setPlaceholderText("https://yourteam.atlassian.net")

        self.email_edit = QLineEdit(settings.get("email", ""))
        self.email_edit.setPlaceholderText("you@company.com")

        self.token_edit = QLineEdit(settings.get("token", ""))
        self.token_edit.setPlaceholderText("API token from id.atlassian.com")
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Jira URL:", self.url_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("API Token:", self.token_edit)
        layout.addLayout(form)

        hint = QLabel("Get your API token at: id.atlassian.com → Security → API tokens")
        hint.setObjectName("dim")
        hint.setWordWrap(True)
        layout.addWidget(hint)

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

    def _test(self):
        self.status_lbl.setText("Testing…")
        try:
            client = JiraClient(self.url_edit.text(), self.email_edit.text(), self.token_edit.text())
            info = client.test_connection()
            name = info.get("displayName", "unknown")
            self.status_lbl.setText(f"✓ Connected as {name}")
            self.status_lbl.setStyleSheet(f"color: {ACCENT_GREEN};")
        except Exception as e:
            self.status_lbl.setText(f"✗ {str(e)[:80]}")
            self.status_lbl.setStyleSheet(f"color: {ACCENT_ORG};")

    def get_settings(self):
        return {
            "url":   self.url_edit.text().strip(),
            "email": self.email_edit.text().strip(),
            "token": self.token_edit.text().strip(),
        }


# ── Story edit panel ──────────────────────────────────────────────────────────

class StoryEditPanel(QFrame):
    saved = pyqtSignal(str, dict, str)   # issue_key, fields, comment

    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.current_key = None
        self._members = []
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

        # Assignee
        grp_fields = QGroupBox("STORY FIELDS")
        form = QFormLayout(grp_fields)
        form.setSpacing(10)

        self.assignee_combo = QComboBox()
        self.assignee_combo.setMinimumWidth(200)
        form.addRow("Assignee:", self.assignee_combo)

        self.points_spin = QDoubleSpinBox()
        self.points_spin.setRange(0, 999)
        self.points_spin.setSingleStep(0.5)
        self.points_spin.setDecimals(1)
        self.points_spin.setSpecialValueText("—")
        form.addRow("Story Points:", self.points_spin)

        layout.addWidget(grp_fields)

        # Description
        grp_desc = QGroupBox("DESCRIPTION")
        desc_layout = QVBoxLayout(grp_desc)
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Story description…")
        self.desc_edit.setMinimumHeight(100)
        desc_layout.addWidget(self.desc_edit)
        layout.addWidget(grp_desc)

        # Comment
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
        self.save_btn.setObjectName("success")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

    def set_members(self, members: list):
        self._members = members
        self.assignee_combo.clear()
        self.assignee_combo.addItem("— Unassigned —", None)
        for m in members:
            self.assignee_combo.addItem(m.get("displayName", "?"), m.get("accountId"))

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

        # Story points (customfield_10016 is standard for next-gen / cloud)
        pts = fields.get("customfield_10016") or fields.get("story_points")
        if pts is not None:
            self.points_spin.setValue(float(pts))
        else:
            self.points_spin.setValue(0)

        # Description (plain text extraction from ADF)
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
        aid = self.assignee_combo.currentData()
        fields["assignee"] = {"accountId": aid} if aid else None
        pts = self.points_spin.value()
        if pts > 0:
            fields["customfield_10016"] = pts
        desc_text = self.desc_edit.toPlainText().strip()
        if desc_text:
            fields["description"] = {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": desc_text}]}]
            }
        comment = self.comment_edit.toPlainText().strip()
        self.saved.emit(self.current_key, fields, comment)
    

# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jira Team Manager")
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

        logo = QLabel("◈  JIRA TEAM MANAGER")
        logo.setObjectName("heading")
        logo.setStyleSheet(f"font-size: 14px; color: {ACCENT_CYAN}; letter-spacing: 3px;")
        tb_layout.addWidget(logo)
        tb_layout.addStretch()

        self.connect_btn = QPushButton("⚙  Configure")
        self.connect_btn.setObjectName("primary")
        self.connect_btn.clicked.connect(self._open_settings)
        tb_layout.addWidget(self.connect_btn)

        self.refresh_btn = QPushButton("↺  Refresh")
        self.refresh_btn.clicked.connect(self._load_sprint_issues)
        self.refresh_btn.setEnabled(False)
        tb_layout.addWidget(self.refresh_btn)

        root.addWidget(topbar)

        # Filter bar
        filterbar = QFrame()
        filterbar.setStyleSheet(f"background-color: {PANEL_BG}; border-bottom: 1px solid {BORDER};")
        fb_layout = QHBoxLayout(filterbar)
        fb_layout.setContentsMargins(20, 8, 20, 8)
        fb_layout.setSpacing(12)

        fb_layout.addWidget(QLabel("PROJECT"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(180)
        self.project_combo.currentIndexChanged.connect(self._on_project_changed)
        fb_layout.addWidget(self.project_combo)

        fb_layout.addWidget(QLabel("BOARD"))
        self.board_combo = QComboBox()
        self.board_combo.setMinimumWidth(160)
        self.board_combo.currentIndexChanged.connect(self._on_board_changed)
        fb_layout.addWidget(self.board_combo)

        fb_layout.addWidget(QLabel("SPRINT"))
        self.sprint_combo = QComboBox()
        self.sprint_combo.setMinimumWidth(200)
        fb_layout.addWidget(self.sprint_combo)

        load_btn = QPushButton("Load Stories")
        load_btn.setObjectName("primary")
        load_btn.clicked.connect(self._load_sprint_issues)
        fb_layout.addWidget(load_btn)

        fb_layout.addStretch()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter stories…")
        self.search_edit.setMinimumWidth(200)
        self.search_edit.textChanged.connect(self._filter_table)
        fb_layout.addWidget(self.search_edit)

        root.addWidget(filterbar)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(4)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: {DARK_BG}; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT_BLUE}; }}
        """)
        root.addWidget(self.progress)

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
        root.addWidget(splitter, 1)

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
                self._settings["email"],
                self._settings["token"],
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

    # ── Save ──────────────────────────────────────────────────────────────────
    def _on_save_story(self, key: str, fields: dict, comment: str):
        self._busy(True)
        self._status(f"Saving {key}…")
        self._spawn(
            self._do_save, key, fields, comment,
            on_result=lambda _: self._on_saved(key),
        )

    def _do_save(self, key, fields, comment):
        # Remove None assignee if it causes issues (Jira Cloud accepts null)
        self._client.update_issue(key, fields)
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
    app.setApplicationName("Jira Team Manager")
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
