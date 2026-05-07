# ── Import Comments ───────────────────────────────────────────────────────
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

        # Build set of loaded keys and a summary+assignee lookup
        loaded_keys = set()
        # {key: (summary, assignee_display_name)}
        story_info = {}
        for row in range(self.table.rowCount()):
            key_item     = self.table.item(row, 0)
            summary_item = self.table.item(row, 1)
            assignee_item= self.table.item(row, 2)
            if key_item:
                k = key_item.text()
                loaded_keys.add(k)
                story_info[k] = (
                    summary_item.text() if summary_item else "",
                    assignee_item.text() if assignee_item else "",
                )

        # Build other instance client if settings available
        other_client = None
        s = self._settings
        active_mode = s.get("mode", JiraClient.MODE_SENTINEL)
        if active_mode == JiraClient.MODE_SENTINEL and s.get("acyd_url") and s.get("acyd_token"):
            other_client = JiraClient(s["acyd_url"], s["acyd_token"], JiraClient.MODE_ACYD)
        elif active_mode == JiraClient.MODE_ACYD and s.get("sentinel_url") and s.get("sentinel_token"):
            other_client = JiraClient(s["sentinel_url"], s["sentinel_token"], JiraClient.MODE_SENTINEL)

        # Find cross-instance matches by summary + assignee
        # cross_map: {active_key: other_instance_key}
        cross_map = {}
        if other_client:
            for key, comment in parsed.items():
                if key not in story_info:
                    continue
                summary, assignee = story_info[key]
                if not summary:
                    continue
                # Escape quotes in JQL
                safe_summary = summary.replace('"', '\\"')
                jql = f'summary = "{safe_summary}"'
                if assignee and assignee != "—":
                    safe_assignee = assignee.replace('"', '\\"')
                    jql += f' AND assignee = "{safe_assignee}"'
                matches = other_client.search_issues_jql(jql, fields="summary,assignee")
                if matches:
                    cross_map[key] = matches[0]["key"]

        cross_keys = set(cross_map.keys())
        dlg = ImportCommentsDialog(parsed, loaded_keys, cross_keys, cross_map, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            to_post = dlg.get_comments()
            if to_post:
                self._busy(True)
                n = len(to_post)
                nc = len({k for k in to_post if k in cross_keys})
                self._status(f"Posting {n} comments ({nc} to both instances)…")
                self._spawn(
                    self._post_imported_comments, to_post, cross_map, other_client,
                    on_result=lambda _: (
                        self._busy(False),
                        self._status(f"✓ Posted {n} comments successfully.")
                    )
                )