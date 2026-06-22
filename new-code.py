 Here's every change in order:

---

**1. `SettingsDialog._build_ui` — Display Name field added to form**

```python
# Before url_edit
self.display_name_edit = QLineEdit()
self.display_name_edit.setPlaceholderText("e.g. Production, Staging, Dev…")
form.addRow("Display Name:", self.display_name_edit)
_dn_hint = QLabel("Optional. Replaces 'Primary' / 'Secondary' labels throughout the app.")
_dn_hint.setObjectName("dim")
_dn_hint.setWordWrap(True)
form.addRow("", _dn_hint)
```

---

**2. `SettingsDialog._build_ui` — `display_name` added to `_data` for both modes**

```python
self._data = {
    JiraClient.MODE_SECONDARY: {
        ...
        "display_name": settings.get("secondary_display_name", ""),
    },
    JiraClient.MODE_PRIMARY: {
        ...
        "display_name": settings.get("primary_display_name", ""),
    },
}
```

---

**3. `SettingsDialog._set_mode` — save, restore, and use `display_name` in instance label**

```python
def _set_mode(self, mode: str):
    if hasattr(self, "_mode"):
        ...
        self._data[self._mode]["display_name"] = self.display_name_edit.text().strip()

    ...
    default_label = "SECONDARY" if is_secondary else "PRIMARY"
    custom_name   = self._data[mode].get("display_name", "").strip()
    self.instance_lbl.setText(f"{custom_name or default_label} INSTANCE")

    ...
    self.display_name_edit.setText(self._data[mode].get("display_name", ""))
```

---

**4. `SettingsDialog._save_and_accept` — persist `display_name`**

```python
self._data[self._mode]["display_name"] = self.display_name_edit.text().strip()
```

---

**5. `SettingsDialog.get_settings` — include `display_name` in returned dict**

```python
"secondary_display_name": self._data[JiraClient.MODE_SECONDARY].get("display_name", ""),
"primary_display_name":   self._data[JiraClient.MODE_PRIMARY].get("display_name", ""),
```

---

**6. `MainWindow._save_settings` — persist both display names to QSettings**

```python
qs.setValue("secondary_display_name", s.get("secondary_display_name", ""))
# ...
qs.setValue("primary_display_name",   s.get("primary_display_name", ""))
```

---

**7. `MainWindow._load_settings` — load both display names from QSettings**

```python
"secondary_display_name": qs.value("secondary_display_name", ""),
# ...
"primary_display_name":   qs.value("primary_display_name", ""),
```

---

**8. `MainWindow._instance_label` — new helper method**

```python
def _instance_label(self, mode: str) -> str:
    """Return the user-set display name for a mode, falling back to PRIMARY/SECONDARY."""
    key = "primary_display_name" if mode == JiraClient.MODE_PRIMARY else "secondary_display_name"
    return self._settings.get(key, "").strip() or (
        "PRIMARY" if mode == JiraClient.MODE_PRIMARY else "SECONDARY"
    )
```

---

**9. Five call sites in `MainWindow` updated to use `_instance_label()`**

| Method | Was | Now |
|---|---|---|
| Auto-connect on startup | `"SECONDARY" if mode == ... else "PRIMARY"` | `self._instance_label(mode)` |
| `_open_settings` | `"SECONDARY" if mode == ... else "PRIMARY"` | `self._instance_label(mode)` |
| `_switch_instance` | `"SECONDARY" if new_mode == ... else "PRIMARY"` | `self._instance_label(new_mode)` |
| `_load_sprint_issues` | `"SECONDARY" if mode == ... else "PRIMARY"` | `self._instance_label(mode)` |
| `_clone_issue` | `"PRIMARY" if other_mode == ... else "SECONDARY"` (×2) | `self._instance_label(other_mode)` / `self._instance_label(current_mode)` |

## [2.15.1] — 2026-06-22

### Features

* **Custom display names for instances.** Added a "Display Name" field to the settings dialog for each instance. When set, the name replaces "Primary" / "Secondary" everywhere it appears in the app — the top bar mode indicator, the Switch Instance status message, the sprint load status, and the clone dialog instance selector. Falls back to "PRIMARY" / "SECONDARY" if left blank. Values are persisted via `QSettings` as `primary_display_name` and `secondary_display_name`. A new `_instance_label(mode)` helper on `MainWindow` centralises the fallback logic so all call sites stay consistent.
