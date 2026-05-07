# After
def _post_imported_comments(self, comments: dict,
                            cross_map: dict = None, other_client=None):
    cross_map = cross_map or {}
    for key, comment in comments.items():
        self._client.add_comment(key, comment)
        if other_client and key in cross_map:
            other_key = cross_map[key]
            try:
                other_client.add_comment(other_key, comment)
            except Exception:
                pass  # Don't fail batch if cross-post fails
    return True
    
def __init__(self, parsed, loaded_keys,
             cross_keys=None, cross_posts=None, parent=None):
            
            
def get_cross_posts(self) -> dict:
    return {k: v for k, v in self._cross_posts.items() if k in self._to_post}
    
def search_issues_jql(self, jql: str, fields: str = "summary,assignee,status"):
    encoded = urllib.parse.quote(jql)
    url = (f"{self.base_url}/rest/api/{self.api_version}/"
           f"search?jql={encoded}&maxResults=50&fields={fields}")
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()).get("issues", [])
    except Exception:
        return []

