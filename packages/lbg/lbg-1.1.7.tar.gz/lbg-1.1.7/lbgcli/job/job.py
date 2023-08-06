import json
import os
import traceback
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

import oss2
import yaml
from oss2 import determine_part_size, SizedFileAdapter
from oss2.models import PartInfo
from tqdm import tqdm

from lbgcli.const import GlobalConfig
from lbgcli.job._jcc import JCCOperator
from lbgcli.module_impl import Module, append_format_to_parser, TableResult, TolerantException
from lbgcli.util import query_yes_no, zip_dir, download, download_head


class JobModule(Module):

    def __init__(self, cli):
        super().__init__(cli)

    def add_to_parser(self, subparser):
        self.parser = subparser.add_parser('job', help='Operating Job Module')
        self.parser.set_defaults(func=lambda _: self.parser.print_help())
        self.sub_parser = self.parser.add_subparsers()
        self.load_ls()
        self.load_delete()
        self.load_kill()
        self.load_terminate()
        self.load_log()
        self.load_submit()
        self.load_download()
        self.load_describe()
        self.load_jcc()
        self.load_resubmit()

    def load_ls(self):
        parser_ls = self.sub_parser.add_parser('ls', help='list all job')
        parser_ls.set_defaults(func=lambda args: self.func_ls(args))
        parser_ls.add_argument('-i', '--index', action='store', type=int, default=0,
                               help='index of job group, default is 0, which use id of job group in rank n, disable if job group id is specified')
        parser_ls.add_argument('-jg', '--job_group_id', action='store', type=int, help='job group id')
        parser_ls.add_argument('-fa', '--fail', action='store_const', const=-1, help='only show failed job')
        parser_ls.add_argument('-pe', '--pending', action='store_const', const=0, help='only show pending job')
        parser_ls.add_argument('-ru', '--running', action='store_const', const=1, help='only show running job')
        parser_ls.add_argument('-fi', '--finished', action='store_const', const=2, help='only show finished job')
        parser_ls.add_argument('-sc', '--scheduling', action='store_const', const=3, help='only show scheduling job')
        parser_ls.add_argument('-st', '--stopping', action='store_const', const=4, help='only show stopping job')
        parser_ls.add_argument('-sp', '--stopped', action='store_const', const=5, help='only show stopped job')
        parser_ls.add_argument('-q', '--quiet', action='store_true', help='only show job id')
        append_format_to_parser(parser_ls)
        parser_ls.add_argument('-n', '--number', action='store', type=int, default=-1,
                               help='number of result to be display, default all')

    def func_ls(self, args):
        jgid = 0
        if args.job_group_id:
            jgid = args.job_group_id
        else:
            jg_list = self.cli.client.job_group.list_job_group_by_number(self.cli.program_id(), args.index + 1)
            if len(jg_list) == 0:
                raise TolerantException('no job group.')
            if len(jg_list) < args.index + 1:
                jgid = jg_list[-1]['id']
            else:
                jgid = jg_list[args.index]['id']
        status = []
        if args.fail:
            status.append(args.fail)
        if args.pending:
            status.append(args.pending)
        if args.running:
            status.append(args.running)
        if args.finished:
            status.append(args.finished)
        if args.scheduling:
            status.append(args.scheduling)
        if args.stopping:
            status.append(args.stopping)
        if args.stopped:
            status.append(args.stopped)
        result = self.cli.client.job.list_by_number(jgid, args.number, status=status)
        tr = TableResult(result, first_col='taskId',
                         no_header=args.noheader, default_format=self.cli.output_format())
        if args.quiet:
            for each in tr.data:
                self.cli.print(each['taskId'])
            return
        result = tr.output(args)
        self.cli.print(result)

    def load_delete(self):
        parser_tm = self.sub_parser.add_parser('rm', help='delete selected job')
        parser_tm.set_defaults(func=lambda args: self.func_delete(args))
        parser_tm.add_argument('job_ids', nargs='+', type=int, help='id of the job')
        parser_tm.add_argument('-f', '--force', action='store_true', help='force delete job')

    def func_delete(self, args):
        job_ids = args.job_ids
        force = args.force
        for each in job_ids:
            if not force:
                if not query_yes_no(f'do you want to delete this job with id: {each}', default='no'):
                    continue
            result = self.cli.client.job.delete(each)
            if result == {}:
                self.cli.print(f'successfully delete job with id: {each}')

    def load_terminate(self):
        parser_tm = self.sub_parser.add_parser('terminate', help='terminate selected job')
        parser_tm.set_defaults(func=lambda args: self.func_terminate(args))
        parser_tm.add_argument('job_id', nargs='+', type=int, help='id of the job')
        parser_tm.add_argument('-f', '--force', action='store_true', help='force terminate job')

    def func_terminate(self, args):
        job_ids = args.job_id
        force = args.force
        for each in job_ids:
            if not force:
                if not query_yes_no(f'do you want to terminate this job with id: {each}', default='no'):
                    continue
            result = self.cli.client.job.terminate(each)
            if result == {}:
                self.cli.print(f'successfully terminate job with id: {each}')

    def load_kill(self):
        parser_tm = self.sub_parser.add_parser('kill', help='kill selected job')
        parser_tm.set_defaults(func=lambda args: self.func_kill(args))
        parser_tm.add_argument('job_ids', nargs='+', type=int, help='id of the job')
        parser_tm.add_argument('-f', '--force', action='store_true', help='force kill job')

    def func_kill(self, args):
        job_ids = args.job_ids
        force = args.force
        for each in job_ids:
            if not force:
                if not query_yes_no(f'do you want to kill this job with id: {each}', default='no'):
                    continue
            result = self.cli.client.job.kill(each)
            if result == {}:
                self.cli.print(f'successfully kill job with id: {each}')

    def load_log(self):
        parser_tm = self.sub_parser.add_parser('log', help='show selected job log')
        parser_tm.set_defaults(func=lambda args: self.func_log(args))
        # parser_tm.add_argument('-j', '--json', action='store_true', help='show json format')
        parser_tm.add_argument('job_ids', nargs='+', type=int, help='id of the job')

    def func_log(self, args):
        job_ids = args.job_ids
        for each in job_ids:
            result = self.cli.client.job.log(each)
            log = ''
            try:
                if 'log' not in result:
                    log = f"job: {each} does not have log yet."
                else:
                    try:
                        log = json.loads(result.get('log')).get('log')
                        if isinstance(log, list):
                            log = '\n'.join(log)
                    except:
                        log = result.get('log')
                    # if args.json:
                    #     log = json.dumps(j, indent=4)
                    # else:
                    #     md = j.get('modify_date', 'None')
                    #     time = datetime.fromtimestamp(md)
                    #     t = j.get('stage', 'None')
                    #     logs = j.get('log', 'None')
                    #     nl = '\n'
                    #     log = f"type: {t}   modify_date: {time}\n{nl.join(logs)}"
            except Exception as e:
                traceback.print_exc()
            self.cli.print(log)

    def load_submit(self):
        parser_tm = self.sub_parser.add_parser('submit', help='submit job')
        parser_tm.set_defaults(func=lambda args: self.func_submit(args))
        parser_tm.add_argument('-i', '--file', action='store', help='predefined file')
        parser_tm.add_argument('-p', '--input', action='store', help='input file location')
        parser_tm.add_argument('-jt', '--job_type', action='store', help='indicate/container')
        parser_tm.add_argument('-jgid', '--job_group_id', action='store', type=int, help='job group id')
        parser_tm.add_argument('-pjid', '--project_id', action='store', type=int,
                               help='project id, will overwrite default')
        parser_tm.add_argument('-n', '--job_name', action='store', help='name')
        parser_tm.add_argument('-im', '--image_name', action='store', help='image name')
        parser_tm.add_argument('-ds', '--disk_size', action='store', help='disk size (GB)')
        parser_tm.add_argument('-sc', '--scass_type', action='store', help='scass type')
        parser_tm.add_argument('-mt', '--machine_type', action='store', help='machine type')
        parser_tm.add_argument('-nn', '--nnode', action='store', type=int, help='nnode')
        parser_tm.add_argument('-igid', '--instance_group_id', action='store', type=int, help='instance group id')
        parser_tm.add_argument('-c', '--cmd', action='store', help='command')
        parser_tm.add_argument('-l', '--log_file', action='store', help='log file location')
        parser_tm.add_argument('-o', '--out_files', action='store', help='log file location', nargs='?')
        parser_tm.add_argument('-pf', '--platform', action='store', help='ali/sugon')
        parser_tm.add_argument('-r', '--region', action='store', help='region name')
        parser_tm.add_argument('-odm', '--on_demand', action='store', type=int, help='0:spot(default) 1:on_demand ')
        parser_tm.add_argument('-ckptt', '--checkpoint_time', action='store', type=int, help='checkpoint time (minute)')
        parser_tm.add_argument('-ckptf', '--checkpoint_files', action='store', help='checkpoint file', nargs='?')
        parser_tm.add_argument('-dpb', '--disable_progress', action='store_true', help='disable progress bar')
        parser_tm.add_argument('-oji', '--only_job_id', action='store_true', help='only show job id')
        parser_tm.add_argument('-ojgi', '--only_job_group_id', action='store_true', help='only show job id')

    def func_submit(self, args):
        data = {}
        if args.file:
            p = Path(args.file)
            d = {}
            if p.suffix == '.json':
                d = json.loads(p.read_text())
            elif p.suffix == '.yaml' or p.suffix == '.yml':
                d = yaml.safe_load(p.read_text())
            else:
                raise ValueError('unsupported file formate, current support are json yaml yml.')
            for k, v in d.items():
                if k == "backward_files":
                    data["out_files"] = v
                else:
                    data[k] = v
        if args.job_type:
            data['job_type'] = args.job_type
        else:
            if 'job_type' not in data:
                data['job_type'] = 'indicate'
        if args.job_group_id:
            data['job_group_id'] = args.job_group_id
        if args.project_id:
            data['project_id'] = args.project_id
        else:
            if 'project_id' not in data:
                if 'program_id' in data:
                    data['project_id'] = data['program_id']
                else:
                    data['project_id'] = self.cli.program_id()
        if args.job_name:
            data['job_name'] = args.job_name
        if args.image_name:
            data['image_name'] = args.image_name
        if args.disk_size:
            data['disk_size'] = args.disk_size
        if 'machine_type' in data:
            data['scass_type'] = data['machine_type']
        if args.scass_type:
            data['scass_type'] = args.scass_type
        if args.machine_type:
            data['scass_type'] = args.machine_type
        if args.nnode:
            data['nnode'] = args.nnode
        if args.instance_group_id:
            data['instance_group_id'] = args.instance_group_id
        if args.cmd:
            data['cmd'] = args.cmd
        else:
            if 'command' in data:
                data['cmd'] = data['command']
        if args.log_file:
            data['log_file'] = args.log_file
        if args.out_files:
            data['out_files'] = args.out_files
        if args.platform:
            data['platform'] = args.platform
        if args.region:
            data['region'] = args.region
        if args.on_demand:
            data['on_demand'] = args.on_demand
        if args.checkpoint_time:
            data['checkpoint_time'] = args.checkpoint_time
        if args.checkpoint_files:
            data['checkpoint_files'] = args.checkpoint_files
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                raise ValueError(f'input path does not exist: {input_path}')
            oss_path = self._upload_job_data(
                job_type='indicate', zip_path=input_path, disable_progress=args.disable_progress)
            data['oss_path'] = oss_path
        else:
            raise ValueError('missing input file')
        if 'job_group_id' in data and not isinstance(data['job_group_id'], int):
            if isinstance(data['job_group_id'], str):
                try:
                    data['job_group_id'] = int(data['job_group_id'])
                except:
                    data['job_group_id'] = 0
            else:
                data['job_group_id'] = 0
        result = self.cli.client.job.insert(**data)
        if args.only_job_id:
            self.cli.print(result['jobId'])
            return
        if args.only_job_group_id:
            self.cli.print(result['jobGroupId'])
            return
        self.cli.print("Submit job succeed. JOB GROUP ID: %s, JOB ID: %s" % (result['jobGroupId'], result['jobId']))
        self.cli.log("job", "submit",
                     {'jobGroupId': result['jobGroupId'], 'jobId': result['jobId'],
                      'submitLocation': os.path.abspath(input_path)})

    def _upload_job_data(self, job_type, zip_path, **kwargs):
        task_uuid = uuid.uuid1().hex
        save_files = []
        zip_path = os.path.abspath(zip_path)
        if zip_path[-1] == '/' or zip_path[-1] == '\\':
            zip_path = zip_path[:-1]
        zip_task_file = zip_path + '.zip'
        zip_dir(zip_path, zip_task_file, save_files)
        self.cli.print("Zip File Success!")
        self.cli.print("Uploading")
        oss_task_dir = f'dpcloudserver/{job_type}/{task_uuid}/{task_uuid}.zip'
        self._upload_file_to_oss(oss_task_dir, zip_task_file, **kwargs)
        oss_task_dir = urllib.parse.urljoin('https://dpcloudserver.' + self.cli.storage_endpoint(), oss_task_dir)
        self.cli.print("Uploaded")
        os.remove(zip_task_file)
        return oss_task_dir

    def _upload_file_to_oss(self, oss_task_dir, zip_task_file, **kwargs):
        bucket = self._get_oss_bucket()
        total_size = os.path.getsize(zip_task_file)
        part_size = determine_part_size(total_size, preferred_size=1000 * 1024)
        upload_id = bucket.init_multipart_upload(oss_task_dir).upload_id
        parts = []
        with open(zip_task_file, 'rb') as fileobj:
            bar_format = "{l_bar}{bar}| {n:.02f}/{total:.02f} %  [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
            pbar = tqdm(total=100, desc="Uploading to oss", smoothing=0.01, bar_format=bar_format,
                        disable=kwargs.get('disable_progress'))
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                percent = num_to_upload * 100 / (total_size + 1)
                result = bucket.upload_part(
                    oss_task_dir, upload_id, part_number, SizedFileAdapter(fileobj, num_to_upload))
                parts.append(PartInfo(part_number, result.etag))
                offset += num_to_upload
                part_number += 1
                pbar.update(percent)
            pbar.close()
        bucket.complete_multipart_upload(oss_task_dir, upload_id, parts)

    def _get_oss_bucket(self):
        data = self.cli.client.job.get_sts()
        auth = oss2.StsAuth(data['AccessKeyId'], data['AccessKeySecret'], data['SecurityToken'])
        bucket = oss2.Bucket(auth, self.cli.storage_endpoint(), GlobalConfig.STORAGE_BUCKET_NAME)
        return bucket

    def load_download(self):
        parser_tm = self.sub_parser.add_parser('download', help='download selected job')
        parser_tm.set_defaults(func=lambda args: self.func_download(args))
        parser_tm.add_argument('job_ids', nargs='+', type=int, help='id of the job')
        parser_tm.add_argument('-p', '--path', action='store', help='download location default current dir')
        parser_tm.add_argument('-pr', '--parent', action='store_true', help='create parent dir if needed')

    def func_download(self, args, tolerate=False):
        job_ids = args.job_ids
        if args.path:
            target = args.path
        else:
            target = os.getcwd()
        bar_format = "{l_bar}{bar}| {n:.02f}/{total:.02f} %  [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        parent_bar = tqdm(job_ids, desc="Downloading Job", bar_format=bar_format)
        download_paths = []
        for each in job_ids:
            parent_bar.set_description("Downloading Job " + str(each))
            result = self.cli.client.job.detail(each)
            if result.get('resultUrl') and download_head(result.get('resultUrl')):
                p = Path(target)
                result_path = Path(result.get('result'))
                if not p.exists():
                    if args.parent:
                        p.mkdir(exist_ok=True, parents=True)
                    else:
                        p.mkdir(exist_ok=True)
                target_path = Path(target).joinpath(str(result['id']))
                download(result.get('resultUrl'), target_path, suffix=result_path.suffix)
                download_paths.append((result["id"], target_path.absolute()))
            else:
                self.cli.print(f'job id: {result["id"]} does not have result yet.')
            parent_bar.update(1)
        parent_bar.close()
        for (k, v) in download_paths:
            self.cli.print(f'job {k} download to {v}')

    def load_describe(self):
        parser_ls = self.sub_parser.add_parser('describe', help='describe job')
        parser_ls.set_defaults(func=lambda args: self.func_describe(args))
        parser_ls.add_argument('job_id', nargs='+', type=int, help='id of the job')
        append_format_to_parser(parser_ls)

    def func_describe(self, args):
        jobs = []
        for each in args.job_id:
            result = self.cli.client.job.detail(each)
            jobs.append(result)
        tr = TableResult(jobs, first_col='id',
                         no_header=args.noheader, default_format=self.cli.output_format())
        result = tr.output(args)
        self.cli.print(result)

    def load_jcc(self):
        parser_ls = self.sub_parser.add_parser('view', help='view job file')
        parser_ls.set_defaults(func=lambda args: self.func_jcc(args))
        parser_ls.add_argument('job_id', type=int, help='id of the job')

    def func_jcc(self, args):
        JCCOperator(self.cli, args.job_id).start()

    def load_resubmit(self):
        parser_tm = self.sub_parser.add_parser('resubmit', help='resubmit selected job')
        parser_tm.set_defaults(func=lambda args: self.func_resubmit(args))
        parser_tm.add_argument('job_ids', nargs='+', type=int, help='id of the job')
        parser_tm.add_argument('-f', '--force', action='store_true', help='force resubmit job')

    def func_resubmit(self, args):
        job_ids = args.job_ids
        force = args.force
        for each in job_ids:
            if not force:
                if not query_yes_no(f'do you want to resubmit this job with id: {each}', default='no'):
                    continue
            result = self.cli.client.job.resubmit(each)
            if result == {}:
                self.cli.print(f'successfully resubmit job with id: {each}')
