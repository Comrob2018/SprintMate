# Before:
        sprint_layout.addLayout(sprint_btn_row)
        self._tabs.addTab(sprint_tab, "📊  Sprint Report")
                                                          # ← blank line here caused Pylance to lose track
        # ── Tab 2: People Report ──

# After:
        sprint_layout.addLayout(sprint_btn_row)
        self._tabs.addTab(sprint_tab, "📊  Sprint Report")
        # ── Tab 2: People Report ──

sprint_btn_row = QHBoxLayout()
self._save_sprint_btn = QPushButton("⬇  Save as HTML")
self._save_sprint_btn.setObjectName("toolbar_btn")
self._save_sprint_btn.clicked.connect(self._save_html)
self._save_sprint_btn.setEnabled(False)
sprint_btn_row.addWidget(self._save_sprint_btn)
sprint_btn_row.addStretch()
sprint_layout.addLayout(sprint_btn_row)
self._tabs.addTab(sprint_tab, "📊  Sprint Report")




# Before — two separate _do definitions, scope_label branch-scoped:
def _generate_sprint_report(self):
    ...
    if self._sr_scope_sprint_rb.isChecked():
        sprint_id   = self._sr_sprint_combo.currentData() or 0
        scope_label = self._sr_sprint_combo.currentText()   # only set in if-branch
        ...
        def _do():
            return self._client.get_sprint_issues(self._board_id, sprint_id)
    else:
        date_from   = self._sr_date_from.text().strip()
        date_to     = self._sr_date_to.text().strip()
        scope_label = f"{date_from or '…'} → {date_to or '…'}"  # only set in else-branch
        def _do():
            ...
            all_issues = []   # inside nested closure — Pylance loses it
            ...
            return all_issues

    def _on_done(issues):
        self._build_report(issues, scope_label)   # ← Pylance: scope_label may be undefined


# After — all variables hoisted, single _do, imports removed:
def _generate_sprint_report(self):
    self._sr_gen_btn.setEnabled(False)
    self._sr_status.setText("Fetching issues…")
    self._browser.setHtml("<p style='color:#888;padding:20px;'>Loading…</p>")

    # All variables defined unconditionally at method scope
    use_sprint  = self._sr_scope_sprint_rb.isChecked()
    sprint_id   = self._sr_sprint_combo.currentData() or 0 if use_sprint else 0
    date_from   = "" if use_sprint else self._sr_date_from.text().strip()
    date_to     = "" if use_sprint else self._sr_date_to.text().strip()

    if use_sprint:
        scope_label = self._sr_sprint_combo.currentText()
        if not sprint_id:
            self._sr_gen_btn.setEnabled(True)
            self._sr_status.setText("⚠ No sprint selected.")
            return
    else:
        scope_label = f"{date_from or '…'} → {date_to or '…'}"

    # Single _do — branches internally, no nested closures
    def _do() -> list:
        if use_sprint:
            return self._client.get_sprint_issues(self._board_id, sprint_id)
        # Date range path
        jql_parts = []
        if date_from:
            jql_parts.append(f'updated >= "{date_from}"')
        if date_to:
            jql_parts.append(f'updated <= "{date_to}"')
        jql = " AND ".join(jql_parts) if jql_parts else "updated >= -90d"
        jql += " ORDER BY updated DESC"
        encoded = urllib.parse.quote(jql)        # uses top-level import, not __import__()
        sp = self._client.story_point_field_id
        fields = ",".join([
            "summary", "assignee", "status", "priority", "issuetype",
            "duedate", sp, "comment",
        ])
        all_issues: list = []                    # typed annotation keeps Pylance happy
        start = 0
        max_results = 100
        while True:
            url = (f"{self._client.base_url}/rest/api/{self._client.api_version}/search"
                   f"?jql={encoded}&maxResults={max_results}&startAt={start}&fields={fields}")
            req = urllib.request.Request(url, headers=self._client.headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            batch = data.get("issues", [])
            all_issues.extend(batch)
            if len(batch) < max_results:
                break
            start += max_results
        return all_issues

    def _on_done(issues: list) -> None:
        self._sr_gen_btn.setEnabled(True)
        self._sr_status.setText(f"✓ {len(issues)} issues loaded.")
        self._save_sprint_btn.setEnabled(True)
        self._build_report(issues, scope_label)   # scope_label always defined now

    def _on_err(e: str) -> None:
        self._sr_gen_btn.setEnabled(True)
        self._sr_status.setText(f"✗ {e}")
        self._browser.setHtml(
            f"<p style='color:#f78166;padding:20px;'>Error: {e}</p>"
        )

    worker = Worker(_do)
    worker.result.connect(_on_done)
    worker.error.connect(_on_err)
    worker.start()
    self._sr_worker = worker
