import os
from github import Github
from argparse import ArgumentParser, Namespace
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

    repo_ignore = [repo.strip() for repo in open('%s/.github-utils/repo_ignore' % os.getenv('HOME')).readlines()]

    repo_names = []
    for repo in target.get_repos():
        if ('%s/%s' % (target.login, repo.name) not in repo_ignore) and (not os.path.exists('%s/%s' % (config.project_dir, repo.name))):
            repo_names.append(repo.name)

    for repo_name in repo_names:
        os.system('git clone git@github.com:%s/%s.git %s/%s' % (target.login, repo_name, config.project_dir, repo_name))
