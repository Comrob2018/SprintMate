Four changes:
1. Removed ASSIGNEE label and dropdown from filter bar:

# Removed entirely
fb_layout.addWidget(QLabel("ASSIGNEE"))
self.assignee_filter = QComboBox()
self.assignee_filter.setMinimumWidth(160)
self.assignee_filter.setEnabled(False)
self.assignee_filter.addItem("— All —", None)
self.assignee_filter.currentIndexChanged.connect(...)
fb_layout.addWidget(self.assignee_filter)


2. Removed enable call in _on_issues_loaded:

# Removed
self.assignee_filter.setEnabled(True)


3. Removed populate in _on_members_loaded:

# Removed
self.assignee_filter.blockSignals(True)
self.assignee_filter.clear()
self.assignee_filter.addItem("— All —", None)
for m in members:
    self.assignee_filter.addItem(...)
self.assignee_filter.blockSignals(False)


4. Simplified _filter_table back to text-only:

# Before
def _filter_table(self, text: str):
    text = text.lower()
    assignee_filter = self.assignee_filter.currentData()
    for row in range(self.table.rowCount()):
        text_match = any(...) if text else True
        assignee_match = (assignee_filter is None or ...)
        self.table.setRowHidden(row, not (text_match and assignee_match))

# After
def _filter_table(self, text: str):
    text = text.lower()
    for row in range(self.table.rowCount()):
        match = any(
            text in (self.table.item(row, col).text().lower() if self.table.item(row, col) else "")
            for col in range(self.table.columnCount())
        ) if text else True
        self.table.setRowHidden(row, not match)
