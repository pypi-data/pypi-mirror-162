import json
import os
import time
import urllib.parse

import requests

import lbgcli.meta
from lbgcore.image import Image
from lbgcore.job import Job
from lbgcore.jobgroup import JobGroup
from lbgcore.machine import Machine
from lbgcore.program import Program
from lbgcore.server import Server


class RequestInfoException(Exception):
    pass


class Client:
    def __init__(self, email=None, password=None, token=None, config_file_location='~/.lebesgue_config.json',
                 base_url='https://bohrium.dp.tech', use_config_file=False):
        self.config = {}
        config_file_location_expand = os.path.expanduser(config_file_location)
        file_data = {}
        self.token = ''
        self.user_id = None
        if use_config_file:
            if os.path.exists(config_file_location_expand):
                with open(config_file_location_expand, 'r') as f:
                    file_data = json.loads(f.read())
            self.config['email'] = file_data.get('email', email)
            self.config['password'] = file_data.get('password', password)
            self.base_url = file_data.get('base_url', base_url)
        else:
            self.config['email'] = email
            self.config['password'] = password
            self.base_url = base_url
        if token is not None:
            self.token = token
        else:
            self._login()
        self.program = Program(self)
        self.server = Server(self)
        self.image = Image(self)
        self.job_group = JobGroup(self)
        self.job = Job(self)
        self.machine = Machine(self)

    def post(self, url, data=None, header=None, params=None, retry=5):
        return self._req('POST', url, data=data, header=header, params=params, retry=retry)

    def get(self, url, header=None, params=None, retry=5):
        return self._req('GET', url, header=header, params=params, retry=retry)

    def _req(self, method, url, data=None, header=None, params=None, retry=5):
        short_url = url
        url = urllib.parse.urljoin(self.base_url, url)
        if header is None:
            header = {}
        if self.token:
            header['Authorization'] = f'jwt {self.token}'
        header["bohr-client"] = f"utility:{lbgcli.meta.version}"
        err = None
        for i in range(retry):
            resp = None
            if method == 'GET':
                resp = requests.get(url, params=params, headers=header)
            else:
                resp = requests.post(url, json=data, params=params, headers=header)
            if not resp.ok:
                try:
                    result = resp.json()
                    err = result.get("error")
                except:
                    pass
                time.sleep(0.1 * i)
                continue
            result = resp.json()
            if result['code'] == '0000' or result['code'] == 0:
                return result.get('data', {})
            else:
                err = result.get('message') or result.get('error')
                break
        raise RequestInfoException(short_url, err)

    def _login(self):
        if self.config['email'] is None or self.config['password'] is None:
            raise RequestInfoException('can not find login information, please check your config')
        post_data = {
            'email': self.config['email'],
            'password': self.config['password']
        }
        resp = self.post('/account/login', post_data)
        self.token = resp['token']
        # print(self.token)
        self.user_id = resp['user_id']
