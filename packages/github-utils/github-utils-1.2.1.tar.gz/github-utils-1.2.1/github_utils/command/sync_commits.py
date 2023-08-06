import os
from github import Github
from argparse import ArgumentParser, Namespace
from ..config import load_config


def add_arguments(parser: ArgumentParser):
    pass


def execute(args: Namespace):
    config = load_config(args.config)

    for file in os.listdir(config.project_dir):
        repo_path = '%s/%s' % (config.project_dir, file)

        if os.path.isdir(repo_path):
            os.chdir(repo_path)
            os.system('git pull origin -a')
            os.system('git push origin --all')
