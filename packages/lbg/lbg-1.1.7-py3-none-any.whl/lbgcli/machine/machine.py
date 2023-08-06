import argparse

from lbgcli.module_impl import Module, TableResult, append_format_to_parser, generate_example


class MachineModule(Module):

    def __init__(self, cli):
        super().__init__(cli)

    def add_to_parser(self, subparser):
        self.parser = subparser.add_parser("machine", help=f'Operating Machine Module')
        self.parser.set_defaults(func=lambda _: self.parser.print_help())
        self.sub_parser = self.parser.add_subparsers()
        self.load_ls()

    def load_ls(self):
        examples = {
            "": "list all machine configuration",
            "-cpu": "only show cpu result",
            "-s cpu,memory -d": "sort by cpu and memory with descending order",
        }
        parser_ls = self.sub_parser.add_parser('ls', help=f'list all available machine',
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               epilog=generate_example(examples))
        parser_ls.set_defaults(func=lambda args: self.func_ls(args))
        parser_ls.add_argument('-cpu', action='store_true',
                               help=f'only show cpu machine')
        parser_ls.add_argument('-gpu', action='store_true',
                               help=f'only show gpu machine')
        parser_ls.add_argument('-p', '--platform', action='store',
                               help=f'show only this platform')
        parser_ls.add_argument('-s', '--sort', action='store',
                               help=f'sort with value, split by ",". default: id')
        parser_ls.add_argument('-d', '--descending', action='store_true',
                               help=f'sort with descend value')
        append_format_to_parser(parser_ls)
        # parser_ls.add_argument('-f', '--format', action='store', help='change header format')

    def func_ls(self, args):
        result = self.cli.client.machine.list_all_machine(gpu_only=args.gpu, cpu_only=args.cpu, platform=args.platform)
        sort = ["id"]
        if args.sort:
            sort = args.sort.split(",")

        def mapper_func(each_value: dict):
            each_value['machine_type'] = each_value["scass_type"]
            each_value.pop('scass_type')
            each_value.pop('ondemand_max_price')
            each_value.pop('spot_max_price')
            each_value.pop('create_time')
            return each_value

        tr = TableResult(result, mapper_func=mapper_func, columns_order=['machine_type', 'id', 'cpu',
                                                                         'memory', 'gpu', 'platform',
                                                                         'ondemand_standard_price',
                                                                         'spot_standard_price', 'update_time'],
                         no_header=args.noheader, sort_by=sort, ascending=not args.descending,
                         default_format=self.cli.output_format())

        result = tr.output(args)
        self.cli.print(result)
