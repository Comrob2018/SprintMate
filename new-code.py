def _set_mode(self, mode: str):
    # Save current fields before switching
    if hasattr(self, "_mode"):
        self._data[self._mode]["url"]   = self.url_edit.text().strip()
        self._data[self._mode]["token"] = self.token_edit.text().strip()

    self._mode = mode
    is_sentinel = mode == JiraClient.MODE_SENTINEL
    self.sentinel_btn.setChecked(is_sentinel)
    self.acyd_btn.setChecked(not is_sentinel)
    self.instance_lbl.setText(f"{'SENTINEL' if is_sentinel else 'ACYD'} INSTANCE")

    # Load saved values for this instance
    self.url_edit.setText(self._data[mode]["url"])
    self.token_edit.setText(self._data[mode]["token"])
    self.status_lbl.setText("")
