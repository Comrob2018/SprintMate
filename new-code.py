Sorry about that! The `bash` output was returned as raw text rather than rendered as a code block. Let me display it properly:

Here's the full class:

```python
class SprintReportDialog(QDialog):
    """Sprint report dialog with two tabs: Sprint Report and People Report."""

    def __init__(self, issues: list, sprint_label: str, sp_field: str,
                 fl_field: str, base_url: str, adf_to_text_fn,
                 client=None, board_id: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sprint Report")
        self.setMinimumSize(960, 720)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        self._issues       = issues
        self._sprint_label = sprint_label
        self._sp_field     = sp_field
        self._fl_field     = fl_field
        self._base_url     = base_url
        self._adf_to_text  = adf_to_text_fn
        self._client       = client
        self._board_id     = board_id
        self._html         = ""
        self._people_html  = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs, 1)

        # ── Tab 1: Sprint Report ──────────────────────────────────────────────
        sprint_tab = QWidget()
        sprint_layout = QVBoxLayout(sprint_tab)
        sprint_layout.setSpacing(8)
        sprint_layout.setContentsMargins(0, 12, 0, 0)

        title = QLabel("◈  SPRINT REPORT")
        title.setObjectName("heading")
        sprint_layout.addWidget(title)
        sub = QLabel(sprint_label)
        sub.setObjectName("dim")
        sprint_layout.addWidget(sub)

        from PyQt6.QtWidgets import QTextBrowser
        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        self._browser.setStyleSheet(
            f"background: #ffffff; color: #111111; border: 1px solid {BORDER}; border-radius: 6px;"
        )
        sprint_layout.addWidget(self._browser, 1)

        sprint_btn_row = QHBoxLayout()
        save_sprint_btn = QPushButton("⬇  Save as HTML")
        save_sprint_btn.setObjectName("toolbar_btn")
        save_sprint_btn.clicked.connect(self._save_html)
        sprint_btn_row.addWidget(save_sprint_btn)
        sprint_btn_row.addStretch()
        sprint_layout.addLayout(sprint_btn_row)
        self._tabs.addTab(sprint_tab, "📊  Sprint Report")

        # ── Tab 2: People Report ──────────────────────────────────────────────
        people_tab = QWidget()
        people_layout = QVBoxLayout(people_tab)
        people_layout.setSpacing(10)
        people_layout.setContentsMargins(0, 12, 0, 0)

        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(12)

        # -- Scope: Sprint or Date Range
        scope_grp = QGroupBox("SCOPE")
        scope_inner = QVBoxLayout(scope_grp)
        scope_inner.setSpacing(6)

        self._scope_sprint_rb = QRadioButton("Sprint")
        self._scope_date_rb   = QRadioButton("Date Range")
        self._scope_sprint_rb.setChecked(True)
        scope_inner.addWidget(self._scope_sprint_rb)
        scope_inner.addWidget(self._scope_date_rb)

        self._sprint_scope_combo = QComboBox()
        self._sprint_scope_combo.setMinimumWidth(220)
        self._sprint_scope_combo.addItem("Loading sprints…")
        self._sprint_scope_combo.setEnabled(False)
        scope_inner.addWidget(self._sprint_scope_combo)

        date_row = QHBoxLayout()
        self._date_from = QLineEdit()
        self._date_from.setPlaceholderText("From  YYYY-MM-DD")
        self._date_from.setEnabled(False)
        self._date_to = QLineEdit()
        self._date_to.setPlaceholderText("To  YYYY-MM-DD")
        self._date_to.setEnabled(False)
        date_row.addWidget(self._date_from)
        date_row.addWidget(QLabel("→"))
        date_row.addWidget(self._date_to)
        scope_inner.addLayout(date_row)
        ctrl_row.addWidget(scope_grp)

        def _on_scope_toggle():
            use_sprint = self._scope_sprint_rb.isChecked()
            self._sprint_scope_combo.setEnabled(use_sprint and self._sprint_scope_combo.count() > 0)
            self._date_from.setEnabled(not use_sprint)
            self._date_to.setEnabled(not use_sprint)

        self._scope_sprint_rb.toggled.connect(_on_scope_toggle)
        self._scope_date_rb.toggled.connect(_on_scope_toggle)

        # -- People selector
        people_grp = QGroupBox("PEOPLE")
        people_inner = QVBoxLayout(people_grp)
        people_inner.setSpacing(6)

        people_inner.addWidget(QLabel("Select from sprint:"))
        self._people_list = QListWidget()
        self._people_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._people_list.setMaximumHeight(120)

        seen = set()
        for iss in issues:
            aobj = (iss.get("fields") or {}).get("assignee") or {}
            name = aobj.get("name") or aobj.get("accountId") or ""
            display = aobj.get("displayName") or name
            if name and name not in seen:
                seen.add(name)
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, name)
                self._people_list.addItem(item)

        people_inner.addWidget(self._people_list)
        people_inner.addWidget(QLabel("Add more (comma-separated usernames):"))
        self._extra_people = QLineEdit()
        self._extra_people.setPlaceholderText("e.g. jsmith, adoe")
        people_inner.addWidget(self._extra_people)
        ctrl_row.addWidget(people_grp, 1)

        people_layout.addLayout(ctrl_row)

        gen_row = QHBoxLayout()
        self._gen_btn = QPushButton("▶  Generate People Report")
        self._gen_btn.setObjectName("save_btn")
        self._gen_btn.clicked.connect(self._generate_people_report)
        gen_row.addWidget(self._gen_btn)
        self._people_status = QLabel("")
        self._people_status.setObjectName("dim")
        gen_row.addWidget(self._people_status, 1)
        people_layout.addLayout(gen_row)

        self._people_browser = QTextBrowser()
        self._people_browser.setOpenExternalLinks(True)
        self._people_browser.setStyleSheet(
            f"background: #ffffff; color: #111111; border: 1px solid {BORDER}; border-radius: 6px;"
        )
        people_layout.addWidget(self._people_browser, 1)

        people_btn_row = QHBoxLayout()
        save_people_btn = QPushButton("⬇  Save as HTML")
        save_people_btn.setObjectName("toolbar_btn")
        save_people_btn.clicked.connect(self._save_people_html)
        save_people_btn.setEnabled(False)
        self._save_people_btn = save_people_btn
        people_btn_row.addWidget(save_people_btn)
        people_btn_row.addStretch()
        people_layout.addLayout(people_btn_row)

        self._tabs.addTab(people_tab, "👤  People Report")

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._build_report()
        self._load_sprints_for_people_tab()
        QTimer.singleShot(50, lambda: self._browser.setHtml(self._html))

    # ── Sprint Report ─────────────────────────────────────────────────────────
    def _build_report(self):
        sp = self._sp_field
        today = date.today().strftime("%Y-%m-%d")

        total_pts = done_pts = 0
        status_counts: dict[str, int] = {}
        assignee_stats: dict[str, dict] = {}

        for iss in self._issues:
            f = iss.get("fields", {})
            status = (f.get("status") or {}).get("name", "—")
            status_counts[status] = status_counts.get(status, 0) + 1

            pts_raw = f.get(sp) or f.get("customfield_10016")
            try:
                pts = int(float(pts_raw)) if pts_raw is not None else 0
            except (TypeError, ValueError):
                pts = 0
            total_pts += pts
            if status == "Done":
                done_pts += pts

            aobj = f.get("assignee") or {}
            aname = aobj.get("displayName") or aobj.get("name") or "Unassigned"
            if aname not in assignee_stats:
                assignee_stats[aname] = {"total": 0, "done": 0, "pts": 0, "done_pts": 0, "stories": []}
            assignee_stats[aname]["total"] += 1
            assignee_stats[aname]["pts"] += pts
            if status == "Done":
                assignee_stats[aname]["done"] += 1
                assignee_stats[aname]["done_pts"] += pts
            assignee_stats[aname]["stories"].append(iss)

        pct_done = round(done_pts / total_pts * 100) if total_pts else 0
        n_done   = status_counts.get("Done", 0)
        n_total  = len(self._issues)

        STATUS_CSS = {
            "To Do":       "#6e7681",
            "In Progress": "#388bfd",
            "Done":        "#3fb950",
            "In Review":   "#39d5f5",
            "Blocked":     "#f78166",
        }

        def status_badge(name):
            col = STATUS_CSS.get(name, "#8b949e")
            return (f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;'
                    f'font-size:11px;font-weight:bold;background:{col}22;color:{col};'
                    f'border:1px solid {col}55;">{name}</span>')

        def priority_icon(name):
            icons = {"Highest": "🔴", "High": "🟠", "Medium": "🟡",
                     "Low": "🟢", "Lowest": "⚪"}
            return icons.get(name, "•")

        def bar(pct, colour="#388bfd", width=180):
            filled = max(0, min(pct, 100))
            return (f'<div style="display:inline-block;width:{width}px;height:8px;'
                    f'background:#e0e0e0;border-radius:4px;vertical-align:middle;">'
                    f'<div style="width:{filled}%;height:8px;background:{colour};'
                    f'border-radius:4px;"></div></div>')

        story_rows = []
        for iss in sorted(self._issues, key=lambda i: i.get("key", "")):
            f      = iss.get("fields", {})
            key    = iss.get("key", "")
            summ   = f.get("summary", "")
            status = (f.get("status") or {}).get("name", "—")
            pri    = (f.get("priority") or {}).get("name", "—")
            itype  = (f.get("issuetype") or {}).get("name", "—")
            due    = (f.get("duedate") or "")[:10] or "—"
            aobj   = f.get("assignee") or {}
            aname  = aobj.get("displayName") or aobj.get("name") or "—"
            pts_raw = f.get(sp) or f.get("customfield_10016")
            try:
                pts_str = str(int(float(pts_raw))) if pts_raw is not None else "—"
            except (TypeError, ValueError):
                pts_str = "—"

            key_cell = (f'<a href="{self._base_url}/browse/{key}" style="color:#388bfd;">{key}</a>'
                        if self._base_url else key)

            due_style = ""
            if due != "—":
                try:
                    days = (date.fromisoformat(due) - date.today()).days
                    if days < 0:
                        due_style = "color:#f78166;font-weight:bold;"
                    elif days <= 3:
                        due_style = "color:#e3b341;"
                except ValueError:
                    pass

            story_rows.append(
                f"<tr>"
                f"<td>{key_cell}</td>"
                f"<td>{summ}</td>"
                f"<td>{aname}</td>"
                f"<td>{status_badge(status)}</td>"
                f"<td style='text-align:center;'>{priority_icon(pri)} {pri}</td>"
                f"<td style='text-align:center;'>{pts_str}</td>"
                f"<td style='text-align:center;{due_style}'>{due}</td>"
                f"<td style='text-align:center;'>{itype}</td>"
                f"</tr>"
            )

        assignee_rows = []
        for aname, ast in sorted(assignee_stats.items(), key=lambda x: -x[1]["pts"]):
            ap = round(ast["done_pts"] / ast["pts"] * 100) if ast["pts"] else 0
            assignee_rows.append(
                f"<tr>"
                f"<td><strong>{aname}</strong></td>"
                f"<td style='text-align:center;'>{ast['total']}</td>"
                f"<td style='text-align:center;'>{ast['done']}</td>"
                f"<td style='text-align:center;'>{ast['pts']}</td>"
                f"<td style='text-align:center;'>{ast['done_pts']}</td>"
                f"<td>{bar(ap)} &nbsp;{ap}%</td>"
                f"</tr>"
            )

        status_rows = "".join(
            f"<tr><td>{status_badge(s)}</td>"
            f"<td style='text-align:center;'>{c}</td>"
            f"<td style='text-align:center;'>{round(c/n_total*100) if n_total else 0}%</td></tr>"
            for s, c in sorted(status_counts.items(), key=lambda x: -x[1])
        )

        td = "padding:8px 12px;border-bottom:1px solid #e0e0e0;"
        th = ("padding:8px 12px;background:#f6f8fa;font-size:11px;letter-spacing:.5px;"
              "text-transform:uppercase;border-bottom:2px solid #d0d7de;text-align:left;")

        self._html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Sprint Report — {self._sprint_label}</title>
<style>
  body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
          color:#1f2328;background:#ffffff;margin:0;padding:32px; }}
  h1   {{ font-size:22px;font-weight:700;margin:0 0 4px; }}
  h2   {{ font-size:14px;font-weight:600;margin:28px 0 10px;color:#57606a;
          text-transform:uppercase;letter-spacing:.8px; }}
  .meta {{ font-size:12px;color:#57606a;margin-bottom:28px; }}
  .stat-grid {{ display:flex;gap:20px;margin-bottom:28px;flex-wrap:wrap; }}
  .stat-card {{ background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;
                padding:16px 20px;min-width:130px; }}
  .stat-card .val {{ font-size:28px;font-weight:700;color:#1f2328; }}
  .stat-card .lbl {{ font-size:11px;color:#57606a;text-transform:uppercase;
                     letter-spacing:.5px;margin-top:2px; }}
  table {{ border-collapse:collapse;width:100%;font-size:13px; }}
  th    {{ {th} }}
  td    {{ {td} }}
  tr:last-child td {{ border-bottom:none; }}
  tr:hover td {{ background:#f6f8fa; }}
  .progress-wrap {{ background:#e0e0e0;border-radius:4px;height:10px;
                    width:100%;margin-top:6px; }}
  .progress-fill {{ background:#3fb950;border-radius:4px;height:10px; }}
</style>
</head>
<body>
<h1>Sprint Report</h1>
<div class="meta">{self._sprint_label} &nbsp;·&nbsp; Generated {today}</div>

<div class="stat-grid">
  <div class="stat-card"><div class="val">{n_total}</div><div class="lbl">Total Stories</div></div>
  <div class="stat-card"><div class="val">{n_done}</div><div class="lbl">Done</div></div>
  <div class="stat-card"><div class="val">{total_pts}</div><div class="lbl">Total Points</div></div>
  <div class="stat-card"><div class="val">{done_pts}</div><div class="lbl">Points Done</div></div>
  <div class="stat-card">
    <div class="val">{pct_done}%</div>
    <div class="lbl">Velocity</div>
    <div class="progress-wrap"><div class="progress-fill" style="width:{pct_done}%;"></div></div>
  </div>
</div>

<h2>Status Breakdown</h2>
<table>
  <tr><th>Status</th><th>Count</th><th>%</th></tr>
  {status_rows}
</table>

<h2>By Assignee</h2>
<table>
  <tr>
    <th>Name</th><th>Stories</th><th>Done</th>
    <th>Pts</th><th>Pts Done</th><th>Progress</th>
  </tr>
  {"".join(assignee_rows)}
</table>

<h2>All Stories</h2>
<table>
  <tr>
    <th>Key</th><th>Summary</th><th>Assignee</th><th>Status</th>
    <th>Priority</th><th>Pts</th><th>Due</th><th>Type</th>
  </tr>
  {"".join(story_rows)}
</table>
</body>
</html>"""

        self._browser.setHtml(self._html)

    def _save_html(self):
        from PyQt6.QtWidgets import QFileDialog
        slug = re.sub(r"[^\w\-]", "-", self._sprint_label)[:60]
        suggested = f"sprint-report-{slug}-{date.today()}.html"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Sprint Report", suggested,
            "HTML Files (*.html);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._html)
            QMessageBox.information(self, "Saved", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))

    # ── People Report ─────────────────────────────────────────────────────────
    def _load_sprints_for_people_tab(self):
        if not self._client or not self._board_id:
            self._sprint_scope_combo.clear()
            self._sprint_scope_combo.addItem("No board available")
            return

        def _do():
            return self._client.get_all_sprints(self._board_id)

        worker = _Worker(_do)
        worker.result.connect(self._on_sprints_loaded)
        worker.error.connect(lambda e: self._sprint_scope_combo.addItem("Failed to load"))
        worker.start()
        self._sprint_worker = worker

    def _on_sprints_loaded(self, sprints):
        self._sprint_scope_combo.clear()
        if not sprints:
            self._sprint_scope_combo.addItem("No sprints found")
            return
        for s in reversed(sprints):  # most recent first
            state = s.get("state", "")
            label = f"{s.get('name', '')}  [{state}]"
            self._sprint_scope_combo.addItem(label, userData=s.get("id"))
        self._sprint_scope_combo.setEnabled(self._scope_sprint_rb.isChecked())

    def _generate_people_report(self):
        selected = []
        for i in range(self._people_list.count()):
            item = self._people_list.item(i)
            if item.isSelected():
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        extras = [n.strip() for n in self._extra_people.text().split(",") if n.strip()]
        assignees = list(dict.fromkeys(selected + extras))

        if not assignees:
            QMessageBox.warning(self, "No People Selected",
                                "Please select at least one person or enter a username.")
            return

        sprint_id   = 0
        date_from   = ""
        date_to     = ""
        scope_label = ""

        if self._scope_sprint_rb.isChecked():
            sprint_id   = self._sprint_scope_combo.currentData() or 0
            scope_label = self._sprint_scope_combo.currentText()
        else:
            date_from   = self._date_from.text().strip()
            date_to     = self._date_to.text().strip()
            scope_label = f"{date_from or '…'} → {date_to or '…'}"

        self._gen_btn.setEnabled(False)
        self._people_status.setText("Fetching issues…")
        self._people_browser.setHtml("<p style='color:#888;padding:20px;'>Loading…</p>")

        def _do():
            return self._client.get_issues_for_people_report(
                assignees=assignees,
                date_from=date_from,
                date_to=date_to,
                sprint_id=sprint_id,
                board_id=self._board_id,
            )

        def _on_done(issues):
            self._gen_btn.setEnabled(True)
            self._people_status.setText(f"✓ {len(issues)} issues fetched.")
            self._build_people_report(issues, assignees, scope_label)
            self._save_people_btn.setEnabled(True)

        def _on_err(e):
            self._gen_btn.setEnabled(True)
            self._people_status.setText(f"✗ {e}")
            self._people_browser.setHtml(
                f"<p style='color:#f78166;padding:20px;'>Error: {e}</p>"
            )

        worker = _Worker(_do)
        worker.result.connect(_on_done)
        worker.error.connect(_on_err)
        worker.start()
        self._people_report_worker = worker

    def _build_people_report(self, issues: list, assignees: list, scope_label: str):
        sp    = self._sp_field
        today = date.today().strftime("%Y-%m-%d")

        by_assignee: dict[str, dict] = {}
        for a in assignees:
            by_assignee[a] = {
                "display": a, "total": 0, "done": 0,
                "pts": 0, "done_pts": 0,
                "by_status": {},
                "cycle_times": [],
                "issues": [],
            }

        for iss in issues:
            f     = iss.get("fields", {})
            aobj  = f.get("assignee") or {}
            aname = aobj.get("name") or aobj.get("accountId") or ""
            if aname not in by_assignee:
                continue
            rec = by_assignee[aname]
            rec["display"] = aobj.get("displayName") or aname

            status  = (f.get("status") or {}).get("name", "—")
            pts_raw = f.get(sp) or f.get("customfield_10016")
            try:
                pts = int(float(pts_raw)) if pts_raw is not None else 0
            except (TypeError, ValueError):
                pts = 0

            rec["total"] += 1
            rec["pts"]   += pts
            rec["by_status"][status] = rec["by_status"].get(status, 0) + 1

            if status == "Done":
                rec["done"]     += 1
                rec["done_pts"] += pts
                created  = f.get("created", "")[:10]
                resolved = f.get("resolutiondate", "")[:10]
                if created and resolved:
                    try:
                        ct = (date.fromisoformat(resolved) - date.fromisoformat(created)).days
                        rec["cycle_times"].append(max(0, ct))
                    except ValueError:
                        pass

            rec["issues"].append(iss)

        STATUS_CSS = {
            "To Do":       "#6e7681", "In Progress": "#388bfd",
            "Done":        "#3fb950", "In Review":   "#39d5f5",
            "Blocked":     "#f78166",
        }

        def badge(name):
            col = STATUS_CSS.get(name, "#8b949e")
            return (f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;'
                    f'font-size:11px;font-weight:bold;background:{col}22;color:{col};'
                    f'border:1px solid {col}55;">{name}</span>')

        def bar(pct, colour="#388bfd", width=140):
            filled = max(0, min(pct, 100))
            return (f'<div style="display:inline-block;width:{width}px;height:8px;'
                    f'background:#e0e0e0;border-radius:4px;vertical-align:middle;">'
                    f'<div style="width:{filled}%;height:8px;background:{colour};'
                    f'border-radius:4px;"></div></div>&nbsp;{pct}%')

        td = "padding:8px 12px;border-bottom:1px solid #e0e0e0;vertical-align:middle;"
        th = ("padding:8px 12px;background:#f6f8fa;font-size:11px;letter-spacing:.5px;"
              "text-transform:uppercase;border-bottom:2px solid #d0d7de;text-align:left;")

        summary_rows = []
        for aname in assignees:
            rec = by_assignee.get(aname, {})
            if not rec:
                continue
            done_pct = round(rec["done"] / rec["total"] * 100) if rec["total"] else 0
            pts_pct  = round(rec["done_pts"] / rec["pts"] * 100) if rec["pts"] else 0
            avg_ct   = (round(sum(rec["cycle_times"]) / len(rec["cycle_times"]), 1)
                        if rec["cycle_times"] else "—")
            status_breakdown = " &nbsp; ".join(
                f'{badge(s)} ×{c}' for s, c in sorted(rec["by_status"].items())
            )
            summary_rows.append(
                f"<tr>"
                f"<td><strong>{rec.get('display', aname)}</strong></td>"
                f"<td style='text-align:center;'>{rec['total']}</td>"
                f"<td style='text-align:center;'>{rec['done']}</td>"
                f"<td>{bar(done_pct, '#3fb950')}</td>"
                f"<td style='text-align:center;'>{rec['pts']}</td>"
                f"<td style='text-align:center;'>{rec['done_pts']}</td>"
                f"<td>{bar(pts_pct, '#388bfd')}</td>"
                f"<td style='text-align:center;'>{avg_ct}</td>"
                f"<td>{status_breakdown}</td>"
                f"</tr>"
            )

        detail_sections = []
        for aname in assignees:
            rec = by_assignee.get(aname, {})
            if not rec or not rec["issues"]:
                continue
            rows = []
            for iss in sorted(rec["issues"], key=lambda i: i.get("key", "")):
                f       = iss.get("fields", {})
                key     = iss.get("key", "")
                summ    = f.get("summary", "")
                status  = (f.get("status") or {}).get("name", "—")
                pri     = (f.get("priority") or {}).get("name", "—")
                itype   = (f.get("issuetype") or {}).get("name", "—")
                due     = (f.get("duedate") or "")[:10] or "—"
                pts_raw = f.get(sp) or f.get("customfield_10016")
                try:
                    pts_str = str(int(float(pts_raw))) if pts_raw is not None else "—"
                except (TypeError, ValueError):
                    pts_str = "—"
                resolved = (f.get("resolutiondate") or "")[:10] or "—"
                key_cell = (f'<a href="{self._base_url}/browse/{key}" style="color:#388bfd;">{key}</a>'
                            if self._base_url else key)
                due_style = ""
                if due != "—":
                    try:
                        days = (date.fromisoformat(due) - date.today()).days
                        if days < 0:
                            due_style = "color:#f78166;font-weight:bold;"
                        elif days <= 3:
                            due_style = "color:#e3b341;"
                    except ValueError:
                        pass
                rows.append(
                    f"<tr>"
                    f"<td>{key_cell}</td><td>{summ}</td>"
                    f"<td>{badge(status)}</td>"
                    f"<td style='text-align:center;'>{pts_str}</td>"
                    f"<td style='text-align:center;{due_style}'>{due}</td>"
                    f"<td>{resolved}</td><td>{itype}</td><td>{pri}</td>"
                    f"</tr>"
                )
            done_pct = round(rec["done"] / rec["total"] * 100) if rec["total"] else 0
            detail_sections.append(f"""
<h2 style="margin-top:36px;border-bottom:2px solid #d0d7de;padding-bottom:6px;">
  {rec.get('display', aname)}
  <span style="font-size:13px;font-weight:400;color:#57606a;margin-left:12px;">
    {rec['total']} stories &nbsp;·&nbsp; {rec['done']} done &nbsp;·&nbsp;
    {rec['pts']} pts total &nbsp;·&nbsp; {rec['done_pts']} pts done &nbsp;·&nbsp;
    {done_pct}% complete
  </span>
</h2>
<table>
  <tr>
    <th>Key</th><th>Summary</th><th>Status</th><th>Pts</th>
    <th>Due</th><th>Resolved</th><th>Type</th><th>Priority</th>
  </tr>
  {"".join(rows)}
</table>""")

        self._people_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>People Report — {scope_label}</title>
<style>
  body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
          color:#1f2328;background:#ffffff;margin:0;padding:32px; }}
  h1   {{ font-size:22px;font-weight:700;margin:0 0 4px; }}
  h2   {{ font-size:16px;font-weight:700; }}
  .meta {{ font-size:12px;color:#57606a;margin-bottom:28px; }}
  table {{ border-collapse:collapse;width:100%;font-size:13px;margin-bottom:24px; }}
  th    {{ {th} }}
  td    {{ {td} }}
  tr:last-child td {{ border-bottom:none; }}
  tr:hover td {{ background:#f6f8fa; }}
</style>
</head>
<body>
<h1>People Report</h1>
<div class="meta">
  Scope: {scope_label} &nbsp;·&nbsp;
  People: {", ".join(by_assignee[a].get("display", a) for a in assignees if a in by_assignee)} &nbsp;·&nbsp;
  Generated {today}
</div>

<h2 style="margin-bottom:10px;">Summary</h2>
<table>
  <tr>
    <th>Person</th><th>Stories</th><th>Done</th><th>Story Progress</th>
    <th>Total Pts</th><th>Done Pts</th><th>Points Progress</th>
    <th>Avg Cycle (days)</th><th>By Status</th>
  </tr>
  {"".join(summary_rows)}
</table>

{"".join(detail_sections)}
</body>
</html>"""

        self._people_browser.setHtml(self._people_html)

    def _save_people_html(self):
        from PyQt6.QtWidgets import QFileDialog
        suggested = f"people-report-{date.today()}.html"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save People Report", suggested,
            "HTML Files (*.html);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._people_html)
            QMessageBox.information(self, "Saved", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))
```