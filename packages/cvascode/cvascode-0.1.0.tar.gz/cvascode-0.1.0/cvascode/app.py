import sys
from argparse import ArgumentParser
from cvascode.core.commands import version, template


def main():
    # create the top-level parser
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    data_parser = ArgumentParser(add_help=False)
    data_parser.add_argument(
        "-d",
        "--data-file",
        help="Data file(s) containing CV data in YAML format",
        action='append',
        type=str,
        required=True
        )

    # create the parser for the "version" command
    parser_version = subparsers.add_parser('version', parents=[])
    parser_version.set_defaults(func=version)

    # create the parser for the "template" command
    parser_temp = subparsers.add_parser('template', parents=[data_parser])
    parser_temp.add_argument("template_file", help="File containing jinja template to file", type=str)
    parser_temp.add_argument("output_file", help="Output file", type=str)
    parser_temp.add_argument("--docx", help="Enable docx templating, this will ignore any start/end options", action='store_true')
    parser_temp.add_argument("--block-start", help="String to mark the start of jinja block", default="{%", type=str)
    parser_temp.add_argument("--block-end", help="String to mark the end of jinja block", default="%}", type=str)
    parser_temp.add_argument("--variable-start", help="String to mark the start of jinja variable", default="{{", type=str)
    parser_temp.add_argument("--variable-end", help="String to mark the end of jinja variable", default="}}", type=str)
    parser_temp.add_argument("--comment-start", help="String to mark the start of jinja comment", default="{#", type=str)
    parser_temp.add_argument("--comment-end", help="String to mark the end of jinja comment", default="#}", type=str)
    parser_temp.set_defaults(func=template)

    # parse the args and call whatever function was selected
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError as e:
        parser.print_usage()
        print(e)
        sys.exit(1)
