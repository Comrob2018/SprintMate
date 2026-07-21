Just one change, three lines affected.

**What changed**

In `_populate_table` in `MainWindow`, the assignee cell build went from this:

```python
assignee = f.get("assignee")
aname = assignee.get("displayName", "Unassigned") if assignee else "—"
initials = "".join(w[0].upper() for w in aname.split()[:2]) if aname != "—" else "—"
a_item = QTableWidgetItem(f"  {initials}  {aname}")
a_item.setForeground(QColor(TEXT_SEC))
a_item.setToolTip(aname)
self.table.setItem(row, COL_ASSIGNEE, a_item)
```

to this:

```python
assignee = f.get("assignee")
aname = assignee.get("displayName", "Unassigned") if assignee else "—"
a_item = QTableWidgetItem(aname)
a_item.setForeground(QColor(TEXT_SEC))
a_item.setToolTip(aname)
self.table.setItem(row, COL_ASSIGNEE, a_item)
```

**Steps**

1. Find `_populate_table` in `MainWindow` (search for `def _populate_table` — there are two, you want the one in `MainWindow` not `EditPanel`)
2. Find the block that builds `a_item` for `COL_ASSIGNEE`
3. Delete the `initials = ...` line
4. Change `QTableWidgetItem(f"  {initials}  {aname}")` to `QTableWidgetItem(aname)`
5. Leave the `setForeground`, `setToolTip`, and `setItem` lines unchanged

That's it — the tooltip still shows the full name, the colour is unchanged, filtering works normally again.