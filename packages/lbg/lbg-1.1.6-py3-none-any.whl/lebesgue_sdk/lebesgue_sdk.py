# -*- coding: utf-8 -*-
import json
import os
import subprocess
import time
import uuid
import zipfile
from datetime import datetime
from urllib import parse

import oss2
import requests
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo
from requests_toolbelt import MultipartEncoder
from tqdm import tqdm, trange


def zip_dir(zip_path, out_file, save_files=[]):
    """
    压缩指定文件夹
    :param zip_path: 目标文件夹路径
    :param out_file: 压缩文件保存路径+xxxx.zip
    :param save_files: 需要压缩的文件，空list 则压缩全文件
    :return: 无
    """
    # 转化需要保存的文件地址
    dic_to_save = {}
    for tmp_file in save_files:
        dic_to_save[tmp_file] = 1
    zip = zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(zip_path):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(zip_path, '')
        for filename in filenames:
            # 获取绝对路径
            abs_path = os.path.join(path, filename)
            # 获取相对路径
            file_path = os.path.join(fpath, filename)
            if dic_to_save and (file_path not in dic_to_save):
                continue
            else:
                zip.write(os.path.join(path, filename),
                          os.path.join(fpath, filename))
    zip.close()


def unzip_file(zip_file_path, out_path):
    """
    解压到指定文件夹
    :param zip_file_path:     解压文件目标路径
    :param out_path: 压缩文件路径+名称 /p/a/t/h/job.zip
    return: 无
    """
    zip_file = zipfile.ZipFile(zip_file_path, "r", zipfile.ZIP_DEFLATED)
    for tmp_file in zip_file.namelist():
        zip_file.extract(tmp_file, out_path)


def exec_cmd(cmd):
    p = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


