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
                "url":   settings.get("sentinel_url", ""),
                "token": settings.get("sentinel_token", ""),
            },
            JiraClient.MODE_ACYD: {
                "url":   settings.get("acyd_url", ""),
                "token": settings.get("acyd_token", ""),
            },
        }
        self._set_mode(settings.get("mode", JiraClient.MODE_SENTINEL))