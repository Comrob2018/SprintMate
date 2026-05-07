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
            "No valid entries found in the file.\n\nExpected format:\nMDT-123: Your comment text here")
        return

    loaded_keys = set()
    for row in range(self.table.rowCount()):
        item = self.table.item(row, 0)
        if item:
            loaded_keys.add(item.text())

    dlg = ImportCommentsDialog(parsed, loaded_keys, self)
    if dlg.exec() == QDialog.DialogCode.Accepted:
        to_post = dlg.get_comments()
        if to_post:
            self._busy(True)
            self._status(f"Posting {len(to_post)} comments…")
            self._spawn(
                self._post_imported_comments, to_post,
                on_result=lambda _: (
                    self._busy(False),
                    self._status(f"✓ Posted {len(to_post)} comments successfully.")
                )
            )

def _parse_comments_file(self, raw: str) -> dict:
    """Parse file with format: KEY: comment text (one per line)."""
    import re
    result = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Match patterns like MDT-123: comment or MDT-123 : comment
        match = re.match(r'^([A-Z][A-Z0-9]+-\d+)\s*:\s*(.+)$', line)
        if match:
            key = match.group(1).strip()
            comment = match.group(2).strip()
            if comment:
                result[key] = comment
    return result

def _post_imported_comments(self, comments: dict):
    for key, comment in comments.items():
        self._client.add_comment(key, comment)
    return True
