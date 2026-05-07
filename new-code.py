def get_project_members(self, project_key: str):
    try:
        encoded = urllib.parse.quote(project_key)
        url = (f"{self.base_url}/rest/api/{self.api_version}/"
               f"user/assignable/search?project={encoded}&maxResults=100")
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result if isinstance(result, list) else []
    except Exception:
        return []
