Six changes:
1. _data in SettingsDialog.__init__ — added default_project:

# Before
JiraClient.MODE_SENTINEL: {
    "url":   settings.get("sentinel_url", ""),
    "token": settings.get("sentinel_token", ""),
},

# After
JiraClient.MODE_SENTINEL: {
    "url":             settings.get("sentinel_url", ""),
    "token":           settings.get("sentinel_token", ""),
    "default_project": settings.get("sentinel_default_project", ""),
},


(same for ACYD)
2. Settings form — added Default Project field:

# Added after PAT Token row
self.default_project_edit = QLineEdit()
self.default_project_edit.setPlaceholderText("e.g. MDT  (auto-selects on connect)")
form.addRow("Default Project:", self.default_project_edit)


3. _set_mode — saves/loads default_project when switching instances:

# Added to save block
self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()

# Added to load block
self.default_project_edit.setText(self._data[mode]["default_project"])


4. _save_and_accept — saves default_project before closing:

# Added
self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()


5. get_settings — returns default_project for both instances:

# Added
"sentinel_default_project": self._data[JiraClient.MODE_SENTINEL]["default_project"],
"acyd_default_project":     self._data[JiraClient.MODE_ACYD]["default_project"],


6. _on_projects_loaded in MainWindow — auto-selects default project:

# Added after populating project combo
mode = self._settings.get("mode", JiraClient.MODE_SENTINEL)
default_key = self._settings.get(f"{mode}_default_project", "")
if default_key:
    for i in range(self.project_combo.count()):
        if self.project_combo.itemData(i) == default_key:
            self.project_combo.setCurrentIndex(i)
            break
