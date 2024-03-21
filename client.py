import requests
import re
from bs4 import BeautifulSoup
from config import ua, Config

class Client:
    def __init__(self,config: Config):
        self.config = config
        self.root = "https://www.coalcloud.net"

    def soft_login(self):
        if self.config.cookie:
            self.cookie = self.config.cookie
            try:
                email_address = self.get_self_mail()
                if email_address == self.config.username:
                    print("软登录成功")
                    return True
            except Exception:
                pass
        return self.login()

    def login(self):
        session = requests.Session()
        session.headers.update({"User-Agent": ua})
        url_login = self.root+"/login"
        response = session.get(url_login)
        token = self.get_token(response.text)
        login_data = {
            "token": token,
            "username": self.config.username,
            "password": self.config.password
        }
        login_response = session.post(url_login,login_data)
        if (match := re.search(r'<title>.*?用户中心.*?</title>', login_response.text)):
            print("登陆成功")
            cookies_dict = session.cookies.get_dict()
            cookies_string = '; '.join([f'{key}={value}' for key, value in cookies_dict.items()])
            self.config.cookie = cookies_string
            user_id = self.get_user_id()
        else:
            raise '登录失败，请自行查明原因'

    def get_token(self,html:str):
        csrfToken = re.search(r"var csrfToken = '([^']+)'", html, re.DOTALL)
        csrfToken_str = csrfToken.group(1) if csrfToken else None
        self.config.token = csrfToken_str
        return csrfToken_str if csrfToken_str else None

    def get_self_mail(self):
        url = self.root + "/clientarea.php?action=details"
        headers = {
            "Cookie":self.cookie,
            "User_Agent":ua
        }
        response = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(response.text,'lxml')
        email_input = soup.find('input', {'id': 'inputEmail'})
        email_address = email_input.get('value') if email_input else None
        return email_address

    def get_user_id(self):
        url = self.root + "/account/users"
        headers = {
            "Cookie":self.config.cookie,
            "User_Agent":ua
        }
        response = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        a_tag = soup.find('a', class_='btn btn-danger btn-sm btn-remove-user disabled')
        user_id = a_tag.get('data-id')
        self.config.user_id = user_id
        return user_id
