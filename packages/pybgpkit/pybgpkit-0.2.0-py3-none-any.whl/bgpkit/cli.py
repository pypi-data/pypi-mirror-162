import argparse

from . import Parser


def main():
    parser = argparse.ArgumentParser(description="pybgpkit commandline tools")

    parsers = parser.add_subparsers(help='pybgpkit subcommands', dest="command")

    parser_parser = parsers.add_parser('parser', help='pybgpkit parser command')
    parser_parser.add_argument('--file', type=str, help='specify MRT file location', required=True)

    opts = parser.parse_args()

    if opts.command == "parser":
        parser = Parser(url=opts.file)
        elems = parser.parse_all()


if __name__ == '__main__':
    main()
