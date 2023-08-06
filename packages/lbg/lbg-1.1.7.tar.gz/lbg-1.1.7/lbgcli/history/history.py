import argparse
import json
import os
from datetime import datetime, timedelta

import pandas
import pytimeparse

from lbgcli.const import GlobalConfig
from lbgcli.module_impl import Module, TolerantException, TableResult, generate_example


class HistoryModule(Module):

    def __init__(self, cli):
        super().__init__(cli)

    def add_to_parser(self, subparser):
        self.parser = subparser.add_parser('history', help='Operating History Module')
        self.parser.set_defaults(func=lambda _: self.parser.print_help())
        self.sub_parser = self.parser.add_subparsers()
        self.load_job()

    def load_job(self):
        examples = {
            "-s 3d15h": "show job submit history before 3 days and 15 hours",
            "-as": "show result with ascending order",
            "-n 50": "only show 50 records",
        }
        parser_job = self.sub_parser.add_parser('job', help='list all job submit history',
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                epilog=generate_example(examples))
        parser_job.set_defaults(func=lambda args: self.func_job(args))

        parser_job.add_argument('-s', '--start', action='store',
                                help='default is a day ago. format: 1w3d2h32m or d:h:s')
        parser_job.add_argument('-e', '--end', action='store',
                                help='default now. format: 1w3d2h32m or d:h:s')
        parser_job.add_argument('-as', '--asce', action='store_true',
                                help='list by ascending, default descending')
        # append_format_to_parser(parser_job)
        parser_job.add_argument('-n', '--number', action='store', type=int, default=50,
                                help='number of log to be display, default 50')

    def get_log(self):
        ctx_dir_location = os.path.expanduser(self.cli.LBG_CLI_CTX_DIR_LOCATION)
        path = os.path.join(ctx_dir_location, GlobalConfig.CONFIG_ACTION_RECORD)
        if not os.path.exists(path):
            raise TolerantException("no history")
        dateparse = lambda x: datetime.fromisoformat(x)
        df = pandas.read_csv(path, index_col=0, names=["date", "module", "function", "meta"], parse_dates=['date'],
                             date_parser=dateparse)
        return df

    def func_job(self, args):
        logs = self.get_log()
        start = datetime.now() - timedelta(days=1)
        if args.start:
            start_value = pytimeparse.parse(args.start)
            start = datetime.now() - timedelta(seconds=start_value)
        end = datetime.now()
        if args.end:
            end_value = pytimeparse.parse(args.end)
            end = datetime.now() - timedelta(seconds=end_value)
        df = logs[start:end]
        df = df[df['module'] == 'job']
        if args.asce:
            df = df[::-1]
        if args.number:
            df = df[:args.number]
        df.reset_index(inplace=True)
        result = json.loads(df.to_json(date_format='iso'))
        tr = TableResult(result, first_col='date', default_format=self.cli.output_format())
        # print(tr.df)
        result = tr.to_table()
        self.cli.print(result)
