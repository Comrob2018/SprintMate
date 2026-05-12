The issue is that NewStoryDialog gets its members passed in from self.edit_panel._members at the time the dialog opens — but if get_project_members failed due to access restrictions (like on the Sentinel DIT project), that list is empty.
The fix is to pass members from a separate source, or better yet, fetch them fresh specifically for the new story dialog when it opens. The simplest approach is to fall back to a broader user search if the members list is empty:
In _open_new_story, change:

def _open_new_story(self):
    key = self.project_combo.currentData()
    if not key or not self._client:
        return
    
    members = self.edit_panel._members
    
    # If project member fetch failed (access restricted), fall back to
    # searching for all assignable users without a project filter
    if not members:
        try:
            members = self._client.search_users("")
        except Exception:
            members = []

    dlg = NewStoryDialog(
        project_key=key,
        members=members,
        ...
    )


And in JiraClient.search_users, the empty string query may not work on all DC versions — a single space or a wildcard works better:

def search_users(self, query: str):
    encoded = urllib.parse.quote(query or ".")
    url = f"{self.base_url}/rest/api/{self.api_version}/user/search?username={encoded}&maxResults=200"
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result if isinstance(result, list) else []
    except Exception:
        return []


Note username= instead of query= — that’s the correct parameter for DC/Server API v2, and . as the wildcard returns all users.​​​​​​​​​​​​​​​​