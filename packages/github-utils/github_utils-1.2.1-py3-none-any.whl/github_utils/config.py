import os
import configparser
from dataclasses import dataclass


@dataclass
class GithubConfig:
    credential_token: str
    project_dir: str
    project_ignore_pattern: str


def load_config(filename) -> GithubConfig:
    if not os.path.exists(filename):
        raise Exception('configuration file "%s" not found.' % filename)

    config = configparser.ConfigParser()
    config.read(filename)

    return GithubConfig(
        credential_token=config.get('credential', 'token'),
        project_dir=config.get('project', 'dir'),
        project_ignore_pattern=config.get('project', 'ignore_pattern')
    )
