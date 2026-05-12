def get_project_members(self, project_key: str):
    all_users = []
    start = 0
    max_results = 200

    while True:
        url = (f"{self.base_url}/rest/api/{self.api_version}/user/search"
               f"?username=.&maxResults={max_results}&startAt={start}")
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                batch = json.loads(resp.read().decode())
                if not isinstance(batch, list) or not batch:
                    break
                all_users.extend(batch)
                if len(batch) < max_results:
                    break
                start += max_results
        except Exception:
            break

    return all_users
