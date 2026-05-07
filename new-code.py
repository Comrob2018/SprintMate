def get_project_members(self, project_key: str):
    encoded = urllib.parse.quote(project_key)
    url = (f"{self.base_url}/rest/api/{self.api_version}/"
           f"user/assignable/search?project={encoded}&maxResults=100")
    print(f"DEBUG get_project_members URL: {url}")
    req = urllib.request.Request(url, headers=self.headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            print(f"DEBUG get_project_members type={type(result).__name__} len={len(result) if isinstance(result, list) else 'n/a'}")
            if result:
                print(f"DEBUG first item keys: {list(result[0].keys()) if isinstance(result, list) else list(result.keys())}")
            return result if isinstance(result, list) else []
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} [GET {url}]: {e.read().decode()}")
    except Exception:
        return []