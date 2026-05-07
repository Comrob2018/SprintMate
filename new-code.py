
# After
def search_users(self, query: str):
    encoded = urllib.parse.quote(query)
    url = f"{self.base_url}/rest/api/{self.api_version}/user/search?query={encoded}&maxResults=20"
    req = urllib.request.Request(url, headers=self.headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())
        return result if isinstance(result, list) else []
