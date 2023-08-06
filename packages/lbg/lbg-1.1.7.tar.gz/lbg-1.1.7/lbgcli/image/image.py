from lbgcli.module_impl import Module, TableResult, append_format_to_parser
from lbgcli.util import query_yes_no


class ImageModule(Module):
    STATUS_FAIL = -1
    STATUS_SCHEDULING = 0
    STATUS_PENDING = 1
    STATUS_COMPLETE = 2
    STATUS_DELETED = 3

    def status_list(self):
        return [self.STATUS_FAIL, self.STATUS_SCHEDULING, self.STATUS_PENDING, self.STATUS_COMPLETE,
                self.STATUS_DELETED]

    def __init__(self, cli):
        super().__init__(cli)

    def add_to_parser(self, subparser):
        self.parser = subparser.add_parser('image', help='Operating Image Module')
        self.parser.set_defaults(func=lambda _: self.parser.print_help())
        self.sub_parser = self.parser.add_subparsers()
        self.load_ls()
        self.load_rm()
        self.load_release()

    def load_ls(self):
        parser_ls = self.sub_parser.add_parser('ls', help='list all available image')
        parser_ls.set_defaults(func=lambda args: self.func_ls(args))
        parser_ls.add_argument('-q', '--quiet', action='store_true', help='only show node id')
        parser_ls.add_argument('-fa', '--failed', action='store_true', help='only show failed image')
        parser_ls.add_argument('-s', '--scheduling', action='store_true', help='only show scheduling image')
        parser_ls.add_argument('-p', '--pending', action='store_true', help='only show pending image')
        parser_ls.add_argument('-c', '--completed', action='store_true', help='only show completed image')
        parser_ls.add_argument('-d', '--deleted', action='store_true', help='only show deleted image')
        # parser_ls.add_argument('-sn', '--snapshot', action='store_true', help='only show image kind is "snapshot"')
        # parser_ls.add_argument('-im', '--image', action='store_true', help='only show image kind is "image"')
        # parser_ls.add_argument('-pr', '--private', action='store_true', help='only show image kind is "image"')
        parser_ls.add_argument('-f', '--format', action='store', help='change header format')
        append_format_to_parser(parser_ls)

    def func_ls(self, args):
        kind = None
        # if not all([args.snapshot, args.image]) and (args.snapshot or args.image):
        #     if args.snapshot:
        #         kind = 'snapshop'
        #     else:
        #         kind = ''
        result = self.cli.client.image.list_all_image(self.cli.program_id())

        def filter_func(each_value):
            whole_list = [args.failed, args.scheduling, args.pending, args.completed, args.deleted]
            if not any(whole_list):
                return True
            if args.failed:
                if each_value['status'] == self.STATUS_FAIL:
                    return True
            if args.scheduling:
                if each_value['status'] == self.STATUS_SCHEDULING:
                    return True
            if args.pending:
                if each_value['status'] == self.STATUS_PENDING:
                    return True
            if args.completed:
                if each_value['status'] == self.STATUS_COMPLETE:
                    return True
            if args.deleted:
                if each_value['status'] == self.STATUS_DELETED:
                    return True
            return False

        tr = TableResult(result, filter_func=filter_func, first_col='imageId',
                         no_header=args.noheader, default_format=self.cli.output_format())
        if args.quiet:
            for each in tr.data:
                self.cli.print(each['imageId'])
            return

        result = tr.output(args)
        self.cli.print(result)

    def load_rm(self):
        parser_stop = self.sub_parser.add_parser('rm', help='delete selected image')
        parser_stop.set_defaults(func=lambda args: self.func_rm(args))
        parser_stop.add_argument('image_id', nargs='+', type=int, help='id of the image')
        parser_stop.add_argument('-f', '--force', action='store_true', help='force delete the image')

    def func_rm(self, args):
        image_ids = args.image_id
        force = args.force
        for each in image_ids:
            if not force:
                if not query_yes_no(f'do you want to release server with machine_id: {each}', default='no'):
                    continue
            result = self.cli.client.image.delete(each)
            if result == {}:
                self.cli.print(f'successfully delete server with machine_id: {each}')

    def load_release(self):
        parser_stop = self.sub_parser.add_parser('release', help='release selected image')
        parser_stop.set_defaults(func=lambda args: self.func_release(args))
        parser_stop.add_argument('image_id', nargs=1, type=int, help='id of the image')
        parser_stop.add_argument('-n', '--name', type=str, help='image name')
        parser_stop.add_argument('-c', '--comment', type=str, default=[''], help='image comment')

    def func_release(self, args):
        image_id = args.image_id[0]
        program_id = self.cli.program_id()
        self.cli.client.image.release(image_id, program_id, args.name, comment=args.comment)
