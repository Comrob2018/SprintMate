def get_priorities(self):
    url = f"{self.base_url}/rest/api/{self.api_version}/priority/search?maxResults=50"
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            # v3 returns {values: [...]}, v2 returns a list directly
            if isinstance(result, list):
                return result
            return result.get("values", [])
    except Exception:
        # Fall back to plain /priority for older DC versions
        try:
            result = self._request("GET", "priority")
            return result if isinstance(result, list) else []
        except Exception:
            return []
