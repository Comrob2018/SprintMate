## [2.15.1] — 2026-06-22

### Features

* **Custom display names for instances.** Added a "Display Name" field to the settings dialog for each instance. When set, the name replaces "Primary" / "Secondary" everywhere it appears in the app — the top bar mode indicator, the Switch Instance status message, the sprint load status, and the clone dialog instance selector. Falls back to "PRIMARY" / "SECONDARY" if left blank. Values are persisted via `QSettings` as `primary_display_name` and `secondary_display_name`. A new `_instance_label(mode)` helper on `MainWindow` centralises the fallback logic so all call sites stay consistent.
