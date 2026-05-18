Here are the exact changes, in order:

1. _parse_comments_file — replace paired_key with paired_keys list

Find:

            paired_key = keys_found[1] if len(keys_found) >= 2 else None

            for key in keys_found[:2]:
                result[key] = {
                    "comment":    comment,
                    "summary":    summary,
                    "assignee":   assignee,
                    "paired_key": paired_key if paired_key != key else keys_found[0],
                }


Replace with:

            all_keys = list(dict.fromkeys(keys_found[:2]))  # deduplicated, max 2

            for key in all_keys:
                result[key] = {
                    "comment":     comment,
                    "summary":     summary,
                    "assignee":    assignee,
                    "paired_keys": [k for k in all_keys if k != key],
                }


2. _parse_comments_csv — split key column on commas, keep key2 as fallback

Find:

                for row in reader:
                    key     = (row.get(key_col)      or "").strip().upper()
                    summary = (row.get(summary_col)   or "").strip() if summary_col  else ""
                    assignee= (row.get(assignee_col)  or "").strip() if assignee_col else ""
                    comment = (row.get(comment_col)   or "").strip()
                    key2    = (row.get(key2_col)      or "").strip().upper() if key2_col else ""

                    if key2 and not re.match(KEY_RE, key2):
                        key2 = ""

                    if not key or not comment:
                        continue

                    paired = key2 or None
                    result[key] = {
                        "comment":    comment,
                        "summary":    summary,
                        "assignee":   assignee,
                        "paired_key": paired,
                    }
                    if paired:
                        result[paired] = {
                            "comment":    comment,
                            "summary":    summary,
                            "assignee":   assignee,
                            "paired_key": key,
                        }


Replace with:

                for row in reader:
                    raw_key  = (row.get(key_col) or "").strip()
                    summary  = (row.get(summary_col)  or "").strip() if summary_col  else ""
                    assignee = (row.get(assignee_col) or "").strip() if assignee_col else ""
                    comment  = (row.get(comment_col)  or "").strip()

                    if not raw_key or not comment:
                        continue

                    # Support comma-separated keys in the key column
                    all_keys = [
                        k.strip().upper() for k in raw_key.split(",")
                        if re.match(KEY_RE, k.strip().upper())
                    ]

                    # Fall back to legacy key2 column if only one key in key column
                    if len(all_keys) == 1 and key2_col:
                        key2 = (row.get(key2_col) or "").strip().upper()
                        if key2 and re.match(KEY_RE, key2):
                            all_keys.append(key2)

                    all_keys = list(dict.fromkeys(all_keys))  # deduplicate, preserve order

                    if not all_keys:
                        continue

                    for key in all_keys:
                        result[key] = {
                            "comment":     comment,
                            "summary":     summary,
                            "assignee":    assignee,
                            "paired_keys": [k for k in all_keys if k != key],
                        }


3. cross_map build loop in _import_comments — use paired_keys list

Find:

        cross_map = {}
        if other_client:
            for key, entry in parsed.items():
                paired = entry.get("paired_key")
                if paired and paired in parsed:
                    if key in loaded_keys and paired not in loaded_keys:
                        cross_map[key] = paired
                    continue


Replace with:

        cross_map = {}
        if other_client:
            for key, entry in parsed.items():
                paired_keys = entry.get("paired_keys") or []
                explicit = [p for p in paired_keys if p in parsed and p not in loaded_keys]
                if explicit:
                    if key in loaded_keys:
                        cross_map[key] = explicit
                    continue


Also find (end of the same loop):

                if matches:
                    best = _best_match(matches, file_summary, file_assignee)
                    if best:
                        cross_map[key] = best


Replace with:

                if matches:
                    best = _best_match(matches, file_summary, file_assignee)
                    if best:
                        cross_map[key] = [best]


4. Cross-post count in status bar

Find:

                nc = len({k for k in to_post if k in cross_keys})


Replace with:

                nc = sum(1 for k in to_post if cross_map.get(k))


5. _post_imported_comments — iterate the list

Find:

                if other_client and key in cross_map:
                    other_key = cross_map[key]
                    try:
                        other_client.add_comment(other_key, comment)
                    except Exception as e:
                        cross_failures.append(f"{key} → {other_key}: {e}")


Replace with:

                if other_client and key in cross_map:
                    for other_key in cross_map[key]:
                        try:
                            other_client.add_comment(other_key, comment)
                        except Exception as e:
                            cross_failures.append(f"{key} → {other_key}: {e}")


6. ImportCommentsDialog preview table

Find:

            cross_key  = (cross_map or {}).get(key, "")
            cross_item = QTableWidgetItem(cross_key if cross_key else "—")
            cross_item.setForeground(QColor(ACCENT_CYAN if cross_key else TEXT_DIM))


Replace with:

            cross_keys = (cross_map or {}).get(key, [])
            cross_text = ", ".join(cross_keys) if cross_keys else "—"
            cross_item = QTableWidgetItem(cross_text)
            cross_item.setForeground(QColor(ACCENT_CYAN if cross_keys else TEXT_DIM))


7. ImportCommentsDialog detail pane

Find:

        cross    = self._cross_map.get(key, "")


Replace with:

        cross_keys = self._cross_map.get(key, [])
        cross      = ", ".join(cross_keys) if cross_keys else ""

