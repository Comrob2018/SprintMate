def get_project_members(self, project_key: str):
    encoded = urllib.parse.quote(project_key)
    all_members = []
    start = 0
    max_results = 200

    while True:
        url = (f"{self.base_url}/rest/api/{self.api_version}/"
               f"user/assignable/search?project={encoded}"
               f"&maxResults={max_results}&startAt={start}")
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                batch = result if isinstance(result, list) else []
                if not batch:
                    break
                all_members.extend(batch)
                if len(batch) < max_results:
                    break
                start += max_results
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} [GET {url}]: {e.read().decode()}")
        except Exception:
            break

    return all_members


def set_members(self, members: list):
    if members and "to" in members[0]:
        return
    self._members = members
    
    # Remember who's currently assigned before we rebuild the list
    current_aid = self.assignee_combo.currentData()
    
    self.assignee_combo.clear()
    self.assignee_combo.addItem("— Unassigned —", None)
    for m in members:
        uid = m.get("name") or m.get("key") or m.get("accountId")
        display = m.get("displayName") or m.get("name") or "?"
        self.assignee_combo.addItem(display, uid)
    
    # Reapply the selection after rebuilding
    if current_aid:
        for i in range(self.assignee_combo.count()):
            if self.assignee_combo.itemData(i) == current_aid:
                self.assignee_combo.setCurrentIndex(i)
                break
