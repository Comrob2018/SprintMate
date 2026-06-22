Here's every change made, in order:

---

**1. `JiraClient.clone_issue` — new method**
Added before `archive_issues`. Creates a new issue on any `JiraClient` instance, used as the target of a clone.

```python
def clone_issue(self, project_key: str, summary: str,
                description: str = "", assignee_name: str = "",
                issue_type: str = "Story") -> dict:
    """Create a new issue — used as the target of a clone operation."""
    fields: dict = {
        "project":   {"key": project_key},
        "summary":   summary,
        "issuetype": {"name": issue_type},
    }
    if description:
        fields["description"] = description
    if assignee_name:
        fields["assignee"] = {"name": assignee_name}
    return self._request("POST", "issue", {"fields": fields})
```

---

**2. `StoryEditPanel._build_ui` — Clone button added to header**
Added alongside the existing Copy Key, Open in Jira, and Attach File buttons.

```python
self.clone_btn = QPushButton("⎘  Clone")
self.clone_btn.setToolTip("Clone this story to a project or instance")
self.clone_btn.setFixedHeight(28)
self.clone_btn.setEnabled(False)
hdr.addWidget(self.title_lbl, 1)
hdr.addWidget(self.key_lbl)
hdr.addWidget(self.copy_key_btn)
hdr.addWidget(self.open_jira_btn)
hdr.addWidget(self.clone_btn)
hdr.addWidget(self.attach_btn)
layout.addLayout(hdr)
```

---

**3. `StoryEditPanel._load_issue_fields` — enable `clone_btn` when issue loads**
Added alongside the existing enables for `copy_key_btn`, `open_jira_btn`, and `attach_btn`.

```python
self.copy_key_btn.setEnabled(True)
self.open_jira_btn.setEnabled(True)
self.clone_btn.setEnabled(True)
self.attach_btn.setEnabled(True)
```

---

**4. `MainWindow._on_story_selected` — wire `clone_btn` to current issue**
Added after the attach button wiring, before the edit/delete comment wiring.

```python
# Re-wire clone button
try:
    self.edit_panel.clone_btn.clicked.disconnect()
except Exception:
    pass
self.edit_panel.clone_btn.clicked.connect(
    lambda: self._clone_issue(issue)
)
```

---

**5. `MainWindow._on_done` (inside `_open_archive`) — disable `clone_btn` when archived story was selected**
Added alongside the other button disables when the edit panel is cleared post-archive.

```python
self.edit_panel.save_btn.setEnabled(False)
self.edit_panel.attach_btn.setEnabled(False)
self.edit_panel.clone_btn.setEnabled(False)
self.edit_panel.open_jira_btn.setEnabled(False)
self.edit_panel.copy_key_btn.setEnabled(False)
```

---

**6. `MainWindow._clone_issue` — new method**
Added before `_check_for_updates`. The full dialog and clone execution logic.

```python
def _clone_issue(self, issue: dict):
    f          = issue.get("fields", {})
    src_key    = issue.get("key", "")
    summary    = f.get("summary", "")
    desc_raw   = f.get("description") or {}
    desc_text  = self.edit_panel._adf_to_text(desc_raw) if isinstance(desc_raw, dict) else str(desc_raw or "")
    aobj       = f.get("assignee") or {}
    assignee   = aobj.get("name") or aobj.get("accountId") or ""
    assignee_display = aobj.get("displayName") or assignee
    itype      = (f.get("issuetype") or {}).get("name", "Story")

    # Determine available instances from saved settings
    s = self._settings
    current_mode  = s.get("mode", JiraClient.MODE_SECONDARY)
    other_mode    = JiraClient.MODE_PRIMARY if current_mode == JiraClient.MODE_SECONDARY else JiraClient.MODE_SECONDARY
    other_url     = s.get(f"{'primary' if other_mode == JiraClient.MODE_PRIMARY else 'secondary'}_url", "")
    other_token   = s.get(f"{'primary' if other_mode == JiraClient.MODE_PRIMARY else 'secondary'}_token", "")
    other_label   = "PRIMARY" if other_mode == JiraClient.MODE_PRIMARY else "SECONDARY"
    current_label = "PRIMARY" if current_mode == JiraClient.MODE_PRIMARY else "SECONDARY"
    has_other     = bool(other_url and other_token)

    # Build and show dialog, load projects lazily per instance,
    # execute clone via target JiraClient, show result with Copy Key / Open in Jira actions.
    # (full method body in the file)
```

---

**Summary of steps in order:**

1. Added `clone_issue` to `JiraClient`
2. Added `clone_btn` to the edit panel header UI
3. Enabled `clone_btn` when an issue is loaded
4. Wired `clone_btn` to `_clone_issue(issue)` in `_on_story_selected`
5. Disabled `clone_btn` when the edit panel is cleared after an archive
6. Added `_clone_issue` method with the full dialog and execution logic