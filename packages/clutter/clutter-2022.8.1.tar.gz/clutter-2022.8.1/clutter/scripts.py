import click

from .docker import load_secrets, SECRETS_DIR, SECRETS_DELIM
from .aws import list_secrets


@click.group()
def clutter():
    pass


@clutter.command()
@click.argument("patterns", nargs=-1)
@click.option("--profile", default=None)
def list_aws_secrets(patterns, profile):
    patterns = patterns if patterns else "*"
    list_secrets(patterns=patterns, profile_name=profile)


# [NOTE]
# Child Process Cannot Load Parent's Environment Variables!
# @clutter.command()
# @click.option("--secrets-dir", type=click.Path(exists=True, file_okay=False), default=SECRETS_DIR, show_default=True)
# @click.option("--secrets-delim", type=str, default=SECRETS_DELIM, show_default=True)
# def load_envs_from_docker_secrets(secrets_dir, secrets_delim):
#     load_secrets(secrets_dir=secrets_dir, secrets_delim=secrets_delim)
