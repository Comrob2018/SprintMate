Your Jira project has required custom fields and restricted priorities. You need to handle both:
1. Priority — fetch the valid priorities for the project instead of using a hardcoded list. Update NewStoryDialog to accept and use them:

# Change the priority combo section in __init__:
self.priority_combo = QComboBox()
for p in priorities:  # passed in from caller
    self.priority_combo.addItem(p.get("name"), p.get("name"))
form.addRow("Priority:", self.priority_combo)


Update the signature:

def __init__(self, project_key: str, issue_types: list, sprints: list, 
             priorities: list, parent=None):


And pass priorities when opening the dialog in _open_new_story:

dlg = NewStoryDialog(
    project_key=key,
    issue_types=[...],
    sprints=self._sprints,
    priorities=self._client.get_priorities(),
    parent=self,
)


2. Required custom fields — add the three required fields to NewStoryDialog. You’ll need to fetch their allowed values first. Add to JiraClient:

def get_field_allowed_values(self, project_key: str, field_id: str):
    """Fetch allowed values for a custom field via createmeta."""
    url = (f"{self.base_url}/rest/api/{self.api_version}/issue/createmeta"
           f"?projectKeys={project_key}&expand=projects.issuetypes.fields")
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            meta = json.loads(resp.read().decode())
            projects = meta.get("projects", [])
            if not projects:
                return []
            for issuetype in projects[0].get("issuetypes", []):
                fields = issuetype.get("fields", {})
                if field_id in fields:
                    return fields[field_id].get("allowedValues", [])
            return []
    except Exception:
        return []


Then in _open_new_story, fetch the allowed values and pass them in:

def _open_new_story(self):
    key = self.project_combo.currentData()
    if not key or not self._client:
        return

    self._busy(True)
    self._status("Loading project metadata…")
    try:
        priorities = self._client.get_priorities()
        activity_types = self._client.get_field_allowed_values(key, "customfield_18111")
        sub_categories = self._client.get_field_allowed_values(key, "customfield_16006")
        elements = self._client.get_field_allowed_values(key, "customfield_12132")
    except Exception as e:
        self._busy(False)
        QMessageBox.critical(self, "Error", f"Could not load project metadata:\n{e}")
        return
    self._busy(False)

    dlg = NewStoryDialog(
        project_key=key,
        issue_types=[{"name": self.edit_panel.issuetype_combo.itemText(i),
                      "id": self.edit_panel.issuetype_combo.itemData(i)}
                     for i in range(self.edit_panel.issuetype_combo.count())],
        sprints=self._sprints,
        priorities=priorities,
        activity_types=activity_types,
        sub_categories=sub_categories,
        elements=elements,
        parent=self,
    )


Update NewStoryDialog.__init__ to accept and display the new fields:

def __init__(self, project_key: str, issue_types: list, sprints: list,
             priorities: list, activity_types: list, sub_categories: list,
             elements: list, parent=None):
    # ... existing code ...

    # Priority — from API
    self.priority_combo = QComboBox()
    for p in priorities:
        self.priority_combo.addItem(p.get("name"), p.get("name"))
    form.addRow("Priority:", self.priority_combo)

    # Activity Type (customfield_18111)
    self.activity_combo = QComboBox()
    for a in activity_types:
        self.activity_combo.addItem(a.get("value", "?"), a.get("id"))
    form.addRow("Activity Type *:", self.activity_combo)

    # Sub-Category (customfield_16006)
    self.subcategory_combo = QComboBox()
    for s in sub_categories:
        self.subcategory_combo.addItem(s.get("value", "?"), s.get("id"))
    form.addRow("Sub-Category *:", self.subcategory_combo)

    # Element (customfield_12132)
    self.element_combo = QComboBox()
    for e in elements:
        self.element_combo.addItem(e.get("value", "?"), e.get("id"))
    form.addRow("Element *:", self.element_combo)


Update get_values:

def get_values(self) -> dict:
    return {
        "summary":       self.summary_edit.text().strip(),
        "issue_type":    self.type_combo.currentData(),
        "priority":      self.priority_combo.currentData(),
        "story_points":  self.points_combo.currentData(),
        "assignee":      self.assignee_edit.text().strip(),
        "sprint_id":     self.sprint_combo.currentData(),
        "due_date":      self.due_date.date().toString("yyyy-MM-dd") if self.due_check.isChecked() else None,
        "description":   self.desc_edit.toPlainText().strip(),
        "activity_type": self.activity_combo.currentData(),
        "sub_category":  self.subcategory_combo.currentData(),
        "element":       self.element_combo.currentData(),
    }


Finally update create_issue in JiraClient to include the custom fields:

def create_issue(self, project_key, summary, description, issuetype_id,
                 story_points=None, feature_link=None, priority=None,
                 due_date=None, activity_type=None, sub_category=None,
                 element=None):
    fields = {
        "project":   {"key": project_key},
        "summary":   summary,
        "description": description,
        "issuetype": {"id": issuetype_id},
    }
    if priority:
        fields["priority"] = {"name": priority}
    if story_points is not None:
        fields[self.story_point_field_id] = story_points
    if feature_link:
        fields[self.feature_link_field_id] = feature_link
    if due_date:
        fields["duedate"] = due_date
    if activity_type:
        fields["customfield_18111"] = {"id": activity_type}
    if sub_category:
        fields["customfield_16006"] = {"id": sub_category}
    if element:
        fields["customfield_12132"] = {"id": element}

    return self._request("POST", "issue", {"fields": fields})


And update the call in _create_story_with_assignee:

def _create_story_with_assignee(self, project_key: str, vals: dict):
    issue = self._client.create_issue(
        project_key=project_key,
        summary=vals["summary"],
        description=vals["description"],
        issuetype_id=vals["issue_type"],
        story_points=vals["story_points"],
        priority=vals["priority"],
        due_date=vals["due_date"],
        activity_type=vals.get("activity_type"),
        sub_category=vals.get("sub_category"),
        element=vals.get("element"),
    )
    key = issue.get("key")
    if key and vals.get("assignee_id"):
        self._client.update_issue(key, {"assignee": {"name": vals["assignee_id"]}})
    if key and vals.get("sprint_id"):
        self._client.move_to_sprint(key, vals["sprint_id"])
    return issue
