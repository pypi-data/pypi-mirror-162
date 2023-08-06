# -*- coding: utf-8 -*-
import argparse
import getpass
import json
import os
import time

from requests_toolbelt.multipart.encoder import reset

import lebesgue_sdk.lebesgue_sdk as lebesgue_sdk

CONFIG_FILE_LOCATION = os.path.join(os.path.expanduser('~'), ".lebesgue_config.json")


class cmd(object):

    def __init__(self, config=CONFIG_FILE_LOCATION):
        self.version = 1.0
        self.config = config
        self.get_config()
        self.check_username()
        self.dp = lebesgue_sdk.lebesgue_sdk(base_url=self.base_url,
                                            endpoint=self.endpoint,
                                            bucket=self.bucket)
        self.dp.login(self.username, self.password)
        # 登录成功 并且更新下数据
        if self.dp.username and self.config_json['password'] != self.password and self.config_json[
            'username'] != self.username:
            self.config_json['username'] = self.username
            self.config_json['password'] = self.password
            self.update_config()
        # 登录失败 返回并提醒
        if not self.dp.username:
            self._save_log(message='login failed')
            print("==================== Login failed. ====================")
            exit()
        # else:
        #    self._save_log(message='login success', username=self.username)

    def check_username(self):
        if self.username == '' and self.password == '':
            raise ValueError('can not find user information please check your config')

    # 获取 config 信息
    def get_config(self):
        self.config_json = json.loads(open(self.config).read())
        self.username = self.config_json['username']
        self.password = self.config_json['password']
        self.bucket = self.config_json['bucket']
        self.base_url = self.config_json['base_url']
        self.endpoint = self.config_json['endpoint']
        self.save_path = os.path.abspath(
            self.config_json.get('save_path', './result'))
        # os.makedirs(self.save_path, exist_ok=True)
        self.download_url = self.endpoint[:7] + self.bucket + \
                            "." + self.endpoint[7:].strip("/") + "/"
        self.append_job_name = self.config_json.get('append_job_name', False)
        self.log_file = os.path.join(self.save_path, 'result.log')

    # 检测是有用户名
    def update_config(self):
        w = open('./config.json', 'w')
        w.write(json.dumps(self.config_json, indent=2))
        w.close()

    # 获取任务情况
    def insert_job(self, **args):
        # 文件地址
        zip_path = args['zip_path']
        # 参数地址
        config_file_path = args['param_json']
        # 读取数据
        oss_path = self.dp.upload_job_data(
            job_type='indicate', zip_path=zip_path)
        config = json.loads(open(config_file_path).read())
        data = self.dp.insert_job(oss_path, **config)
        if data:
            print("Submit job succeed. JOB GROUP ID: %s, JOB ID: %s" % (data['job_group_id'], data['job_id']))
            self._save_log(message='submit job', job_group_id=data['job_group_id'], job_id=data['job_id'],
                           zip_path=zip_path, oss_path=oss_path)
        else:
            print("Submit job failed.")

    # 查看用户详情
    def get_summary(self, program_id):
        print(self.dp.get_summary(program_id))

    def get_job_group_list(self, program_id):
        for job_group_detail in self.dp.get_job_group_list(program_id):
            print(
                "ID: {:<10} | JOB_NAME: {:<20} | USER: {:<10} | JOB_TYPE: {:<10} | STATUS: {:<3} | CREATE_TIME: {:<10} | SPEND_TIME: {:<10} | COST:{:<5}".format(
                    job_group_detail['id'],
                    job_group_detail['job_name'],
                    job_group_detail['user_name'],
                    job_group_detail.get('job_type', ''),
                    job_group_detail['status'][0],
                    job_group_detail['create_time'],
                    job_group_detail['spend_time'],
                    job_group_detail['cost']
                ))

    def get_job_list(self, job_id):
        for job_detail in self.dp.get_job_list(job_id):
            print(
                "JOB_ID: {:<10} | SPEND_TIME: {:<10} | STATUS: {:<10} | RESULT: {:<10} | INPUT: {:<10} | COST:{:<5} | CREATE_TIME:{:<10} | UPDATE_TIME:{:<10}".format(
                    job_detail['task_id'],
                    job_detail['spend_time'],
                    job_detail['status'],
                    job_detail['result_url'],
                    job_detail['input_data'],
                    job_detail['cost'],
                    job_detail['create_time'],
                    job_detail['update_time']
                ))

    def get_job_detail(self, job_id):
        job_detail = self.dp.get_job_detail(job_id)
        print(
            "{:<15}{:<10}\n{:<15}{:<10}\n{:<15}{:<10}\n{:<15}{:<10}\n{:<15}{:<10}\n{:<15}{:<10}\n{:<15}{:<5}\n{:<15}{:<10}\n{:<15}{:<10}".format(
                "JOB_ID: ", job_detail['job_id'],
                "JOB_GROUP_ID: ", job_detail['job_group_id'],
                "STATUS: ", job_detail['status'],
                "SPEND_TIME: ", job_detail['spend_time'],
                "COST: ", job_detail['cost'],
                "CREATE_TIME: ", job_detail['create_time'],
                "UPATE_TIME: ", job_detail['update_time'],
                "INPUT: ", job_detail['input_data'],
                "RESULT: ", job_detail['result_url']
            ))

    def get_machine_type(self):
        for machine_type_detail in self.dp.get_machine_type():
            print(
                "MACHINE_TYPE: {:<25} | CPU_CORE: {:<4} | GPU: {:<16} | MEM(GB): {:<4} | PLATFORM: {:<3} | SPOT_PRICE(yuan/h): {:<5} | ON_DEMAND_PRICE(yuan/h): {:<5}".format(
                    machine_type_detail['scass_type'],
                    machine_type_detail['cpu'],
                    machine_type_detail['gpu'],
                    machine_type_detail['memory'],
                    machine_type_detail['platform'],
                    machine_type_detail['spot_standard_price'],
                    machine_type_detail['ondemand_standard_price']
                ))

    def list_program(self):
        print("======== Program List ========")
        for program_detail in self.dp.list_program():
            print(
                "Program ID: {:<10} | Program Name: {:<10} | Cost Limit: {:<4} | Total Cost: {:<4} | Cost Limit Type: {}".format(
                    program_detail['id'],
                    program_detail['name'],
                    program_detail['costLimit'] / 100,
                    program_detail['totalCost'] / 100,
                    "Total Budget" if program_detail.get("costLimitType") == 1 else "Monthly Budget"
                ))

    def list_image(self, program_id=1):
        data = self.dp.list_image(program_id)
        print("======== Image List ========")
        total = data['total']
        per_page = data['per_page']
        page_number = 0
        while page_number * per_page < total:
            page_number = page_number + 1
            if page_number > 1:
                data = self.dp.list_image(program_id, page_number)
            for image_detail in data['items']:
                print(
                    "Program Name: {:<10} | ID: {:<5} | Image Name: {:<30} | Status: {:<4} | Platform: {:<3} | Disk Size(GB): {:<5} | Comment: {:<20}".format(
                        image_detail['program_name'] or "None",
                        image_detail['image_id'] or "None",
                        image_detail['image_name'] or "None",
                        image_detail['status'] or "None",
                        image_detail['platform'] or "None",
                        image_detail['disk_size'] or "None",
                        image_detail['comment'] or "None"
                    ))

    def download_job_group_result(self, job_group_id):
        os.makedirs(self.save_path, exist_ok=True)
        if self.dp.download_job_group_result(
                self.save_path, job_group_id, append_job_name=self.append_job_name) != -1:
            print("Downloaded to %s/%s/" % (self.save_path, job_group_id))

    def download_job_result(self, job_id):
        job_group_id = self.dp.get_job_detail(job_id)['job_group_id']
        os.makedirs(self.save_path, exist_ok=True)
        if self.dp.download_job_result(
                self.save_path, job_id, append_job_name=self.append_job_name) != -1:
            print("Downloaded to %s/%s/%s/" % (self.save_path, job_group_id, job_id))

    def kill_job(self, job_id):
        data = self.dp.kill_job(job_id)
        print(data)

    def terminate_job(self, job_id):
        data = self.dp.terminate_job(job_id)
        print(data)

    def terminate_job_group(self, job_group_id):
        data = self.dp.terminate_job_group(job_group_id)
        print(data)

    def delete_job(self, job_id):
        data = self.dp.delete_job(job_id)
        print(data)

    def delete_job_group(self, job_group_id):
        data = self.dp.delete_job_group(job_group_id)

    # 保存提交任务的参数
    def _save_log(self, **kwargs):
        os.makedirs(self.save_path, exist_ok=True)
        with open(self.log_file, 'a') as w:
            tmp_time = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            tmp_data = str(kwargs).replace('\n', '')
            tmp_str = "%s, %s" % (tmp_time, tmp_data) + "\n"
            w.write(tmp_str)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    Ref: https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input/3041990
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = input(question + prompt + " :").lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("请输入 'yes' 或者 'no' " "(or 'y' or 'n').\n")


