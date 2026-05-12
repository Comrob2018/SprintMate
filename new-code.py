def get_boards(self, project_key: str):
    url = f"{self.base_url}/rest/agile/1.0/board?projectKeyOrId={project_key}"
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()).get("values", [])
    except urllib.error.HTTPError:
        return []
    except Exception:
        return []

def get_issue_types(self, project_key: str):
    try:
        result = self._request("GET", f"project/{project_key}")
        return result.get("issueTypes", [])
    except Exception:
        return []
