The only change is in _build_ui — replace the standalone save_btn block with the btn_row version:

Before:

        self.save_btn = QPushButton("▶  SAVE CHANGES")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)


After:

        btn_row = QHBoxLayout()
        self.undo_btn = QPushButton("↩  Undo Save")
        self.undo_btn.setMinimumHeight(40)
        self.undo_btn.setToolTip("Restore the state from before the last save")
        self.undo_btn.setEnabled(False)
        self.undo_btn.clicked.connect(self._undo_save)
        btn_row.addWidget(self.undo_btn)
        self.save_btn = QPushButton("▶  SAVE CHANGES")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setEnabled(False)
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)
