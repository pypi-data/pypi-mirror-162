from argparse import ArgumentParser, Namespace
from github import Github
from github.GithubObject import NotSet
from ..config import load_config


def add_arguments(parser: ArgumentParser):
    parser.add_argument('--organization', help='repository organization', metavar='ORG')
    parser.add_argument('--all', action='store_true', help='remove all repositories', default=False)
    parser.add_argument('name', nargs='*', help='name of repository', default=NotSet)


def execute(args: Namespace):
    config = load_config(args.config)

    gh = Github(login_or_token=config.credential_token)

    if args.organization is None:
        target = gh.get_user()
    else:
        target = gh.get_organization(args.organization)

    if args.all:
        for repo in target.get_repos():
            repo.delete()
    else:
        for name in args.name:
            target.get_repo(name).delete()
