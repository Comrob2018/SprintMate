# After
MODE_SENTINEL = "sentinel"
MODE_ACYD     = "acyd"

def __init__(self, base_url, token, mode=MODE_SENTINEL, email=""):
    self.api_version = "2"  # Both are Data Center
    auth = f"Bearer {token}"
    
body = {"body": text}

# After
fields["description"] = description
fields["assignee"] = {"name": assignee_id}


# After
self._client = JiraClient(url, token, mode)
mode_label = "SENTINEL" if mode == JiraClient.MODE_SENTINEL else "ACYD"
self.mode_indicator.setText(f"◈  {mode_label}")

self.mode_indicator = QLabel("")
self.mode_indicator.setStyleSheet(
    f"color: {ACCENT_BLUE}; font-size: 11px; letter-spacing: 2px; padding: 0 12px;"
)
tb_layout.addWidget(self.mode_indicator)
