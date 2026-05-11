Replace the assignee combo in NewStoryDialog with a text input, then validate against the API before creating:
1. In NewStoryDialog, replace the assignee combo with a QLineEdit:

# Replace this:
self.assignee_combo = QComboBox()
self.assignee_combo.addItem("— Unassigned —", None)
for m in members:
    uid = m.get("name") or m.get("accountId")
    self.assignee_combo.addItem(m.get("displayName", "?"), uid)
form.addRow("Assignee:", self.assignee_combo)

# With this:
self.assignee_edit = QLineEdit()
self.assignee_edit.setPlaceholderText("Enter display name or username…")
form.addRow("Assignee:", self.assignee_edit)


2. Update get_values in NewStoryDialog:

def get_values(self) -> dict:
    return {
        "summary":      self.summary_edit.text().strip(),
        "issue_type":   self.type_combo.currentData(),
        "priority":     self.priority_combo.currentData(),
        "story_points": self.points_combo.currentData(),
        "assignee":     self.assignee_edit.text().strip(),  # ← raw text now
        "sprint_id":    self.sprint_combo.currentData(),
        "due_date":     self.due_date.date().toString("yyyy-MM-dd") if self.due_check.isChecked() else None,
        "description":  self.desc_edit.toPlainText().strip(),
    }


3. Add a search_user method to JiraClient:

def find_user(self, query: str):
    """Returns the first matching user or None."""
    encoded = urllib.parse.quote(query)
    url = (f"{self.base_url}/rest/api/{self.api_version}/"
           f"user/search?username={encoded}&maxResults=5")
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result[0] if isinstance(result, list) and result else None
    except Exception:
        return None


4. Update _open_new_story in MainWindow to validate before creating:

def _open_new_story(self):
    key = self.project_combo.currentData()
    if not key or not self._client:
        return
    dlg = NewStoryDialog(
        project_key=key,
        issue_types=[{"name": self.edit_panel.issuetype_combo.itemText(i),
                      "id": self.edit_panel.issuetype_combo.itemData(i)}
                     for i in range(self.edit_panel.issuetype_combo.count())],
        sprints=self._sprints,
        parent=self,
    )
    if dlg.exec() == QDialog.DialogCode.Accepted:
        vals = dlg.get_values()
        assignee_text = vals.get("assignee", "").strip()

        # Validate assignee if one was entered
        if assignee_text:
            self._busy(True)
            self._status(f"Looking up user '{assignee_text}'…")
            user = self._client.find_user(assignee_text)
            self._busy(False)
            if not user:
                QMessageBox.warning(
                    self, "User Not Found",
                    f"No Jira user found matching '{assignee_text}'.\n"
                    f"Please check the name and try again."
                )
                return
            vals["assignee_id"] = user.get("name") or user.get("accountId")
            vals["assignee_display"] = user.get("displayName", assignee_text)
            self._status(f"Found user: {vals['assignee_display']}")
        else:
            vals["assignee_id"] = None

        self._busy(True)
        self._status("Creating story…")
        self._spawn(
            self._create_story_with_assignee, key, vals,
            on_result=self._on_story_created,
        )

def _create_story_with_assignee(self, project_key: str, vals: dict):
    issue = self._client.create_issue(
        project_key=project_key,
        summary=vals["summary"],
        description=vals["description"],
        issuetype_id=vals["issue_type"],
        story_points=vals["story_points"],
        priority=vals["priority"],
        due_date=vals["due_date"],
    )
    # Assign and move to sprint after creation
    key = issue.get("key")
    if key and vals.get("assignee_id"):
        self._client.update_issue(key, {"assignee": {"name": vals["assignee_id"]}})
    if key and vals.get("sprint_id"):
        self._client.move_to_sprint(key, vals["sprint_id"])
    return issue


5. Update NewStoryDialog.__init__ signature since we no longer need to pass members in:

# Change:
def __init__(self, project_key: str, members: list, issue_types: list,
             sprints: list, parent=None):

# To:
def __init__(self, project_key: str, issue_types: list,
             sprints: list, parent=None):


The flow is now: dialog opens → user types a name → hits Create Story → app looks up the user via API → if not found, shows a warning and stops → if found, creates the story and assigns it.​​​​​​​​​​​​​​​​