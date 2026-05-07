# Removed: Cloud/DC toggle
self.cloud_btn = QPushButton("☁  Jira Cloud")
self.dc_btn = QPushButton("🏢  Data Center / Server")
self.cloud_btn.clicked.connect(lambda: self._set_mode("cloud"))
self.dc_btn.clicked.connect(lambda: self._set_mode("datacenter"))

# Removed: email field
self.email_lbl = QLabel("Email:")
self.email_edit = QLineEdit(settings.get("email", ""))
self.form.addRow(self.email_lbl, self.email_edit)

# Removed: single url/token stored flat
self.url_edit = QLineEdit(settings.get("url", ""))
self.token_edit = QLineEdit(settings.get("token", ""))

# Added: Sentinel/ACYD toggle
self.sentinel_btn = QPushButton("◈  SENTINEL")
self.acyd_btn = QPushButton("◈  ACYD")
self.sentinel_btn.clicked.connect(lambda: self._set_mode(JiraClient.MODE_SENTINEL))
self.acyd_btn.clicked.connect(lambda: self._set_mode(JiraClient.MODE_ACYD))

# Added: internal store for both instances
self._data = {
    JiraClient.MODE_SENTINEL: {
        "url":   settings.get("sentinel_url", ""),
        "token": settings.get("sentinel_token", ""),
    },
    JiraClient.MODE_ACYD: {
        "url":   settings.get("acyd_url", ""),
        "token": settings.get("acyd_token", ""),
    },
}

# Added: OK button now calls _save_and_accept instead of accept
btns.accepted.connect(self._save_and_accept)
