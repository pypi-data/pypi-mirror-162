import sys
import os
import argparse
import importlib


def print_help():
    usage = '''usage: gutils <command> [parameters]

    To see help text, you can run:
      gutils <command> --help
'''
    sys.stderr.write(usage)


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1][0] == '-':
        print_help()
        return -1

    parser = argparse.ArgumentParser()
    parser.add_argument('command')

    # add common arguments
    group = parser.add_argument_group('common')
    parser.add_argument('--config', help='path of configuration file', metavar='FILE', required=False, default='%s/.github-utils/config.ini' % (os.getenv('HOME')))

    command = importlib.import_module('github_utils.command.%s' % (sys.argv[1].replace('-', '_')))
    command.add_arguments(parser)

    return command.execute(
        args=parser.parse_args()
    )


if __name__ == '__main__':
    sys.exit(main())
