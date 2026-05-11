Jira Data Center PATs don’t expose an expiry date via the standard REST API, so we can’t query it directly. The best approach is to let the user enter their token expiry date in Settings and then check it on startup and periodically.
Here are all the changes needed:
1. Add expiry date fields to SettingsDialog:

# Add to the form in __init__, after the default_board_edit row:
self.expiry_edit = QDateEdit()
self.expiry_edit.setCalendarPopup(True)
self.expiry_edit.setDisplayFormat("yyyy-MM-dd")
self.expiry_edit.setDate(QDate.currentDate().addDays(90))
form.addRow("Token Expiry Date:", self.expiry_edit)


2. Update _data in SettingsDialog.__init__ to store expiry per instance:

self._data = {
    JiraClient.MODE_SENTINEL: {
        "url":   settings.get("sentinel_url", "https://jira.sde.sp.gc1.myngc.com/"),
        "token": settings.get("sentinel_token", ""),
        "default_project": settings.get("sentinel_default_project", ""),
        "default_board": settings.get("sentinel_default_board", ""),
        "expiry": settings.get("sentinel_expiry", ""),
    },
    JiraClient.MODE_ACYD: {
        "url":   settings.get("acyd_url", "https://jira.northgrum.com/"),
        "token": settings.get("acyd_token", ""),
        "default_project": settings.get("acyd_default_project", ""),
        "default_board": settings.get("acyd_default_board", ""),
        "expiry": settings.get("acyd_expiry", ""),
    },
}


3. Update _set_mode to load/save expiry:

def _set_mode(self, mode: str):
    if hasattr(self, "_mode"):
        self._data[self._mode]["url"]   = self.url_edit.text().strip()
        self._data[self._mode]["token"] = self.token_edit.text().strip()
        self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()
        self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()
        self._data[self._mode]["expiry"] = self.expiry_edit.date().toString("yyyy-MM-dd")

    self._mode = mode
    is_sentinel = mode == JiraClient.MODE_SENTINEL
    self.sentinel_btn.setChecked(is_sentinel)
    self.acyd_btn.setChecked(not is_sentinel)
    self.instance_lbl.setText(f"{'SENTINEL' if is_sentinel else 'ACYD'} INSTANCE")

    self.url_edit.setText(self._data[mode]["url"])
    self.token_edit.setText(self._data[mode]["token"])
    self.default_project_edit.setText(self._data[mode]["default_project"])
    self.default_board_edit.setText(self._data[mode].get("default_board", ""))
    expiry = self._data[mode].get("expiry", "")
    if expiry:
        self.expiry_edit.setDate(QDate.fromString(expiry, "yyyy-MM-dd"))
    self.status_lbl.setText("")


4. Update _save_and_accept and get_settings:

def _save_and_accept(self):
    self._data[self._mode]["url"]   = self.url_edit.text().strip()
    self._data[self._mode]["token"] = self.token_edit.text().strip()
    self._data[self._mode]["default_project"] = self.default_project_edit.text().strip().upper()
    self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()
    self._data[self._mode]["expiry"] = self.expiry_edit.date().toString("yyyy-MM-dd")
    self.accept()

def get_settings(self):
    return {
        "mode":           self._mode,
        "sentinel_url":   self._data[JiraClient.MODE_SENTINEL]["url"],
        "sentinel_token": self._data[JiraClient.MODE_SENTINEL]["token"],
        "sentinel_expiry": self._data[JiraClient.MODE_SENTINEL]["expiry"],
        "acyd_url":       self._data[JiraClient.MODE_ACYD]["url"],
        "acyd_token":     self._data[JiraClient.MODE_ACYD]["token"],
        "acyd_expiry":    self._data[JiraClient.MODE_ACYD]["expiry"],
        "url":   self._data[self._mode]["url"],
        "token": self._data[self._mode]["token"],
        "sentinel_default_project": self._data[JiraClient.MODE_SENTINEL]["default_project"],
        "acyd_default_project":     self._data[JiraClient.MODE_ACYD]["default_project"],
        "sentinel_default_board": self._data[JiraClient.MODE_SENTINEL].get("default_board", ""),
        "acyd_default_board":     self._data[JiraClient.MODE_ACYD].get("default_board", ""),
    }


5. Add a _check_token_expiry method to MainWindow and call it from _open_settings:

def _check_token_expiry(self):
    today = QDate.currentDate()
    for instance, label in [
        (JiraClient.MODE_SENTINEL, "SENTINEL"),
        (JiraClient.MODE_ACYD, "ACYD"),
    ]:
        expiry_str = self._settings.get(f"{instance.lower()}_expiry", "")
        if not expiry_str:
            continue
        expiry = QDate.fromString(expiry_str, "yyyy-MM-dd")
        if not expiry.isValid():
            continue
        days_left = today.daysTo(expiry)
        if days_left < 0:
            QMessageBox.critical(
                self, f"{label} Token Expired",
                f"Your {label} PAT token expired {abs(days_left)} day(s) ago.\n"
                f"Please update your token in Settings."
            )
        elif days_left in (30, 7, 1):
            QMessageBox.warning(
                self, f"{label} Token Expiring Soon",
                f"Your {label} PAT token expires in {days_left} day(s) "
                f"({expiry_str}).\nPlease update your token in Settings."
            )

def _open_settings(self):
    dlg = SettingsDialog(self._settings, self)
    if dlg.exec() == QDialog.DialogCode.Accepted:
        self._settings = dlg.get_settings()
        mode = self._settings.get("mode", JiraClient.MODE_SENTINEL)
        self._client = JiraClient(
            self._settings["url"],
            self._settings["token"],
            mode
        )
        mode_label = "SENTINEL" if mode == JiraClient.MODE_SENTINEL else "ACYD"
        self.edit_panel._sp_field = self._client.story_point_field_id
        self.edit_panel._fl_field = self._client.feature_link_field_id
        self._sp_field = self._client.story_point_field_id
        self.mode_indicator.setText(f"◈  {mode_label}")
        self.refresh_btn.setEnabled(True)
        self._check_token_expiry()  # ← add this
        self._load_projects()


6. Also call it on startup from __init__ so the warning shows when the app opens:

def __init__(self):
    super().__init__()
    self.setWindowTitle("SprintMate")
    self.setMinimumSize(1200, 760)
    self.setStyleSheet(STYLESHEET)

    self._settings = {}
    self._client: JiraClient | None = None
    self._boards = []
    self._sprints = []
    self._issues = []
    self._workers = []

    self._build_ui()
    self._status("Ready — configure connection to get started.")
    self._check_token_expiry()  # ← add this


The warning will fire exactly on the 30, 7, and 1 day marks. If you want it to warn for any day within those thresholds (e.g. warn every day once under 7 days), change the elif days_left in (30, 7, 1) condition to:

elif days_left <= 30:
    urgency = "critical" if days_left <= 1 else "warning"
    msg = QMessageBox.critical if urgency == "critical" else QMessageBox.warning
    msg(
        self, f"{label} Token Expiring Soon",
        f"Your {label} PAT token expires in {days_left} day(s) "
        f"({expiry_str}).\nPlease update your token in Settings."
    )
