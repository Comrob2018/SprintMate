def get_projects(self):
    url = f"{self.base_url}/rest/api/{self.api_version}/project?maxResults=100&orderBy=name"
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result if isinstance(result, list) else result.get("values", [])
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} [GET {url}]: {e.read().decode()}")
