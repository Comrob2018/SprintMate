Six changes:
1. _data in SettingsDialog.__init__ — added default_board:

# Added to both Sentinel and ACYD
"default_board": settings.get("sentinel_default_board", ""),
"default_board": settings.get("acyd_default_board", ""),


2. Settings form — added Default Board field:

self.default_board_edit = QLineEdit()
self.default_board_edit.setPlaceholderText("e.g. MDT board  (auto-selects on connect)")
form.addRow("Default Board:", self.default_board_edit)


3. _set_mode — saves default_board when switching instances:

# Added
self._data[self._mode]["default_board"] = self.default_board_edit.text().strip()


4. _set_mode — loads default_board when switching instances:

# Added
self.default_board_edit.setText(self._data[mode].get("default_board", ""))


5. get_settings — returns default_board for both instances:

# Added
"sentinel_default_board": self._data[JiraClient.MODE_SENTINEL].get("default_board", ""),
"acyd_default_board":     self._data[JiraClient.MODE_ACYD].get("default_board", ""),


6. _on_boards_loaded in MainWindow — auto-selects default board:

# Added after populating board combo
mode = self._settings.get("mode", JiraClient.MODE_SENTINEL)
default_board = self._settings.get(f"{mode}_default_board", "").lower()
if default_board:
    for i in range(self.board_combo.count()):
        if default_board in self.board_combo.itemText(i).lower():
            self.board_combo.setCurrentIndex(i)
            break
