def _save_and_accept(self):
    self._data[self._mode]["url"]   = self.url_edit.text().strip()
    self._data[self._mode]["token"] = self.token_edit.text().strip()
    self.accept()

def get_settings(self):
    return {
        "mode":           self._mode,
        "sentinel_url":   self._data[JiraClient.MODE_SENTINEL]["url"],
        "sentinel_token": self._data[JiraClient.MODE_SENTINEL]["token"],
        "acyd_url":       self._data[JiraClient.MODE_ACYD]["url"],
        "acyd_token":     self._data[JiraClient.MODE_ACYD]["token"],
        # Active instance shortcuts
        "url":   self._data[self._mode]["url"],
        "token": self._data[self._mode]["token"],
    }