def ask_for(query, default=None, optional=False, secret=False):
    while True:
        question = None
        old_default = default
        if secret and default:
            if len(default) >= 4:
                default = '*' * (len(default) - 4) + default[-4:]
            else:
                default = '*' * len(default)
        if optional:
            question = f"{query} 当前为: [{default}]: "
        else:
            question = f"{query}: "
        result = None
        if secret:
            result = getpass.getpass(prompt=question)
        else:
            result = input(question)
        if not result and not optional:
            print("此为必填项")
            continue
        if result:
            return result
        if optional:
            return old_default


def generate_config_file():
    global CONFIG_FILE_LOCATION
    config = {}
    if os.path.exists(CONFIG_FILE_LOCATION):
        f = open(CONFIG_FILE_LOCATION, 'r')
        config = json.loads(f.read())
        f.close()
    config["base_url"] = ask_for('base_url', default=config.get('base_url', "https://bohrium.dp.tech/"), optional=True)
    config["endpoint"] = ask_for('endpoint', default=config.get('endpoint', "http://oss-cn-shenzhen.aliyuncs.com"),
                                 optional=True)
    config['bucket'] = ask_for('bucket', default=config.get('bucket', "dpcloudserver"), optional=True)
    config['username'] = ask_for('username or email', default=config.get('username'), optional=('username' in config))
    config['password'] = ask_for('password', default=config.get('password'), optional=('password' in config),
                                 secret=True)
    config['save_path'] = ask_for("save_path", default=config.get('save_path', 'result/'), optional=True)
    config['append_job_name'] = True
    j = json.dumps(config, indent=4)
    CONFIG_FILE_LOCATION = os.path.join(os.path.expanduser('~'), ".lebesgue_config.json")
    with open(CONFIG_FILE_LOCATION, "w") as f:
        f.write(j)
    print(f"配置文件保存成功, 保存路径为: {CONFIG_FILE_LOCATION}")
    return CONFIG_FILE_LOCATION


