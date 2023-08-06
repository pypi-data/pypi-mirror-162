import argparse
import csv
import json
import os
import sys
import traceback
from datetime import datetime

import requests
from colorama import init, Fore
from packaging import version

import lbgcli.meta
from lbgcli.config.config import ConfigModule
from lbgcli.const import ConfigKey, GlobalConfig
from lbgcli.history.history import HistoryModule
from lbgcli.image.image import ImageModule
from lbgcli.job.job import JobModule
from lbgcli.job_group.job_group import JobGroupModule
from lbgcli.machine.machine import MachineModule
from lbgcli.module_impl import TolerantException
from lbgcli.node.node import NodeModule
from lbgcli.program.program import ProgramModule
from lbgcore.client import Client, RequestInfoException

init()


class LebesgueCLI:
    LBG_CLI_CTX_DIR_LOCATION = os.environ.get(ConfigKey.CONFIG_FILE_DIR, GlobalConfig.CONFIG_FILE_DIR)

    def __init__(self, writer=sys.stdout):
        self.config: dict = {}

        class ModuleCall:
            pass

        self.module = ModuleCall()
        self._client = None
        self.load_cli_context()
        self.parser = self.init_parser()
        self.writer = writer
        self.check_version()

    def print(self, *value, newline=True):
        if len(value) == 0 and newline:
            self.writer.write('\n')
            return
        for each in value:
            if newline:
                values = str(each).splitlines()
            else:
                values = ''.join(value)
            for v in values:
                if newline:
                    self.writer.write(v + '\n')
                else:
                    self.writer.write(v)

    def log(self, module, function, meta):
        ctx_dir_location = os.path.expanduser(self.LBG_CLI_CTX_DIR_LOCATION)
        path = os.path.join(ctx_dir_location, GlobalConfig.CONFIG_ACTION_RECORD)
        with open(path, 'a', newline='') as f:
            now = datetime.now()
            date_time = now.isoformat()
            writer = csv.writer(f)
            writer.writerow([date_time, module, function, json.dumps(meta)])

    def init_parser(self):
        main_parser = argparse.ArgumentParser(description='Lebesgue Cli',
                                              formatter_class=argparse.RawDescriptionHelpFormatter)
        main_parser.add_argument("-v", "--version", action='version', version=lbgcli.meta.version)
        sub_parser = main_parser.add_subparsers()

        server_module = NodeModule(self)
        setattr(self.module, 'node', server_module)
        server_module.add_to_parser(sub_parser)

        program_module = ProgramModule(self, 'program')
        setattr(self.module, 'program', program_module)
        program_module.add_to_parser(sub_parser)

        project_module = ProgramModule(self, 'project')
        setattr(self.module, 'project', project_module)
        project_module.add_to_parser(sub_parser)

        image_module = ImageModule(self)
        setattr(self.module, 'image', image_module)
        image_module.add_to_parser(sub_parser)

        config_module = ConfigModule(self)
        setattr(self.module, 'config', config_module)
        config_module.add_to_parser(sub_parser)

        jobgroup_module = JobGroupModule(self)
        setattr(self.module, 'job_group', jobgroup_module)
        jobgroup_module.add_to_parser(sub_parser)

        job_module = JobModule(self)
        setattr(self.module, 'job', job_module)
        job_module.add_to_parser(sub_parser)

        history_module = HistoryModule(self)
        setattr(self.module, 'history_module', history_module)
        history_module.add_to_parser(sub_parser)

        machine_module = MachineModule(self)
        setattr(self.module, 'machine_module', machine_module)
        machine_module.add_to_parser(sub_parser)
        return main_parser

    def load_cli_context(self):
        ctx_dir_location = os.path.expanduser(self.LBG_CLI_CTX_DIR_LOCATION)
        if not os.path.exists(ctx_dir_location):
            os.makedirs(ctx_dir_location, exist_ok=True)
        ctx_location = os.path.join(ctx_dir_location, GlobalConfig.CONFIG_FILE_NAME)
        try:
            if os.path.exists(ctx_location):
                with open(ctx_location, 'r') as f:
                    file_data = json.loads(f.read())
                    self.config = file_data
            else:
                with open(ctx_location, 'w') as f:
                    f.write("{}")
        except Exception as e:
            self.print(e)
            self.print("config file reset.")
            with open(ctx_location, 'w') as f:
                f.write("{}")

    def save_cli_context(self):
        ctx_dir_location = os.path.expanduser(self.LBG_CLI_CTX_DIR_LOCATION)
        if not os.path.exists(ctx_dir_location):
            os.makedirs(ctx_dir_location, exist_ok=True)
        ctx_location = os.path.join(ctx_dir_location, GlobalConfig.CONFIG_FILE_NAME)
        try:
            if os.path.exists(ctx_location):
                with open(ctx_location, 'w+') as f:
                    f.write(json.dumps(self.config, indent=4))
        except Exception as e:
            self.print(e)

    def parse(self, *args):
        arg = self.parser.parse_args(*args)
        if 'func' not in arg:
            self.parser.print_help()
        else:
            try:
                arg.func(arg)
            except (TolerantException, RequestInfoException) as e:
                # traceback.print_exc()
                self.print(e)
            except Exception as e:
                traceback.print_exc()
                self.print(e)
        self.save_cli_context()

    @property
    def client(self):
        if self._client is not None:
            return self._client
        account = self.get_account_info()
        if not (account.get('email') and account.get('password')):
            raise TolerantException(
                f"you haven't config your account yet, configure by '{GlobalConfig.CALLER_NAME} config account'.")
        client = Client(**self.get_account_info(),
                        base_url=self.config.get(ConfigKey.LEBESGUE_ADDRESS, GlobalConfig.LEBESGUE_ADDRESS))
        self._client = client
        return client

    def get(self, key, *arg):
        if arg is not None and arg:
            return self.config.get(key, arg[0])
        return self.config.get(key)

    def has(self, key):
        return key in self.config

    def put(self, key, value):
        self.config[key] = value

    def delete(self, key):
        if key in self.config:
            del self.config[key]

    def program_id(self):
        if ConfigKey.CURRENT_PROGRAM_ID in self.config:
            return self.config[ConfigKey.CURRENT_PROGRAM_ID]
        raise TolerantException(
            f"can not find current project id, run '{GlobalConfig.CALLER_NAME} project switch -h' for more information")

    def output_format(self):
        return self.config.get(ConfigKey.DEFAULT_OUTPUT_FORMAT, 'table')

    def get_account_info(self):
        return {
            "email": self.config.get(ConfigKey.ACCOUNT_EMAIL),
            "password": self.config.get(ConfigKey.ACCOUNT_PASSWORD),
        }

    def check_account(self):
        account = self.get_account_info()
        if not account.get('email') or account.get('password'):
            raise TolerantException(
                f"Account information not configure yet, type '{GlobalConfig.CALLER_NAME} config account' to config your account")

    def save_account_info(self, email, password):
        if self.get(ConfigKey.ACCOUNT_EMAIL) != email:
            self.delete(ConfigKey.CURRENT_PROGRAM_ID)
        self.put(ConfigKey.ACCOUNT_EMAIL, email)
        self.put(ConfigKey.ACCOUNT_PASSWORD, password)

    def storage_endpoint(self):
        return self.config.get(ConfigKey.ALI_OSS_ENDPOINT, GlobalConfig.STORAGE_ENDPOINT)

    def check_version(self):
        level = self.get(ConfigKey.CHECK_VERSION_LEVEL, GlobalConfig.CHECK_VERSION_LEVEL)
        if level == -1:
            return
        try:
            resp = requests.get("https://pypi.tuna.tsinghua.edu.cn/pypi/lbg/json", timeout=3)
            latest_version = resp.json()["info"]["version"]
            current_strict = version.Version(lbgcli.meta.version)
            latest_strict = version.Version(latest_version)
            if current_strict < latest_strict:
                warn = f"{Fore.YELLOW}warning: version is out of date. current:{current_strict} latest:{latest_strict}."
                warn += f" To update run: '{Fore.GREEN}pip install -U lbg{Fore.RESET}{Fore.YELLOW}'. To ignore this warning run '{Fore.GREEN}lbg config version -h{Fore.RESET}{Fore.YELLOW}' for more information{Fore.RESET}"
                if current_strict.major < latest_strict.major and level <= 0:
                    self.print(warn)
                    return
                if current_strict.minor < latest_strict.minor and level <= 1:
                    self.print(warn)
                    return
                if current_strict.micro < latest_strict.micro and level <= 2:
                    self.print(warn)
                    return
        except Exception as e:
            # traceback.print_exc()
            pass


def main():
    cli = LebesgueCLI()
    cli.parse()


if __name__ == '__main__':
    cli = LebesgueCLI()
    cli.parse(["job","submit","-i","param.json","-p","fccSi"])
