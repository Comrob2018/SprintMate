class ImportCommentsDialog(QDialog):
    def __init__(self, parsed: dict, loaded_keys: set, parent=None):
        """
        parsed      : {issue_key: comment_text} from the file
        loaded_keys : set of issue keys currently in the story table
        """
        super().__init__(parent)
        self.setWindowTitle("Import Comments — Preview")
        self.setMinimumWidth(620)
        self.setMinimumHeight(440)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        self._parsed = parsed
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("◈  IMPORT COMMENTS PREVIEW")
        title.setObjectName("heading")
        layout.addWidget(title)

        matched   = {k: v for k, v in parsed.items() if k in loaded_keys}
        unmatched = {k: v for k, v in parsed.items() if k not in loaded_keys}

        summary = QLabel(
            f"Found {len(parsed)} entries — "
            f"{len(matched)} matched to loaded stories, "
            f"{len(unmatched)} not found in current sprint."
        )
        summary.setObjectName("dim")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["KEY", "COMMENT", "STATUS"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)

        for key, comment in parsed.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            key_item = QTableWidgetItem(key)
            key_item.setForeground(QColor(ACCENT_CYAN))
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, QTableWidgetItem(comment[:120] + ("…" if len(comment) > 120 else "")))
            if key in loaded_keys:
                status_item = QTableWidgetItem("✓ Will post")
                status_item.setForeground(QColor(ACCENT_GREEN))
            else:
                status_item = QTableWidgetItem("✗ Not in sprint")
                status_item.setForeground(QColor(ACCENT_ORG))
            self.table.setItem(row, 2, status_item)
            self.table.setRowHeight(row, 36)

        layout.addWidget(self.table, 1)

        if unmatched:
            warn = QLabel(f"⚠  {len(unmatched)} keys not found will be skipped.")
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

        self._to_post = matched

    def get_comments(self) -> dict:
        return self._to_post
        
3.
self.import_btn = QPushButton("📄  Import Comments")
self.import_btn.setObjectName("toolbar_btn")
self.import_btn.clicked.connect(self._import_comments)
self.import_btn.setEnabled(False)
fb_layout.addWidget(self.import_btn)


self.import_btn.setEnabled(True)

        
        
4. 
def _import_comments(self):
    # Opens file dialog, parses file, shows preview dialog
    # Posts matched comments via _spawn

def _parse_comments_file(self, raw: str) -> dict:
    # Parses lines matching KEY: comment format
    # Returns {key: comment} dict

def _post_imported_comments(self, comments: dict):
    # Calls add_comment for each matched key
