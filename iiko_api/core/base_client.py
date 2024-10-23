import requests


class BaseClient:
    def __init__(self, base_url, login, hash_password):
        self.base_url = base_url
        self.secret = hash_password
        self.username = login
        self.session = requests.Session()
        self.token = None

    def login(self):
        endpoint = "/resto/api/auth"
        url = f"{self.base_url}{endpoint}"
        params = {"login": self.username, "pass": self.secret}
        self.token = self.session.get(url=url, params=params).text
        print(self.token)

    def logout(self):
        endpoint = "/resto/api/logout"
        params = {"token": self.token}
        r = self.session.get(f"{self.base_url}{endpoint}", params=params)
        print(r.text)

    def _get(self, endpoint, params=None):
        return self.session.get(self.base_url + endpoint, params=params)

    def _post(self, endpoint, data=None):
        return self.session.post(self.base_url + endpoint, data=data)
