def _clone_issue(self, issue: dict):
    # ── Extract fields from the source issue ──────────────────────────────
    f          = issue.get("fields", {})
    src_key    = issue.get("key", "")
    summary    = f.get("summary", "")
    desc_raw   = f.get("description") or {}
    desc_text  = self.edit_panel._adf_to_text(desc_raw) if isinstance(desc_raw, dict) else str(desc_raw or "")
    aobj       = f.get("assignee") or {}
    assignee   = aobj.get("name") or aobj.get("accountId") or ""
    assignee_display = aobj.get("displayName") or assignee
    itype      = (f.get("issuetype") or {}).get("name", "Story")

    # ── Determine available instances ─────────────────────────────────────
    s = self._settings
    current_mode  = s.get("mode", JiraClient.MODE_SECONDARY)
    other_mode    = JiraClient.MODE_PRIMARY if current_mode == JiraClient.MODE_SECONDARY else JiraClient.MODE_SECONDARY
    other_url     = s.get(f"{'primary' if other_mode == JiraClient.MODE_PRIMARY else 'secondary'}_url", "")
    other_token   = s.get(f"{'primary' if other_mode == JiraClient.MODE_PRIMARY else 'secondary'}_token", "")
    other_label   = "PRIMARY" if other_mode == JiraClient.MODE_PRIMARY else "SECONDARY"
    current_label = "PRIMARY" if current_mode == JiraClient.MODE_PRIMARY else "SECONDARY"
    has_other     = bool(other_url and other_token)

    # ── Build dialog ──────────────────────────────────────────────────────
    dlg = QDialog(self)
    dlg.setWindowTitle(f"Clone {src_key}")
    dlg.setMinimumSize(560, 520)
    dlg.setStyleSheet(self.styleSheet())
    layout = QVBoxLayout(dlg)
    layout.setSpacing(12)
    layout.setContentsMargins(24, 24, 24, 24)

    title_lbl = QLabel(f"⎘  CLONE  {src_key}")
    title_lbl.setObjectName("heading")
    layout.addWidget(title_lbl)

    # ── Instance selector ─────────────────────────────────────────────────
    inst_grp = QGroupBox("TARGET INSTANCE")
    inst_layout = QHBoxLayout(inst_grp)
    inst_combo = QComboBox()
    inst_combo.addItem(f"Current ({current_label})", userData="current")
    if has_other:
        inst_combo.addItem(other_label, userData="other")
    inst_layout.addWidget(inst_combo)
    layout.addWidget(inst_grp)

    # ── Project selector ──────────────────────────────────────────────────
    proj_grp = QGroupBox("TARGET PROJECT")
    proj_layout = QHBoxLayout(proj_grp)
    proj_combo = QComboBox()
    proj_combo.setMinimumWidth(300)
    proj_combo.addItem("Loading projects…")
    proj_combo.setEnabled(False)
    proj_layout.addWidget(proj_combo)
    layout.addWidget(proj_grp)

    # ── Editable fields ───────────────────────────────────────────────────
    fields_grp = QGroupBox("FIELDS TO CLONE")
    fields_layout = QVBoxLayout(fields_grp)
    fields_layout.setSpacing(8)

    sum_lbl = QLabel("Summary")
    sum_lbl.setObjectName("dim")
    fields_layout.addWidget(sum_lbl)
    sum_edit = QLineEdit(f"[Clone] {summary}")
    fields_layout.addWidget(sum_edit)

    desc_lbl = QLabel("Description")
    desc_lbl.setObjectName("dim")
    fields_layout.addWidget(desc_lbl)
    desc_edit = QTextEdit()
    desc_edit.setPlainText(desc_text)
    desc_edit.setMaximumHeight(100)
    fields_layout.addWidget(desc_edit)

    assignee_lbl = QLabel("Assignee (username)")
    assignee_lbl.setObjectName("dim")
    fields_layout.addWidget(assignee_lbl)
    assignee_edit = QLineEdit(assignee)
    assignee_edit.setPlaceholderText(f"e.g. {assignee_display or 'jsmith'}")
    fields_layout.addWidget(assignee_edit)

    layout.addWidget(fields_grp)

    # ── Status label + dialog buttons ─────────────────────────────────────
    status_lbl = QLabel("")
    status_lbl.setObjectName("dim")
    layout.addWidget(status_lbl)

    btns = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    clone_ok = btns.button(QDialogButtonBox.StandardButton.Ok)
    clone_ok.setText("⎘  Clone")
    clone_ok.setObjectName("save_btn")
    clone_ok.setEnabled(False)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    layout.addWidget(btns)

    # ── Lazy project loading ──────────────────────────────────────────────
    _project_cache: dict[str, list] = {}

    def _load_projects_for_instance():
        inst = inst_combo.currentData()
        if inst in _project_cache:
            _populate_projects(_project_cache[inst])
            return
        proj_combo.clear()
        proj_combo.addItem("Loading…")
        proj_combo.setEnabled(False)
        clone_ok.setEnabled(False)
        status_lbl.setText("Fetching projects…")
        client = self._client if inst == "current" else JiraClient(other_url, other_token, other_mode)
        worker = _Worker(client.get_projects)
        worker.result.connect(lambda r: _on_projects(r, inst))
        worker.error.connect(lambda e: status_lbl.setText(f"⚠ {e}"))
        worker.start()
        dlg._workers = getattr(dlg, "_workers", [])
        dlg._workers.append(worker)

    def _on_projects(projects, inst_key):
        _project_cache[inst_key] = projects
        _populate_projects(projects)

    def _populate_projects(projects):
        proj_combo.clear()
        if not projects:
            proj_combo.addItem("No projects found")
            status_lbl.setText("⚠ No projects available.")
            return
        for p in sorted(projects, key=lambda x: x.get("name", "")):
            proj_combo.addItem(f"{p.get('key','')} — {p.get('name','')}", userData=p.get("key",""))
        proj_combo.setEnabled(True)
        clone_ok.setEnabled(True)
        status_lbl.setText("")

    inst_combo.currentIndexChanged.connect(lambda _: _load_projects_for_instance())
    _load_projects_for_instance()  # kick off immediately on open

    if dlg.exec() != QDialog.DialogCode.Accepted:
        return

    # ── Collect final values after dialog closes ──────────────────────────
    target_project = proj_combo.currentData()
    if not target_project:
        return

    new_summary  = sum_edit.text().strip() or f"[Clone] {summary}"
    new_desc     = desc_edit.toPlainText().strip()
    new_assignee = assignee_edit.text().strip()
    inst         = inst_combo.currentData()
    target_label = proj_combo.currentText()

    target_client = self._client if inst == "current" else JiraClient(other_url, other_token, other_mode)

    # ── Execute clone in background ───────────────────────────────────────
    self._busy(True)
    self._status(f"Cloning {src_key} → {target_project}…")

    def _do_clone():
        return target_client.clone_issue(
            project_key=target_project,
            summary=new_summary,
            description=new_desc,
            assignee_name=new_assignee,
            issue_type=itype,
        )

    def _on_done(result):
        self._busy(False)
        new_key = result.get("key", "—")
        new_url = f"{target_client.base_url}/browse/{new_key}"

        msg = QMessageBox(self)
        msg.setWindowTitle("Clone Successful")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            f"✓ <b>{src_key}</b> cloned successfully.\n\n"
            f"New issue: <b>{new_key}</b>\n"
            f"Project: {target_label}\n"
            f"Instance: {other_label if inst == 'other' else current_label}"
        )
        copy_btn = msg.addButton("Copy Key", QMessageBox.ButtonRole.ActionRole)
        open_btn = msg.addButton("Open in Jira", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()

        if msg.clickedButton() == copy_btn:
            QApplication.clipboard().setText(new_key)
            self._status(f"✓ Cloned as {new_key} — key copied to clipboard.")
        elif msg.clickedButton() == open_btn:
            webbrowser.open(new_url)
            self._status(f"✓ Cloned as {new_key} — opened in browser.")
        else:
            self._status(f"✓ {src_key} cloned as {new_key}.")

    self._spawn(
        _do_clone,
        on_result=_on_done,
        on_error=lambda e: (
            self._busy(False),
            self._status("✗ Clone failed."),
            QMessageBox.critical(self, "Clone Failed", str(e)),
        ),
    )
