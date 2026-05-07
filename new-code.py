1. JiraClient — added _FIELD_MAP and updated __init__:

# Added class variable
_FIELD_MAP = {
    "sentinel": {
        "story_point":  "customfield_10106",
        "feature_link": "customfield_10100",
    },
    "acyd": {
        "story_point":  "customfield_10006",
        "feature_link": "customfield_10000",
    },
}

# Added to __init__
fields = self._FIELD_MAP.get(mode, self._FIELD_MAP["sentinel"])
self.story_point_field  = fields["story_point"]
self.feature_link_field = fields["feature_link"]


2. get_sprint_issues — dynamic field IDs:

# Before
"comment", "issuetype", "customfield_10016", "duedate",

# After
sp = self.story_point_field
fl = self.feature_link_field
fields = ",".join([
    "summary", "assignee", "status", "priority", "description",
    "comment", "issuetype", sp, fl, "duedate",
    "sprint", "closedSprints", "customfield_10020"
])


3. create_issue — story points field:

# Before
fields["customfield_10016"] = story_points

# After
fields[self.story_point_field] = story_points


4. load_issue in StoryEditPanel — story points and feature link:

# Before
pts = fields.get("customfield_10016") or fields.get("story_points")

# After
pts = fields.get(getattr(self, "_sp_field", "customfield_10016")) or fields.get("customfield_10016") or fields.get("story_points")

# Added feature link load
fl_field = getattr(self, "_fl_field", "customfield_10100")
fl_value = fields.get(fl_field) or ""
if isinstance(fl_value, dict):
    fl_value = fl_value.get("url", "") or fl_value.get("id", "")
self.feature_link_edit.setText(str(fl_value) if fl_value else "")


5. _on_save in StoryEditPanel — story points and feature link:

# Before
fields["customfield_10016"] = pts

# After
fields[getattr(self, "_sp_field", "customfield_10016")] = pts

# Added feature link save
fl_field = getattr(self, "_fl_field", "customfield_10100")
fl_val = self.feature_link_edit.text().strip()
if fl_val:
    fields[fl_field] = fl_val


6. _populate_table — dynamic story points field:

# Before
pts = f.get("customfield_10016") or f.get("story_points") or ""

# After
sp_field = getattr(self, "_sp_field", "customfield_10016")
pts = f.get(sp_field) or f.get("customfield_10016") or f.get("story_points") or ""


7. _do_save — retry logic uses dynamic field:

# Before
if "customfield_10016" in str(e):
    fields_no_pts = {k: v for k, v in fields.items() if k != "customfield_10016"}

# After
sp = self._client.story_point_field
if sp in str(e) or "customfield_10016" in str(e):
    fields_no_pts = {k: v for k, v in fields.items() if k not in (sp, "customfield_10016")}


8. _open_settings — sets field IDs on edit panel:

# Added
self.edit_panel._sp_field = self._client.story_point_field
self.edit_panel._fl_field = self._client.feature_link_field
self._sp_field = self._client.story_point_field


9. StoryEditPanel._build_ui — added feature link field:

# Added after assignee
self.feature_link_edit = QLineEdit()
self.feature_link_edit.setPlaceholderText("Feature link URL or ID…")
form.addRow("Feature Link:", self.feature_link_edit)
