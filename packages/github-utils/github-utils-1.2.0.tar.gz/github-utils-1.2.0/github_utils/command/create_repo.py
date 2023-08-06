from argparse import ArgumentParser, Namespace
from github import Github
from github.GithubObject import NotSet
from ..config import load_config


def add_arguments(parser: ArgumentParser):
    parser.add_argument('--organization', help='repository organization', metavar='ORG')
    parser.add_argument('--description', help='short description', metavar='DESC', default=NotSet)
    parser.add_argument('--homepage', help='url with more information', metavar='URL', default=NotSet)
    parser.add_argument('--private', action='store_true', help='private repository or not', default=True)
    parser.add_argument('--no-issues', action='store_true', help='disable issues', default=False)
    parser.add_argument('--no-wiki', action='store_true', help='disable wiki', default=False)
    parser.add_argument('--no-downloads', action='store_true', help='disable downloads', default=False)
    parser.add_argument('--team-id', help='team id to grant access', type=int, metavar='ID', default=NotSet)
    parser.add_argument('--auto-init', action='store_true', help='create initial commit', default=False)
    parser.add_argument('--gitignore', help='apply .gitignore template', metavar='LANG', default=NotSet)
    parser.add_argument('name', nargs='+', help='name of repository', default=NotSet)


def execute(args: Namespace):
    config = load_config(args.config)

    gh = Github(login_or_token=config.credential_token)

    kwargs = {
        'description': args.description,
        'homepage': args.homepage,
        'private': args.private,
        'has_issues': (not args.no_issues),
        'has_wiki': (not args.no_wiki),
        'has_downloads': (not args.no_downloads),
        'auto_init': args.auto_init,
        'gitignore_template': args.gitignore
    }

    if args.organization is None:
        target = gh.get_user()
    else:
        target = gh.get_organization(args.organization)
        if args.team_id is not NotSet:
            team = target.get_team(args.team_id)
        else:
            team = NotSet

        kwargs['team_id'] = team

    for name in args.name:
        target.create_repo(name, **kwargs)

    return 0