def main():
    # 检测用户名是否登录

    find_config = False
    CONFIG_FILE_LOCATION = ''
    # 检查当前文件
    abs_path = os.path.dirname(os.path.abspath(__file__))
    # os.chdir(abs_path)
    CONFIG_FILE_LOCATION = os.path.join(abs_path, "config.json")
    if os.path.exists(CONFIG_FILE_LOCATION):
        find_config = True

    # 检查当前工作目录
    if not find_config:
        CONFIG_FILE_LOCATION = os.path.join(os.getcwd(), "config.json")
        if os.path.exists(CONFIG_FILE_LOCATION):
            find_config = True

    # 检查家目录
    if not find_config:
        CONFIG_FILE_LOCATION = os.path.join(os.path.expanduser('~'), ".lebesgue_config.json")
        if os.path.exists(CONFIG_FILE_LOCATION):
            find_config = True

    if not find_config:
        if query_yes_no("未找到配置文件，是否配置?"):
            CONFIG_FILE_LOCATION = generate_config_file()
            print("配置完成, 重新运行以生效。")
            quit()
        else:
            print("Lebesgue Utility需要配置用户信息才能继续。")
            quit()
    # 初始化 cmd 并尝试登录
    tmp = cmd(config=CONFIG_FILE_LOCATION)

    # 进行参数解析 有一次性命令行模式 和 交互模式
    parser = argparse.ArgumentParser(description='Lebesgue Shell')
    parser.add_argument('-i', '--job_config_json', type=str, help='Config file path for job')
    parser.add_argument('-p', '--input_path', type=str, help='Directory for input files.')

    parser.add_argument('-pgid', '--program_id', type=int, help='Program ID')
    parser.add_argument('-jgid', '--job_group_id', type=int, help='Job Group ID')
    parser.add_argument('-jid', '--job_id', type=int, help='Job ID')
    parser.add_argument('-m', '--machine_type',
                        action='store_true', help='Get all machine types.')
    parser.add_argument('-im', '--image_list',
                        action='store_true', help='Get image list.')
    parser.add_argument('-d', '--details', action='store_true', help='Get details.')
    parser.add_argument('-del', '--delete', action='store_true', help='Delete resources.')
    parser.add_argument('-t', '--terminate', action='store_true', help='Terminate job or job group.')
    parser.add_argument('-k', '--kill', action='store_true', help='Kill job.')
    parser.add_argument('-D', '--download', action='store_true', help='Download results.')
    parser.add_argument('-c', '--config', action='store_true', help='Config Lebesgue user information.')
    args = parser.parse_args()
    args = vars(args)
    if args['details']:
        if args['program_id']:
            tmp.get_job_group_list(args['program_id'])
        elif args['job_group_id']:
            tmp.get_job_list(args['job_group_id'])
        elif args['job_id']:
            tmp.get_job_detail(args['job_id'])
        else:
            tmp.list_program()
    elif args['machine_type']:
        tmp.get_machine_type()
    elif args['image_list']:
        if args['program_id']:
            tmp.list_image(args['program_id'])
        else:
            print('Need Program ID')
    elif args['job_config_json']:
        input_json = args['job_config_json']
        path = args['input_path']
        if not path:
            print("Need job config file path.")
        else:
            tmp.insert_job(zip_path=path, param_json=input_json)
    elif args['kill']:
        if args['job_id']:
            tmp.kill_job(args['job_id'])
    elif args['terminate']:
        if args['job_group_id']:
            tmp.terminate_job_group(args['job_group_id'])
        elif args['job_id']:
            tmp.terminate_job(args['job_id'])
        else:
            print('Need job id or job group id.')
    elif args['delete']:
        if args['job_group_id']:
            tmp.delete_job_group(args['job_group_id'])
        else:
            print('Need job group id.')
    elif args['download']:
        if args['job_group_id']:
            tmp.download_job_group_result(args['job_group_id'])
        elif args['job_id']:
            tmp.download_job_result(args['job_id'])
        else:
            print('Need job ID.')
    elif args['config']:
        generate_config_file()
    else:
        print('Invalid Arguments.')
        parser.print_help()


if __name__ == '__main__':
    main()