class lebesgue_sdk(object):
    """
    : base_url         host url
    : endpoint
    : bucket
    : login_host       login url
    : web_server       cloudserver/slurm
    : login_callback
    : message_callback
    """

    LEBESGUE_SESSION_LOCATION = '~/.lebesgue_session.json'

    def __init__(self, base_url,
                 endpoint,
                 bucket,
                 login_host=None,
                 web_server="cloudserver",
                 login_callback=None,
                 message_callback=None):
        self.base_url = base_url.strip("/") + '/'
        self.endpoint = endpoint
        self.bucket_name = bucket
        self.login_host = login_host and (login_host.strip("/") + "/") or self.base_url
        self.web_server = web_server
        self.login_callback = login_callback
        self.message_callback = message_callback if message_callback is not None else (lambda x: print(x))
        self.version = 1.0
        self.oss_path = self.endpoint.split("/")
        if self.bucket_name:
            self.oss_path[2] = "%s.%s" % (self.bucket_name, self.oss_path[2]) + "/"
        self.oss_path = "/".join(self.oss_path)
        self.headers = {'Content-Type': 'application/json'}
        self.cookies = {}
        self.username = None
        # self._check_sdk_version()
        self._load_temp()

    def _get_url(self, url, **kwargs):
        url = parse.urljoin(self.base_url, url)
        for i in range(5):
            time.sleep(0.1)
            try:
                kwargs['username'] = self.username
                res = requests.get(url, params=kwargs, headers=self.headers, timeout=30)
                if res.status_code == 500:
                    break
                res.raise_for_status()
                res = res.json()
                if res['code'] == "2100":
                    self.login_err()
                    self.req_err(res.get('message'))
                    break

                if res['code'] != "0000" and res['code'] != 0:
                    self.req_err(res.get('message'))
                    break
                return res['data']
            except Exception as e:
                print("get url %s error: %s" % (url, str(e)))
        return {}

    def _post_url(self, url, json_data, retry_count=1, host=None):
        url = parse.urljoin((host or self.base_url), url)
        for i in range(retry_count):
            time.sleep(0.1)
            try:
                json_data['username'] = json_data.get(
                    'username') or self.username
                res = requests.post(
                    url, json=json_data, headers=self.headers, timeout=30)
                self.cookies = requests.utils.dict_from_cookiejar(
                    res.cookies) or self.cookies
                res.raise_for_status()
                res = res.json()
                if res['code'] == "2100":
                    self.login_err()
                    self.req_err(res.get('message'))
                    break

                if res['code'] != "0000" and res['code'] != 0:
                    self.req_err(res.get('message'))
                    break

                return res['data']
            except Exception as e:
                print("post url %s error: %s" % (url, str(e)))
        return {}

    def upload2native(self, url, file_path):
        url = self.base_url + url
        data = MultipartEncoder(
            fields={'file': (file_path, open(file_path, 'rb'), 'application/zip')})
        ret = requests.post(url, data=data, headers={
            'Content-Type': data.content_type}, cookies=self.cookies)
        ret = json.loads(ret.text)
        return ret

    def write_file(self, _path, write_str):
        with open(_path, 'w') as fp:
            fp.write(write_str)

    def read_file(self, _path):
        try:
            with open(_path, 'r') as fp:
                ret = fp.read()
            return ret
        except:
            pass
        return ''

    def req_err(self, message):
        if self.message_callback is not None:
            self.message_callback(message)

    def login_err(self):
        try:
            os.remove(os.path.expanduser(self.LEBESGUE_SESSION_LOCATION))
            self.login_callback()
        except:
            pass

    # after init, load native file for cookies
    def _load_temp(self):
        data = self.read_file(os.path.expanduser(self.LEBESGUE_SESSION_LOCATION))
        try:
            tmp = json.loads(data)
            self.cookies = tmp.get('cookies')
            userinfo = tmp.get('userinfo')
            self.username = userinfo.get('user_name')
        except:
            return self.login_err()

    def _save_cookies(self, data):
        self.write_file(os.path.expanduser(self.LEBESGUE_SESSION_LOCATION), data)

    # TODO: replace session with jwt
    def login(self, username, password):
        data = self._post_url(
            'account/login', {"username": username, "password": password}, host=self.login_host)
        if not data:
            print("Login failed!")
            return

        self.username = data.get('user_name')
        # print("Welcome ", self.username, "Login succeed!", time.ctime())
        token = data["token"]
        self.headers["Authorization"] = f'jwt {token}'
        # self._save_cookies(json.dumps(
        #     {'cookies': self.cookies, 'userinfo': data}))

    def _upload_file_to_oss(self, oss_task_dir, zip_task_file):
        self.bucket = self._get_oss_bucket()
        total_size = os.path.getsize(zip_task_file)
        part_size = determine_part_size(total_size, preferred_size=1000 * 1024)
        upload_id = self.bucket.init_multipart_upload(oss_task_dir).upload_id
        parts = []
        with open(zip_task_file, 'rb') as fileobj:
            bar_format = "{l_bar}{bar}| {n:.02f}/{total:.02f} %  [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
            pbar = tqdm(total=100, desc="Uploading to oss", smoothing=0.01, bar_format=bar_format)
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                percent = num_to_upload * 100 / (total_size + 1)
                # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                result = self.bucket.upload_part(
                    oss_task_dir, upload_id, part_number, SizedFileAdapter(fileobj, num_to_upload))
                parts.append(PartInfo(part_number, result.etag))
                offset += num_to_upload
                part_number += 1
                pbar.update(percent)
            pbar.close()
        self.bucket.complete_multipart_upload(oss_task_dir, upload_id, parts)

    # compress and upload
    def upload_job_data(self, job_type, zip_path, data_type="zip"):
        task_uuid = uuid.uuid1().hex
        # compress
        save_files = []
        zip_path = os.path.abspath(zip_path)
        if zip_path[-1] == '/' or zip_path[-1] == '\\':
            zip_path = zip_path[:-1]
        zip_task_file = zip_path + '.zip'
        zip_dir(zip_path, zip_task_file, save_files)
        print("Zip File Success!:", zip_task_file)
        # upload
        print("Uploading")
        if self.web_server == 'cloudserver':
            oss_task_dir = os.path.join(
                'dpcloudserver/%s/%s/%s.zip' % (job_type, task_uuid, task_uuid))
            self._upload_file_to_oss(oss_task_dir, zip_task_file)
            # get download url
            oss_task_dir = self.oss_path + oss_task_dir
        elif self.web_server == 'slurm':
            ret = self.upload2native("data/upload_file", zip_task_file)
            if ret['code'] != "0000":
                return ''

            oss_task_dir = ret['data']['file_path']
        print("Uploaded")
        # reset oss_path
        os.remove(zip_task_file)
        return oss_task_dir

    def _get_oss_bucket(self):
        url = "data/get_sts_token"
        data = self._get_url(url=url)
        if 'SecurityToken' not in data:
            return -1
        oss_info = data
        key_id = oss_info['AccessKeyId']
        key_secret = oss_info['AccessKeySecret']
        token = oss_info['SecurityToken']
        auth = oss2.StsAuth(key_id, key_secret, token)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        return bucket

    # download and decompress
    def _download_result(self, oss_path, save_path, retry=5):
        flag = 0
        for i in range(retry):
            try:
                # 从 oss 下载
                if self.web_server == "cloudserver":
                    self.bucket = self._get_oss_bucket()
                    self.bucket.get_object_to_file(oss_path, save_path)

                if self.web_server == "slurm":
                    res = requests.get(oss_path)
                    with open(save_path, "wb") as f:
                        f.write(res.content)
                flag = 1
                break
            except Exception as e:
                print("download error", e)
        if flag == 0:
            print('Download Error!')
            return flag
        return save_path

    def download_job_group_result(self, save_path, job_group_id=-1, job_id=[], append_job_name=False):
        job_list = self.get_job_list(job_group_id)
        not_finished_list = []
        for i in trange(len(job_list)):
            job = job_list[i]
            if job['status'] != 2 or not job.get('result_url'):
                not_finished_list.append(job.get("task_id"))
                continue
            result_url = job['result_url']
            r = requests.get(result_url, stream=True, cookies=self.cookies)
            target_dir = "%s/%s" % (save_path, job_group_id)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            target_job_path = "%s/%s" % (target_dir, job['task_id'])
            with open(target_job_path + '.zip', "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            unzip_file(target_job_path + '.zip', target_job_path)
            os.remove(target_job_path + '.zip')
        if len(not_finished_list) != 0:
            for each in not_finished_list:
                print(f'task {each} not finished yet, skipped.')

    def download_job_result(self, save_path, job_id, append_job_name=False):
        job_detail = self.get_job_detail(job_id)
        result_url = job_detail['result_url']
        r = requests.get(result_url, stream=True, cookies=self.cookies)
        target_dir = "%s/%s" % (save_path, job_detail['job_group_id'])
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        target_job_path = "%s/%s" % (target_dir, job_id)
        with open(target_job_path + '.zip', "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        unzip_file(target_job_path + '.zip', target_job_path)
        os.remove(target_job_path + '.zip')

    # 获取log
    def get_log(self, job_id=-1, task_id=-1):
        pass

    # 获取用户的详情数据
    def get_user_details(self):
        url = 'data/get_user_details'
        data = self._get_url(url)
        return data

    # 查看任务详情
    def job_detail(self, job_id):
        url = 'data/job/%s' % job_id
        return self._get_url(url)

    def _job_status(self, status):
        DSTATUS = {-1: "Failed", 0: "Pending", 1: "Running", 2: "Finish"}
        if status in DSTATUS:
            return DSTATUS[status]

        return "Unknown"

    def format_strftime(self, datetime):
        try:
            fmt = '%Y-%m-%d %H:%M:%S'
            return datetime.strftime(fmt)
        except:
            return None

    def format_strptime(self, strdatetime):
        try:
            fmt = '%Y-%m-%d %H:%M:%S'
            return datetime.strptime(strdatetime, fmt)
        except:
            return None

    # 续跑任务
    def continue_tasks(self, job_id, task_ids):
        url = 'data/continue_tasks'
        data = self._post_url(
            url, json_data={'job_id': job_id, 'task_ids': task_ids})
        return data

    # 查看job的相关信息
    def get_job_result(self, job_id):
        url = 'data/get_job_result'
        data = self._post_url(url, json_data={'job_id': job_id})
        return data

    # 更新job的相关信息
    def update_job_result(self, job_id, result):
        url = 'data/update_job_result'
        if not result:
            return ''
        data = self._post_url(
            url, json_data={'job_id': job_id, 'result': result})
        return data

    # 获取可用机器数量
    def get_available_machine(self):
        url = 'data/get_available_machine'
        data = self._get_url(url)
        return data

    # 查看机器类型
    def get_machine_type_one_page(self, page=1):
        url = 'resources/instances'
        data = self._get_url(url, page=page)
        return data

    def get_machine_type(self):
        machine_type_list = []
        data = self.get_machine_type_one_page()
        total = data['total']
        per_page = data['per_page']
        page_number = 0
        while page_number * per_page < total:
            page_number = page_number + 1
            if page_number > 1:
                data = self.get_machine_type_one_page(page_number)
            machine_type_list.extend(data['items'])
        return machine_type_list

    # ----data/----
    def insert_job(self, oss_path, **kwargs):
        program_id = kwargs['program_id']
        machine_type = kwargs['machine_type']
        cmd = kwargs['command']
        platform = kwargs['platform'],

        post_data = {
            'job_type': 'indicate',
            'program_id': program_id,
            'machine_type': machine_type,
            'cmd': cmd,
            'platform': platform,
            'oss_path': oss_path
        }
        if kwargs.get('command') is not None:
            post_data["cmd"] = kwargs.get('command')
        if kwargs.get('backward_files') is not None:
            post_data["out_files"] = kwargs.get('backward_files')
        if kwargs.get('machine_type') is not None:
            post_data["scass_type"] = kwargs.get('machine_type')
        for k, v in kwargs.items():
            post_data[k] = v
        data = self._post_url(url="data/v2/insert_job", json_data=post_data)
        return data

    def kill_job(self, job_id):
        data = {}
        url = 'data/job/%s/kill' % (job_id)
        data = self._post_url(url=url, json_data=data)
        return data

    def terminate_job(self, job_id):
        data = {}
        url = 'data/job/%s/terminate' % (job_id)
        data = self._post_url(url=url, json_data=data)
        return data

    def terminate_job_group(self, job_group_id):
        data = {}
        url = 'data/job_group/%s/terminate' % (job_group_id)
        data = self._post_url(url=url, json_data=data)
        return data

    def delete_job_group(self, job_group_id):
        data = {}
        url = 'data/job_group/%s/del' % (job_group_id)
        data = self._post_url(url=url, json_data=data)
        return data

    def delete_job(self, job_id):
        data = {}
        url = 'data/job/%s/del' % (job_id)
        data = self._post_url(url=url, json_data=data)
        return data

    def get_summary(self, program_id):
        url = 'data/statistics/overview'
        data = self._get_url(url, program_id=program_id)
        return data

    def get_job_detail(self, job_id):
        url = 'data/job/%s' % (job_id)
        data = self._get_url(url, version=2)
        return data

    def get_job_group_list_one_page(self, program_id, page=1):
        url = 'data/jobs'
        data = self._get_url(url, program_id=program_id, page=page)
        return data

    def get_job_group_list(self, program_id):
        job_group_list = []
        data = self.get_job_group_list_one_page(program_id)
        total = data['total']
        per_page = data['per_page']
        page_number = 0
        while page_number * per_page < total:
            page_number = page_number + 1
            if page_number > 1:
                data = self.get_job_group_list_one_page(program_id, page_number)
            job_group_list.extend(data['items'])
        return job_group_list

    def get_job_list_one_page(self, job_id, page=1):
        url = 'data/job/%s/tasks' % (job_id)
        data = self._get_url(url, page=page)
        return data

    def get_job_list(self, job_id):
        job_list = []
        data = self.get_job_list_one_page(job_id)
        total = data['total']
        per_page = data['per_page']
        page_number = 0
        while page_number * per_page < total:
            page_number = page_number + 1
            if page_number > 1:
                data = self.get_job_list_one_page(job_id, page_number)
            job_list.extend(data['items'])
        return job_list

    def remark_job(self, job_id, remark):
        url = 'data/job/%s/remark' % (job_id)
        data = self._post_url(url)
        return data

    def star_job(self, job_id, star=1):
        url = 'data/job/%s/star' % (job_id)
        data = {}
        data['star'] = star
        data = self._post_url(url, json_data=data)
        return data

    def list_program_one_page(self, page=1):
        url = 'account/programs'
        data = self._get_url(url, page=page)
        return data

    def list_program(self):
        data = self._get_url('/brm/v1/project/list')
        return data['items']

    def list_image(self, program_id=1, page=1):
        url = 'image/list'
        data = self._get_url(url, program_id=program_id, page=page)
        return data

    def _check_sdk_version(self):
        url = "data/check_sdk_version"
        data = self._get_url(url)
        version = data['version']
        if self.version != version:
            print("============== Current Version %s, New Version %s, Need Update! ==============" % (
                self.version, version))
