def _show_command_palette(self):
        """Fuzzy command launcher — Ctrl+K."""
        COMMANDS = [
            # (label, callable, keywords)
            ("Load Stories",              self.load_btn.click,                     "load sprint refresh"),
            ("New Story",                 self.new_story_btn.click,                "create add new story"),
            ("Save Changes",              self.edit_panel.save_btn.click,          "save commit update"),
            ("Bulk Edit",                 self._open_bulk_edit,                    "bulk edit assignee priority points"),
            ("Archive Story",             self._open_archive,                      "archive remove"),
            ("Import Comments",           self.import_btn.click,                   "import bulk comments"),
            ("Export Stories",            self._export_stories,                    "export csv download"),
            ("Sprint Manager",            self._open_sprint_manager,               "sprint create start close rename"),
            ("Switch Instance",           self._switch_instance,                   "switch instance secondary primary"),
            ("Configure / Settings",      self._open_settings,                     "configure settings url token"),
            ("Check for Updates",         self._check_for_updates,                 "update version upgrade"),
            ("Switch to Stories",         lambda: self.tabs.setCurrentIndex(0),    "stories view table"),
            ("Switch to Active Sprint",   self._switch_to_kanban,                  "kanban board active sprint"),
            ("Switch to Backlog",         self._switch_to_backlog,                 "backlog unassigned"),
            ("Switch to Reports",         lambda: self.tabs.setCurrentIndex(3),    "reports sprint report velocity burndown"),
            ("Sprint Report",             self._reports_generate_sprint,           "sprint report generate"),
            ("People Report",             self._reports_generate_people,           "people report team"),
            ("Velocity History",          self._reports_generate_velocity,         "velocity history chart"),
            ("Burndown Chart",            self._reports_generate_burndown,         "burndown chart remaining"),
            ("Keyboard Shortcuts",        self._show_shortcut_dialog,              "shortcuts help keyboard"),
            ("Recent Stories",            self._show_recent_menu,                  "recent history viewed"),
            ("Refresh Sprint",            self._load_sprint_issues,                "refresh reload sprint"),
        ]

        dlg = QDialog(self)
        dlg.setWindowTitle("Command Palette")
        dlg.setMinimumWidth(500)
        dlg.setStyleSheet(self.styleSheet())
        _add_escape_shortcut(dlg)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        search = QLineEdit()
        search.setPlaceholderText("Type to search commands…")
        search.setObjectName("search_edit")
        layout.addWidget(search)

        list_widget = QListWidget()
        list_widget.setStyleSheet(
            f"QListWidget {{ background: {CARD_BG}; border: 1px solid {BORDER}; "
            f"border-radius: 6px; }} "
            f"QListWidget::item {{ padding: 8px 12px; color: {TEXT_PRI}; }} "
            f"QListWidget::item:selected {{ background: {ACCENT_BLUE}; color: white; }}"
        )
        list_widget.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(list_widget, 1)

        def _populate(term: str = ""):
            list_widget.clear()
            term = term.lower()
            for label, fn, keywords in COMMANDS:
                score = 0
                if term:
                    haystack = (label + " " + keywords).lower()
                    if term in label.lower():
                        score = 2
                    elif all(t in haystack for t in term.split()):
                        score = 1
                    else:
                        continue
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, fn)
                list_widget.addItem(item)
            if list_widget.count():
                list_widget.setCurrentRow(0)

        _populate()
        search.textChanged.connect(_populate)

        def _run():
            item = list_widget.currentItem()
            if item:
                dlg.accept()
                fn = item.data(Qt.ItemDataRole.UserRole)
                if fn:
                    fn()

        list_widget.itemDoubleClicked.connect(lambda _: _run())
        QShortcut(QKeySequence("Return"), dlg).activated.connect(_run)
        QShortcut(QKeySequence("Down"), search).activated.connect(
            lambda: list_widget.setCurrentRow(
                min(list_widget.currentRow() + 1, list_widget.count() - 1)
            )
        )
        QShortcut(QKeySequence("Up"), search).activated.connect(
            lambda: list_widget.setCurrentRow(
                max(list_widget.currentRow() - 1, 0)
            )
        )
        dlg.resize(500, 360)
        dlg.exec()