from lbgcli.const import ConfigKey, GlobalConfig
from lbgcli.module_impl import Module, TableResult, append_format_to_parser


class ProgramModule(Module):

    def __init__(self, cli, self_name):
        self.name = self_name
        super().__init__(cli)

    def add_to_parser(self, subparser):
        self.parser = subparser.add_parser(self.name, help=f'Operating {self.name} Module')
        self.parser.set_defaults(func=lambda _: self.parser.print_help())
        self.sub_parser = self.parser.add_subparsers()
        self.load_ls()
        self.load_switch()
        self.load_current()
        # self.load_rm()
        # self.load_add()
        # self.load_withdraw()
        # self.load_charge()

    def load_ls(self):
        parser_ls = self.sub_parser.add_parser('ls', help=f'list all available {self.name}')
        parser_ls.set_defaults(func=lambda args: self.func_ls(args))
        parser_ls.add_argument('-q', '--quiet', action='store_true', help=f'only show {self.name} id')
        parser_ls.add_argument('-s', '--self', action='store_true',
                               help=f'only show {self.name} belong to current user')
        parser_ls.add_argument('-o', '--other', action='store_true',
                               help=f'only show {self.name} not belong to current user')
        append_format_to_parser(parser_ls)
        # parser_ls.add_argument('-f', '--format', action='store', help='change header format')

    def func_ls(self, args):
        result = self.cli.client.program.list_all_program()

        def filter_func(each_value):
            if args.self:
                if each_value['creatorId'] != self.cli.client.user_id:
                    return False
            if args.other:
                if each_value['creatorId'] == self.cli.client.user_id:
                    return False
            return True

        def map_func(v):
            v["Remaining Budget"] = 0
            costKey = ["totalCost", "costLimit", "monthCost"]
            for eachKey in costKey:
                v[eachKey] = v[eachKey] / 100
            if v.get('costLimitType'):
                if v.get('costLimitType') == 1:
                    v['costLimitTypeStr'] = "Total Budget"
                    v["Remaining Budget"] = round(v["costLimit"] - v["totalCost"], 2)
                elif v.get('costLimitType') == 2:
                    v['costLimitTypeStr'] = "Monthly Budget"
                    v["Remaining Budget"] = round(v["costLimit"] - v["monthCost"], 2)
            if v["costLimit"] == 0:
                v["Remaining Budget"] = '-'
            for eachK, eachV in self.cli.client.program.file_accounting(v['id']).items():
                if eachK == 'path':
                    continue
                v[eachK] = eachV
            return v

        tr = TableResult(result, filter_func=filter_func, first_col='id', no_header=args.noheader,
                         default_format=self.cli.output_format(), mapper_func=map_func)

        if args.quiet:
            for each in tr.data:
                self.cli.print(each['id'])
            return
        result = tr.output(args)
        self.cli.print(result)

    def func_switch(self, args, print_message=True):
        self.cli.put(ConfigKey.CURRENT_PROGRAM_ID, args.program_id)
        if print_message:
            self.cli.print(f"successful change {self.name} id to {args.program_id}")

    def load_switch(self):
        parser_sw = self.sub_parser.add_parser('switch', help=f'switch current {self.name}')
        parser_sw.set_defaults(func=lambda args: self.func_switch(args))
        parser_sw.add_argument('program_id', metavar='<pgid>', action='store', type=int, help=f'{self.name} id')

    def func_current(self, args):
        pgid = self.cli.get(ConfigKey.CURRENT_PROGRAM_ID)
        if pgid is None:
            self.cli.print(
                f"can not find current {self.name} id, run {GlobalConfig.CALLER_NAME} {self.name} switch -h to see more information")
        else:
            self.cli.print(f"current {self.name} id is {pgid}")

    def load_current(self):
        parser_sw = self.sub_parser.add_parser('current', help=f'show current {self.name} id')
        parser_sw.set_defaults(func=lambda args: self.func_current(args))

    # def load_rm(self):
    #     parser_rm = self.sub_parser.add_parser('rm', help=f'delete selected {self.name}')
    #     parser_rm.set_defaults(func=lambda args: self.func_rm(args))
    #     parser_rm.add_argument('program_id', nargs='+', type=int, help=f'id of the {self.name}')
    #     parser_rm.add_argument('-f', '--force', action='store_true', help=f'force delete the {self.name}')
    #
    # def func_rm(self, args):
    #     program_ids = args.program_id
    #     force = args.force
    #     for each in program_ids:
    #         if not force:
    #             if not query_yes_no(f'do you want to delete this {self.name} with id: {each}', default='no'):
    #                 continue
    #         result = self.cli.client.program.delete(each)
    #         if result == {}:
    #             self.cli.print(f'successfully delete {self.name} with id: {each}')

    # def load_add(self):
    #     parser_rm = self.sub_parser.add_parser('add', help=f'create {self.name}')
    #     parser_rm.set_defaults(func=lambda args: self.func_add(args))
    #     parser_rm.add_argument('name', type=str, help=f'name of the {self.name}')
    #     parser_rm.add_argument('-b', '--balance', action='store', type=int, default=0, help='initial balance (CNY fen)')
    #
    # def func_add(self, args):
    #     self.cli.client.program.add(args.name, args.balance)

    # def load_withdraw(self):
    #     parser_withdraw = self.sub_parser.add_parser('withdraw', help=f'with balance from {self.name}')
    #     parser_withdraw.set_defaults(func=lambda args: self.func_withdraw(args))
    #     parser_withdraw.add_argument('amount', type=int, help='amount of balance to be withdraw. (CNY fen)')
    #
    # def func_withdraw(self, args):
    #     self.cli.client.program.charge(self.cli.program_id(), args.amount, kind=2)
    #
    # def load_charge(self):
    #     parser_charge = self.sub_parser.add_parser('charge', help=f'charge balance to {self.name}')
    #     parser_charge.set_defaults(func=lambda args: self.func_charge(args))
    #     parser_charge.add_argument('amount', type=int, help='amount of balance to be charge. (CNY fen)')
    #
    # def func_charge(self, args):
    #     self.cli.client.program.charge(self.cli.program_id(), args.amount, kind=1)
