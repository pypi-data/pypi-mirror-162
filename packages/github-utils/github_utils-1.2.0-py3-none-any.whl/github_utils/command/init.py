import os
import configparser
from argparse import ArgumentParser, Namespace


def add_arguments(parser: ArgumentParser):
    pass


def execute(args: Namespace):
    config = configparser.ConfigParser()
    config['credential'] = {
        'token': '__TOKEN__'
    }
    config['project'] = {
        'dir': '%s/Projects' % os.getenv('HOME'),
    }

    config.write(open(args.config, 'w'))
