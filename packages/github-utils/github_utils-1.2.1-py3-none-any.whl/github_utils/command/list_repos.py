from argparse import ArgumentParser, Namespace
from github import Github
from ..config import load_config


def add_arguments(parser: ArgumentParser):
    parser.add_argument('--organization', help='repository organization', metavar='ORG')


def execute(args: Namespace):
    config = load_config(args.config)

    gh = Github(login_or_token=config.credential_token)

    if args.organization is None:
        target = gh.get_user()
    else:
        target = gh.get_organization(args.organization)

    for repo in target.get_repos():
        print(repo.full_name)

    return 0
