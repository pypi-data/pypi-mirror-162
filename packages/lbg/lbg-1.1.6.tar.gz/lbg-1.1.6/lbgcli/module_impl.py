import json
import textwrap
from enum import Enum

import pandas as pd
import yaml


class Module:
    def __init__(self, cli):
        self.cli = cli
        self.parser = None
        self.sub_parser = None


def append_format_to_parser(parser):
    parser.add_argument('--csv', action='store_true', help='output with csv format')
    parser.add_argument('--json', action='store_true', help='output with json format')
    parser.add_argument('--yaml', action='store_true', help='output with yaml format')
    parser.add_argument('--table', action='store_true', help='output with table format')
    parser.add_argument('--noheader', action='store_true', help='does not print header information')


class OutputFormat(Enum):
    JSON = 'json'
    YAML = 'yaml'
    CSV = 'csv'
    TABLE = 'table'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, OutputFormat))


class TableResult:
    def __init__(self, raw_data, filter_func=None, first_col=None, no_header=False, mapper_func=None, sort_by=None,
                 ascending=True, default_format=None, columns_order=None
                 ):
        if sort_by is None:
            sort_by = []
        self.filter_func = filter_func
        self.no_header = no_header
        self.default_format = default_format
        left_item = raw_data
        if mapper_func is not None:
            left_item = list(map(mapper_func, left_item))
        if filter_func is not None:
            left_item = list(filter(filter_func, left_item))
        self.data = left_item
        self.df = pd.DataFrame.from_dict(left_item)
        if sort_by:
            self.df.sort_values(sort_by, ascending=ascending, inplace=True)
        if columns_order:
            columns_order.reverse()
            for each in columns_order:
                self.move_index_to_front(each)
        if first_col:
            self.move_index_to_front(first_col)

    def to_csv(self):
        return self.df.to_csv(header=not self.no_header, index=False)

    def to_table(self):
        if len(self.df) == 0:
            return ''
        return self.df.to_string(header=not self.no_header, index=False, col_space=12)

    def to_json(self):
        return json.dumps(self.df.to_dict("records"), indent=4, ensure_ascii=False)

    def to_yaml(self):
        return yaml.dump(self.df.to_dict("records"))

    def output(self, args):
        if args.json:
            return self.to_json()
        if args.yaml:
            return self.to_yaml()
        if args.csv:
            return self.to_csv()
        if args.table:
            return self.to_table()
        if self.default_format == OutputFormat.JSON.value:
            return self.to_json()
        if self.default_format == OutputFormat.YAML.value:
            return self.to_yaml()
        if self.default_format == OutputFormat.CSV.value:
            return self.to_csv()
        return self.to_table()

    def move_index_to_front(self, col_name):
        if col_name not in self.df.columns:
            return
        self.df.set_index(self.df.pop(col_name), inplace=True)
        self.df.reset_index(inplace=True)


class TolerantException(Exception):
    pass


def generate_example(detail):
    if not detail:
        return ""
    value = '''example:
'''
    for k, v in detail.items():
        value += f"  %(prog)s {k}   # {v}\n"
    return textwrap.dedent(value)
