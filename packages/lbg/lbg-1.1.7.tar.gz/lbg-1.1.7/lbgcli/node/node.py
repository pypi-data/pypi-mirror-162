from lbgcli.module_impl import Module, TableResult, append_format_to_parser
from lbgcli.util import query_yes_no


class NodeModule(Module):
    STATUS_WAITING = 0
    STATUS_PENDING = 1
    STATUS_STARTED = 2
    STATUS_PAUSED = -1

    def __init__(self, cli):
        super().__init__(cli)

    def add_to_parser(self, subparser):
        self.parser = subparser.add_parser('node', help='Operating Node Module')
        self.parser.set_defaults(func=lambda _: self.parser.print_help())
        self.sub_parser = self.parser.add_subparsers()
        self.load_ls()
        self.load_stop()
        self.load_start()
        self.load_rm()
        self.load_create()
        self.load_to_dev_img()

    def load_ls(self):
        parser_ls = self.sub_parser.add_parser('ls', help='list all available node')
        parser_ls.set_defaults(func=lambda args: self.func_ls(args))
        parser_ls.add_argument('-q', '--quiet', action='store_true', help='only show node id')
        parser_ls.add_argument('-s', '--started', action='store_true', help='only show started node')
        parser_ls.add_argument('-w', '--waiting', action='store_true', help='only show waiting node')
        parser_ls.add_argument('-t', '--pending', action='store_true', help='only show pending node')
        parser_ls.add_argument('-p', '--paused', action='store_true', help='only show paused node')
        # parser_ls.add_argument('-f', '--format', action='store', help='change header format')
        append_format_to_parser(parser_ls)

    def to_status_long(self, s):
        if s == self.STATUS_WAITING:
            return 'waiting'
        elif s == self.STATUS_PENDING:
            return 'pending'
        elif s == self.STATUS_STARTED:
            return 'started'
        elif s == self.STATUS_PAUSED:
            return 'paused'
        else:
            return 'unknown'

    def func_ls(self, args):
        result = self.cli.client.server.list_server(self.cli.program_id())

        def mapper_func(each_value: dict):
            each_value['status_desc'] = self.to_status_long(each_value['status'])
            return each_value

        def filter_func(each_value):
            if all([not args.started, not args.waiting, not args.pending, not args.paused]):
                return True
            if args.started:
                if each_value['status'] == self.STATUS_STARTED:
                    return True
            if args.waiting:
                if each_value['status'] == self.STATUS_WAITING:
                    return True
            if args.pending:
                if each_value['status'] == self.STATUS_PENDING:
                    return True
            if args.paused:
                if each_value['status'] == self.STATUS_PAUSED:
                    return True
            return False

        tr = TableResult(result, filter_func=filter_func,
                         no_header=args.noheader, mapper_func=mapper_func, default_format=self.cli.output_format())
        if args.quiet:
            for each in tr.data:
                self.cli.print(each['nodeId'])
            return

        self.cli.print(tr.output(args))

    def load_stop(self):
        parser_stop = self.sub_parser.add_parser('stop', help='stop selected node')
        parser_stop.set_defaults(func=lambda args: self.func_stop(args))
        parser_stop.add_argument('machine_id', nargs='+', type=int, help='machine id of the node')
        parser_stop.add_argument('-f', '--force', action='store_true', help='force stop the node')

    def func_stop(self, args):
        result = self.cli.client.server.list_server(self.cli.program_id())
        creator_dict = {each["nodeId"]: each["creatorId"] for each in result}
        machine_ids = args.machine_id
        force = args.force
        for each in machine_ids:
            if not force:
                if not query_yes_no(f'do you want to stop node with machine_id: {each}', default='no'):
                    continue
            result = self.cli.client.server.stop(each, creator_dict[each])
            if result == {}:
                self.cli.print(f'successfully stop node with machine_id: {each}')

    def load_start(self):
        parser_stop = self.sub_parser.add_parser('restart', help='restart selected node')
        parser_stop.set_defaults(func=lambda args: self.func_start(args))
        parser_stop.add_argument('machine_id', nargs='+', type=int, help='machine id of the node')

    def func_start(self, args):
        # result = self.cli.client.server.list_server(self.cli.program_id())
        # creator_dict = {each["nodeId"]: each["creatorId"] for each in result}
        machine_ids = args.machine_id
        for each in machine_ids:
            result = self.cli.client.server.restart(each)
            if result == {}:
                self.cli.print(f'successfully restart node with machine_id: {each}')

    def load_rm(self):
        parser_stop = self.sub_parser.add_parser('rm', help='delete selected node')
        parser_stop.set_defaults(func=lambda args: self.func_rm(args))
        parser_stop.add_argument('machine_id', nargs='+', type=int, help='machine id of the node')
        parser_stop.add_argument('-f', '--force', action='store_true', help='force delete the node')

    def func_rm(self, args):
        result = self.cli.client.server.list_server(self.cli.program_id())
        creator_dict = {each["nodeId"]: each["creatorId"] for each in result}
        machine_ids = args.machine_id
        force = args.force
        for each in machine_ids:
            if not force:
                if not query_yes_no(f'do you want to release node with machine_id: {each}', default='no'):
                    continue
            result = self.cli.client.server.delete(each, creator_dict[each])
            if result == {}:
                self.cli.print(f'successfully delete node with machine_id: {each}')

    def load_create(self):
        parser_stop = self.sub_parser.add_parser('create', help='create node with specific config')
        parser_stop.set_defaults(func=lambda args: self.func_create(args))
        parser_stop.add_argument('-n', '--name', action='store', help='name of the node', default='')
        parser_stop.add_argument('-i', '--image_id', action='store', type=int,
                                 help='what image id should be used', required=True)
        parser_stop.add_argument('-s', '--scass_type', action='store',
                                 help='configuration of the node', required=True)
        parser_stop.add_argument('-d', '--disk_size', action='store', type=int,
                                 help='disk size of the node', required=True)

    def parse_scass_type(self, scass_type):
        c, m, g = scass_type.split('_')
        if not c.startswith('c') and not m.startswith('m'):
            raise ValueError(f'incorrect scass_type: {scass_type}')
        try:
            core = int(c[1:])
            memory = int(m[1:])
            gpu = g
            return core, memory, gpu
        except Exception as e:
            raise ValueError(f'incorrect scass_type: {scass_type}')

    def func_create(self, args):
        name = args.name
        image = args.image_id
        scass_type = args.scass_type
        disk_size = args.disk_size
        program_id = self.cli.program_id()
        core, memory, gpu = self.parse_scass_type(scass_type)
        result = self.cli.client.server.create(image, disk_size, memory, core, gpu, program_id, name=name)
        self.cli.print(result)

    def load_to_dev_img(self):
        parser_stop = self.sub_parser.add_parser('tosnap', help='to snapshot')
        parser_stop.set_defaults(func=lambda args: self.func_todevimg(args))
        parser_stop.add_argument('-c', '--comment', action='store', help='comment of image', default='')
        parser_stop.add_argument('-i', '--image_name', action='store',
                                 help='name of the development image', required=True)
        parser_stop.add_argument('-m', '--machine_id', type=int, action='store',
                                 help='id of the node', required=True)

    def func_todevimg(self, args):
        result = self.cli.client.server.to_dev_image(args.machine_id, args.image_name, comment=args.comment)
        if 'id' in result:
            self.cli.print(f'successfully create develop image id: {result["id"]}')
