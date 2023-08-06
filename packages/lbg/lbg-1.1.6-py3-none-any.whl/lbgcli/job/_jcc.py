import readchar
from colorama import Fore
from datetime import datetime
from pathlib import PurePosixPath, Path
from shlex import split

ENABLE_READLINE = True
try:
    try:
        import readline
    except Exception:
        import pyreadline3 as readline
except Exception:
    ENABLE_READLINE = False


class JCCOperator:
    DEFAULT_BUFFER_SIZE = 2048

    def __init__(self, client, job_id):
        self.cli = client
        self.job_id = job_id
        self._wd = PurePosixPath("/")
        self._base_buf_size = self.DEFAULT_BUFFER_SIZE
        self.complete_options = []
        if ENABLE_READLINE:
            try:
                self._rl = readline.Readline()
                self._rl.prompt_color = readline.console.AnsiState(color='white')
                self._rl.prompt_color.trtable['lightmagenta'] = 269
                self._rl.prompt_color.color = 'lightmagenta'
            except AttributeError:
                self._rl = readline
            self._rl.allow_ctrl_c = True
            self._rl.parse_and_bind("tab: complete")

    def _completer(self, text, state):
        command = []
        try:
            command = split(text)
        except ValueError as e:
            self.cli.print(e)
        if len(command) == 0:
            return
        options = [cmd for cmd in self.complete_options if cmd.startswith(command[-1])]
        if state < len(options):
            return options[state]
        else:
            return None

    def _set_autocomplete(self):
        names = self._jcc_ls(only_result=True)
        if ENABLE_READLINE:
            self._rl.set_completer(self._completer)
        self.complete_options = names

    def _help_message(self):
        current_info = f'job id: {self.job_id}, buffer_size: {self._base_buf_size}'
        header_desc = f'{self._color_command("command_name | alias")} {self._color_arg("<required>")} {self._color_arg("[optional]")} : description'
        help_desc = f'{self._color_command("help | h")}: show help message'
        ls = f'{self._color_command("ls")} {self._color_arg("[path]")}: list current file in dir'
        ll = f'{self._color_command("ll | l")} {self._color_arg("[path]")}: list detail of current file in dir'
        cd = f'{self._color_command("cd")} {self._color_arg("<path>")}: change working dir'
        pwd = f'{self._color_command("pwd")}: print current working dir'
        read_option = "\t'n': read next\n" \
                      "\t'q': quite or Ctrl+C\n" \
                      "\t'[0-9]': read next with multiple amount"
        read = f'{self._color_command("read | r")} {self._color_arg("<path>")}: read file\n{read_option}'
        tail = f'{self._color_command("tail")} {self._color_arg("<path>")}: read file from last few byte'
        head = f'{self._color_command("head")} {self._color_arg("<path>")}: read file from first few byte'
        jump_read = f'{self._color_command("jumpread | jr")} {self._color_arg("<path>")} ' \
                    f'{self._color_arg("[start_position]")}: default:0.9'
        setbuf = f'{self._color_command("setbuf")} {self._color_arg("<buf_size>")}: set default buffer size, ' \
                 f'current: {self._base_buf_size}, 0 is set to default {self.DEFAULT_BUFFER_SIZE}'
        exit_desc = f'{self._color_command("exit | q")}: exit or Ctrl+D'
        return (
            '\n'.join(
                [current_info, header_desc, help_desc, setbuf, cd, pwd, ls, ll, read, head, tail, jump_read, exit_desc])
        )

    def _color_command(self, s):
        return Fore.GREEN + s + Fore.RESET

    def _color_dir(self, s):
        return Fore.LIGHTCYAN_EX + s + Fore.RESET

    def _color_pwd(self, s):
        return Fore.LIGHTMAGENTA_EX + s + Fore.RESET

    def _color_arg(self, s):
        return Fore.LIGHTYELLOW_EX + s + Fore.RESET

    def start(self):
        self._set_autocomplete()
        self.cli.print(self._help_message())
        while True:
            try:
                wd_str = str(self._wd)
                wd_str = self._color_pwd(wd_str)
                # self.cli.print(f"{wd_str} $: ", newline=False)
                try:
                    if ENABLE_READLINE:
                        try:
                            input_arg = self._rl.readline(f"{wd_str} : ")
                        except AttributeError:
                            input_arg = input(f"{wd_str} $: ")
                    else:
                        input_arg = input(f"{wd_str} $: ")
                    command = []
                except EOFError:
                    break
                try:
                    command = split(input_arg)
                except ValueError as e:
                    self.cli.print(e)
                if len(command) == 0:
                    continue
                if command[0] in ['help', 'h']:
                    self.cli.print(self._help_message())
                elif command[0] == 'ls':
                    if len(command) == 2:
                        self._jcc_ls(sub_path=command[1])
                    else:
                        self._jcc_ls()
                elif command[0] in ['ll', 'l']:
                    if len(command) == 2:
                        self._jcc_ll(sub_path=command[1])
                    else:
                        self._jcc_ll()
                elif command[0] == 'pwd':
                    self.cli.print(self._wd)
                elif command[0] == 'tail':
                    if len(command) == 1:
                        self.cli.print('missing path')
                        continue
                    read_path = str(self._wd.joinpath(command[1]))
                    self._jcc_tail(read_path)
                elif command[0] == 'head':
                    if len(command) == 1:
                        self.cli.print('missing path')
                        continue
                    read_path = str(self._wd.joinpath(command[1]))
                    self._jcc_head(read_path)
                elif command[0] == 'cd':
                    if len(command) == 1:
                        self.cli.print('missing path')
                        continue
                    if command[1] == '~':
                        command[1] = '/'
                    new_path = self._jcc_cd(command[1])
                    if new_path is not None:
                        self._wd = new_path
                        self._set_autocomplete()
                elif command[0] in ['exit', 'q']:
                    break
                elif command[0] in ['jr', 'jumpread']:
                    position = 0.9
                    if len(command) <= 1:
                        self.cli.print('missing path and amount')
                        continue
                    read_path = str(self._wd.joinpath(command[1]))
                    if len(command) == 2:
                        self._jcc_jr(read_path, position=position)
                    if len(command) == 3:
                        position = float(command[2])
                        self._jcc_jr(read_path, position=position)
                elif command[0] == 'setbuf':
                    if len(command) == 1:
                        self.cli.print('missing buffer size')
                        continue
                    self._jcc_set_buf(int(command[1]))
                elif command[0] in ['read', 'cat', 'r']:
                    if len(command) == 1:
                        self.cli.print('missing path')
                        continue
                    read_path = str(self._wd.joinpath(command[1]))
                    self._read_file(read_path)
                else:
                    self.cli.print(f'unknown command: {command[0]}')
            except KeyboardInterrupt as e:
                self.cli.print()
            # except EOFError as e:
            #     self.cli.print()

    def _jcc_set_buf(self, number):
        if number == 0:
            number = self.DEFAULT_BUFFER_SIZE
        if not self._check_buf_size(number):
            return
        self._base_buf_size = number
        self.cli.print(f'buffer size set to: {number}')

    def _check_buf_size(self, number):
        if number < 0 or number > 51200:
            self.cli.print(f'invalid buffer size: {number}, must between 0 to 51200')
            return False
        return True

    def _jcc_tail(self, file_path, tail_size=None):
        if tail_size is None:
            tail_size = self._base_buf_size
        if not self._check_buf_size(tail_size):
            return None
        state = self.cli.client.job.view_state(self.job_id, str(file_path))
        if len(state) == 0:
            self.cli.print(f'{file_path} does not exist')
            return None
        if state['is_dir']:
            self.cli.print(f'{file_path} is dir')
            return None
        size = state['size']
        start_byte = size - tail_size
        if start_byte < 0:
            start_byte = 0
        data = self.cli.client.job.view_read(self.job_id, file_path, start_byte=start_byte,
                                             buf_size=tail_size)
        content = data['data']
        self.cli.print(content)

    def _jcc_head(self, file_path, buf_size=None):
        if buf_size is None:
            buf_size = self._base_buf_size
        if not self._check_buf_size(buf_size):
            return None
        state = self.cli.client.job.view_state(self.job_id, str(file_path))
        if len(state) == 0:
            self.cli.print(f'{file_path} does not exist')
            return None
        if state['is_dir']:
            self.cli.print(f'{file_path} is dir')
            return None
        size = state['size']
        start_byte = 0
        if start_byte < 0:
            start_byte = 0
        data = self.cli.client.job.view_read(self.job_id, file_path, start_byte=start_byte,
                                             buf_size=buf_size)
        content = data['data']
        self.cli.print(content)

    def _check_if_dir(self, path):
        state = self.cli.client.job.view_state(self.job_id, str(path))
        if len(state) == 0:
            self.cli.print(f'{path} does not exist')
            return False
        if not state['is_dir']:
            self.cli.print(f'{path} is not dir')
            return False
        return True

    def _jcc_jr(self, file_path, position=0.9):
        if position < 0 or position > 1:
            self.cli.print(f'position {position} invalid, support position between 0 to 1.')
        state = self.cli.client.job.view_state(self.job_id, str(file_path))
        if len(state) == 0:
            self.cli.print(f'{file_path} does not exist')
            return None
        if state['is_dir']:
            self.cli.print(f'{file_path} is dir')
            return None
        size = state['size']
        start_byte = int(size * position)
        if start_byte < 0:
            start_byte = 0
        self._read_file(file_path, start_byte=start_byte)

    def _jcc_ls(self, sub_path=None, only_result=False):
        cwd = self._wd
        if sub_path:
            cwd = self._jcc_cd(sub_path)
            if not cwd:
                return None
        result = self.cli.client.job.view_ls(self.job_id, str(cwd))
        result = self._sort_ls_result(result)
        value = []
        value_dir = []
        for each in result:
            if each['is_dir'] and not only_result:
                value_dir.append(self._color_dir(each['name']))
            else:
                value.append(each['name'])
        value_dir.extend(value)
        if not only_result:
            self.cli.print('\t'.join(value_dir))
        return value_dir

    def _sort_ls_result(self, data, sort_by='name', reverse=False):
        return sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    def _jcc_cd(self, new_path):
        cwd = self._wd
        wd_to_be_check = cwd.joinpath(new_path)
        wd_conv = self._to_path_str(wd_to_be_check)
        state = self.cli.client.job.view_state(self.job_id, str(wd_conv))
        if len(state) == 0:
            self.cli.print(f'{wd_to_be_check} does not exist')
            return None
        if not state.get('is_dir'):
            self.cli.print(f'{wd_to_be_check} is file not dir')
            return None
        return wd_conv

    def _jcc_ll(self, sub_path=None):
        cwd = self._wd
        if sub_path:
            new_path = self._jcc_cd(sub_path)
            if not new_path:
                return
            cwd = new_path
        result = self.cli.client.job.view_ls(self.job_id, str(cwd))

        def map_func(v):
            time = datetime.fromtimestamp(v['modify_date']).strftime("%b %d %H:%M")
            v['modify_date_desc'] = time
            v['size_desc'] = self._sizeof_fmt(v['size'])
            if v['is_dir']:
                v['name'] = self._color_dir(v['name'])
            return v

        left_item = list(map(map_func, result))
        left_item = self._sort_ls_result(left_item)
        value_dir = []
        value = []
        for each in left_item:
            if each['is_dir']:
                value_dir.append(each)
            else:
                value.append(each)
        value_dir.extend(value)
        for each in value_dir:
            self.cli.print(
                "{:<10} {:<10} {:<10} {}".format(
                    each['mode'],
                    each['size_desc'],
                    each['modify_date_desc'],
                    each['name']
                ))

    def _to_path_str(self, wd):
        wd_to_be_check = PurePosixPath(Path(wd).resolve())
        wd_to_be_check_str = str(wd_to_be_check)
        if str(wd_to_be_check).startswith('C:\\'):
            wd_to_be_check_str = str(wd_to_be_check)[len('C:\\'):]
        if not wd_to_be_check_str.startswith('/'):
            wd_to_be_check_str += '/'
        wd_to_be_check = PurePosixPath(wd_to_be_check_str)
        return wd_to_be_check

    def _read_file(self, file_path, base_buf_size=None, start_byte=0):
        if base_buf_size is None:
            base_buf_size = self._base_buf_size
        if not self._check_buf_size(base_buf_size):
            return None
        start_byte = start_byte
        state = self.cli.client.job.view_state(self.job_id, str(file_path))
        if len(state) == 0:
            self.cli.print(f'{file_path} does not exist')
            return None
        if state['is_dir']:
            self.cli.print(f'{file_path} is dir')
            return None
        multiply = 1
        while True:
            state = self.cli.client.job.view_state(self.job_id, file_path)
            if len(state) == 0:
                self.cli.print(f'no such file, {file_path}')
                return
            if state['size'] <= start_byte:
                break
            data = self.cli.client.job.view_read(self.job_id, file_path, start_byte=start_byte,
                                                 buf_size=base_buf_size * multiply)
            content = data['data']
            self.cli.print(content, newline=False)
            start_byte = data['next_location']
            if state['size'] <= start_byte:
                break
            multiply = 1
            while True:
                c = readchar.readchar()
                if not isinstance(c, str):
                    c = c.decode()
                if c == readchar.key.CTRL_C:
                    self.cli.print()
                    return
                if str(c) == 'n':
                    break
                elif str(c) == 'q':
                    self.cli.print()
                    return
                elif c.isnumeric():
                    if int(c) == 0:
                        multiply = 10
                        break
                    multiply = int(c)
                    break

    def _sizeof_fmt(self, num, suffix="b"):
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"
