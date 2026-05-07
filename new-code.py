def get_project_members(self, project_key: str):
    encoded = urllib.parse.quote(project_key)
    url = (f"{self.base_url}/rest/api/{self.api_version}/"
           f"user/assignable/search?project={encoded}&maxResults=100")
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result if isinstance(result, list) else []
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} [GET {url}]: {e.read().decode()}")
    except Exception:
        return []
