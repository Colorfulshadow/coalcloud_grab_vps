import json
import os

class Config:
    __slots__ = ('path', '_username', '_password', '_token', '_cookie', '_user_id')

    def __init__(self):
        self.path = os.path.join(os.path.dirname(__file__), 'config.json')
        self._username = ''
        self._password = ''
        self._token = ''
        self._cookie = ''
        self._user_id = ''
        if not os.path.exists(self.path):
            self._save()
            print("请在config.json中填写username, password")
            exit(0)
        self._load()
        if not self._username or not self._password:
            print("请在config.json中填写username, password")
            exit(0)

    def _save(self):
        c = {
            'username': self._username,
            'password': self._password,
            'token': self._token,
            'cookie': self._cookie,
            'user_id': self._user_id
        }
        with open(self.path, 'w') as f:
            json.dump(c, f, indent=4)

    def _load(self):
        with open(self.path, 'r') as f:
            j = json.load(f)
            self._username = j['username']
            self._password = j['password']
            self._token = j['token']
            self._cookie = j.get('cookie', '')
            self._user_id = j.get('user_id', '')

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self._save()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value
        self._save()

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self._save()

    @property
    def cookie(self):
        return self._cookie

    @cookie.setter
    def cookie(self, value):
        self._cookie = value.split(';')[0]
        self._save()

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value.split(';')[0]
        self._save()

config = Config()
ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safar"
