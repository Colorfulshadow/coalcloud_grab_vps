import requests
import string
from bs4 import BeautifulSoup
import random
from client import Client
from config import config, ua
from urllib.parse import urlparse, parse_qs


class grab_vps:
    def __init__(self, pid, billingcycle):
        self.pid = pid
        self.billingcycle = billingcycle
        self.client = Client(config)
        self.client.soft_login()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent':ua,
            'Cookie':config.cookie
        })
        self.root = "https://www.coalcloud.net"

    def grab(self):
        post_data = {}
        pid_url = self.root + "/cart.php?a=add&pid=" + self.pid
        response = self.session.get(url=pid_url,allow_redirects=False)
        response = self.session.get(self.root + response.headers['Location'],allow_redirects=False)
        if '缺货' in response.text:
            print('pid为'+self.pid+'的商品暂时缺货...')
            return False
        location= response.headers['Location']
        parsed_url = urlparse(location)
        query_params = parse_qs(parsed_url.query)
        i_value = query_params.get('i', [None])[0]
        if i_value:
            post_data['i'] = i_value
        response = self.session.get(location)

        # 下面这段我也很迷，session在重定向链接中发送的get请求并没有实际效果，所以无奈只能这样发送请求了
        # 已经通过上面的代码解决
        # real_url = response.history[1].url
        # response_real = self.session.get(url=real_url)

        # post request to cart url
        cart_url = self.root + "/cart.php"
        soup = BeautifulSoup(response.text, 'lxml')
        for input_tag in soup.find_all('input'):
            if 'name' in input_tag.attrs and 'value' in input_tag.attrs:
                name = input_tag['name']
                value = input_tag['value']
                post_data[name] = value
        post_data['hostname'] = self.generate_hostname()
        post_data['rootpw'] = self.generate_rootpw()
        post_data['billingcycle'] = self.billingcycle
        post_data['ajax'] = '1'
        post_data['a'] = 'confproduct'
        post_data['configure'] = 'true'
        # post_data['calctotal'] = 'true'
        token_value = post_data.pop('token', None)
        response = self.session.post(url=cart_url, data=post_data)

        # get request to confdomains
        confdomains_url = self.root + "/cart.php?a=confdomains"
        response = self.session.get(url=confdomains_url,allow_redirects=False)

        # get request to checkout
        checkout_url = self.root + "/cart.php?a=checkout&e=false"
        response = self.session.get(url=checkout_url)

        # post request to confirm
        confirm_url = self.root + "/cart.php?a=checkout"
        confirm_data = {
                        'token':token_value,
                        'submit':'true',
                        'custtype':'existing',
                        'user_id':config.user_id,
                        'loginemail':config.username,
                        'loginpassword':config.password,
                        'country':'CN',
                        'paymentmethod':'f2falipay',
                        'ccinfo':'new',
                        'ccnumber':'',
                        'ccexpirydate':'',
                        'cccvv':'',
                        'ccdescription':'',
                        'notes':'',
                        'accepttos':'on'
                        }
        confirm_data_more = self.get_self_info()
        confirm_data.update(confirm_data_more)
        response = self.session.post(url=confirm_url,data=confirm_data,allow_redirects=False)

        # get complete request
        complete_url = self.root + "/cart.php?a=complete"
        response = self.session.get(complete_url,allow_redirects=False)
        return True

    def get_self_info(self):
        url = self.root + "/clientarea.php?action=details"
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        post_data = {}
        for input_tag in soup.find_all('input'):
            if ('name' in input_tag.attrs and 'value' in input_tag.attrs and 'id' in input_tag.attrs and input_tag.get('type') != 'checkbox'):
                name = input_tag['name']
                value = input_tag['value']
                post_data[name] = value
        return post_data

    @staticmethod
    def generate_hostname(prefix="VM-", length=12):
        chars = string.ascii_letters + string.digits
        random_part = ''.join(random.choice(chars) for _ in range(length))
        return prefix + random_part

    @staticmethod
    def generate_rootpw(length=16):
        chars = string.ascii_letters + string.digits
        password = ''.join(random.choice(chars) for _ in range(length))
        return password