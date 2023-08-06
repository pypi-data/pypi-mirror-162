from .keycloak import Keycloak
from . import poolparty
from . import jenkins

from functools import update_wrapper, partial
from configparser import ConfigParser
from sys import platform
import subprocess
import os
import sys
import appdirs
import click
import tempfile

from pathlib import Path

from loguru import logger


@click.group()
def cli():
    """The venerable P3D command line utils"""
    ...

@cli.group()
def jk():
    """Jenkins commands"""
    ...

@cli.group()
def pp():
    """PoolParty commands"""
    ...

@cli.group()
def kc():
    """Keycloak commands"""
    ...

def kc_adm_command(func):
    """Decorator to encapsulate common logic for kc admin commands that need authentication"""
    @click.option("--server", help="The server url")
    @click.option("--username", help="The username for import must have rights to modify the realm")
    @click.option("--password", help="The password")
    @click.option("--user_realm_name", help="The realm the user is in")
    @click.option("--realm_name", help="The realm the mappers should be added to")
    @click.option("--auth_config", type=click.Path(exists=True, dir_okay=False, readable=True), help="Read KC authorization from a config file")
    @click.option("--auth", help="Read KC authorization from a config file")
    @click.pass_context
    def inner(ctx, *args, **kwargs):
        # make sure ctx.obj is a dict
        ctx.ensure_object(dict)

        # fill params with cli args
        params = {
            'server': kwargs['server'],
            'username': kwargs['username'],
            'password': kwargs['password'],
            'user_realm_name': kwargs['user_realm_name'],
            'realm_name': kwargs['realm_name']
        }

        # read from config file and set params if not already set by cli arg
        if 'auth_config' in kwargs and 'auth' in kwargs:
            def set_from_config(config, param_name):
                if param_name in config[kwargs['auth']] and params[param_name] is None:
                    params[param_name] = config[kwargs['auth']][param_name]

            config = ConfigParser()
            config.read(kwargs['auth_config'])

            list(map(partial(set_from_config, config), params.keys()))

        # prompt for missing values that are still missing
        def prompt_if_missing(param_name: str):
            if params[param_name] is None:
                params[param_name] = click.prompt(param_name.capitalize())
        list(map(prompt_if_missing, params.keys()))

        # remove arguments from `**kwargs` that are consumed by this auth decorator
        # this is needed s.t. decorated functions don't have to be modified to accept
        # those values too (`click` is a bit strange there unfortunately)
        #
        # if we just add `**kwargs` to the decorated function it adds params of
        # sub-commands twice once as positional and then again in `**kwargs` so
        # that ain't not going to working either. Also we'd have to modify
        # downstream to cater for upstream particularities which we want to
        # avoid.
        #
        # maybe there's a better way with some `click` magic
        for param_name in params.keys(): del kwargs[param_name]
        del kwargs['auth_config']
        del kwargs['auth']

        if not params['server'].endswith('/'): params['server'] += '/'

        kc = Keycloak(params['server'], params['username'], params['password'], params['user_realm_name'], params['realm_name'])
        ctx.obj['kc'] = kc
        return ctx.invoke(func, ctx, **kwargs)
    return update_wrapper(inner, func)


@kc.command()
@click.argument("json", type=click.File('r'))
@click.pass_context
@kc_adm_command
def add_mappers(ctx, json):
    """Add mappers to Keycloak IdP from realm export"""
    kc = ctx.obj['kc']
    kc.import_mappers(json)

@pp.command()
@click.argument("clear_text")
@click.option("--password", prompt=True, help="The password used for encryption")
@click.option("--salt", prompt=True, help="The salt used for encryption")
@click.option("--strength", prompt=True, type=click.INT, help="The strength used for encryption")
def encrypt(clear_text: str, password: str, salt: str, strength: int):
    """Encrypt clear text with poolparty encryption

    The settings for PASSWORD, SALT and STRENGTH can usually be found in the
    poolparty.properties file.

    Leave out any of option parameters (--password, --salt, --strengh) to get an
    interactive prompt.
    """
    secret = poolparty.encrypt(clear_text, password, salt, strength)
    print(f"Secret: {secret}")

@pp.command()
@click.argument("secret")
@click.option("--password", prompt=True, help="The password used for decryption")
@click.option("--salt", prompt=True, help="The salt used for decryption")
@click.option("--strength", prompt=True, type=click.INT, help="The strength used for decryption")
def decrypt(secret: str, password: str, salt: str, strength: int):
    """Decrypt secret text with poolparty encryption

    The settings for PASSWORD, SALT and STRENGTH can usually be found in the
    poolparty.properties file.

    Leave out any of the option parameters (--password, --salt, --strengh) to get an interactive prompt.
    """
    clear = poolparty.decrypt(secret, password, salt, strength)
    print(f"Clear: {clear}")

@pp.command()
@click.option("--path", type=click.Path(exists=True, file_okay=False, writable=True))
def install_snapshot(path: Path):
    """Download and invoke the snapshot installer

    Specify `--path` to download the installer to a specific folder. Otherwise,
    the installer will be installed in a temporary directory.

    This command is restricted to Linux for now.
    """

    if platform != "linux":
        logger.error("This command is only implemented for Linux")
        sys.exit(1)

    if not path:
        path = Path(tempfile.gettempdir())

    poolparty.install_snapshot(path)


@pp.command()
@click.option("--port", type=click.INT, default=5000, help="The port to run the server on [default: 5000]")
def mock_server(port: int):
    """Runs a mock server for testing and debugging external integrations

    PoolParty provides several integrations with external APIs/services (cf.
    Semantic Middleware Configurator). This command starts a mock server for
    debugging/testing such integrations.

    The port on which to run the server can be specified via --port. It defaults
    to 5000.

    # Webhook consumer
    Starts a server and echoes any request (+ auxiliary information) coming in.
    In addition starts a healthcheck endpoint that just always returns `200 OK`.

    The webhook consumer url (to configure in Semantic Middleware Configurator)
    is `http://localhost:5000/hook`.
    """

    poolparty.run_mock_server(port)

@jk.command()
@click.option("--branch", help="The branch to build")
@click.option('--no-autodetect', type=click.BOOL, is_flag=True, default=False, help="Disable autodetection of branch in a git repository")
@click.option('--api-user', type=click.STRING, help="Jenkins API user (your username)")
@click.option('--api-key', type=click.STRING, help="Jenkins API key (generate in Jenkins)")
def build(branch: str, no_autodetect: bool, api_key: str, api_user: str):
    """Run the PoolParty build

    Per default (and outside a git repository) builds the `develop` branch of
    PoolParty.

    When inside a git repository `p3do` will automatically detect the current
    branch and build it. This behavior can be disabled with --no-autodetect.

    The branch to build can be specified via --branch (note that this implies
    --no-autodetect inside a git repository).
    """

    if not api_key:
        cache_dir = appdirs.user_cache_dir("p3do")
        os.makedirs(cache_dir, exist_ok=True)
        jk_key = os.path.join(cache_dir, "jk_key")

        try:
            with open(jk_key, 'r') as f:
                api_key = f.read()
        except:
            api_key = click.prompt("Jenkins API Key")
            with open(jk_key, 'w') as f:
                f.write(api_key)

    if not api_user:
        cache_dir = appdirs.user_cache_dir("p3do")
        os.makedirs(cache_dir, exist_ok=True)
        jk_user = os.path.join(cache_dir, "jk_user")

        try:
            with open(jk_user, 'r') as f:
                api_user = f.read()
        except:
            api_user = click.prompt("Jenkins API User")
            with open(jk_user, 'w') as f:
                f.write(api_user)

    if not branch and no_autodetect:
        branch = "develop"
        logger.info("No branch specified and autodetect disabled. Using branch {}", branch)
    elif not branch and not no_autodetect:
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
        if res.returncode == 0:
            branch = res.stdout.decode('utf-8').strip(" \n")
            logger.info("No branch specified and autodetect enabled. Using current branch {} of git directory", branch)
        else:
            branch = "develop"
            logger.info("No branch specified and autodetect enabled. Not in a git directory. Using branch {}", branch)
    else: # branch given
        logger.info("Using branch {}", branch)

    url = jenkins.run_build("P3D-BUILD", branch, api_user, api_key)
    print(f"{url}")

@jk.command()
@click.argument("server")
@click.option("--branch", help="The branch to build")
@click.option('--no-autodetect', type=click.BOOL, is_flag=True, default=False, help="Disable autodetection of branch in a git repository")
@click.option('--api-user', type=click.STRING, help="Jenkins API user (your username)")
@click.option('--api-key', type=click.STRING, help="Jenkins API key (generate in Jenkins)")
def deploy(server: str, branch: str, no_autodetect: bool, api_key: str, api_user: str):
    """Run a PoolParty deployment

    Per default (and outside a git repository) deploys the `develop` branch of
    PoolParty.

    When inside a git repository `p3do` will automatically detect the current
    branch and deploy it. This behavior can be disabled with --no-autodetect.

    The branch to deploy can be specified via --branch (note that this implies
    --no-autodetect inside a git repository).

    The <SERVER> argument is mandatory and must be a valid ssh server name.
    PoolParty will be deployed to this server.
    """

    if not api_key:
        cache_dir = appdirs.user_cache_dir("p3do")
        os.makedirs(cache_dir, exist_ok=True)
        jk_key = os.path.join(cache_dir, "jk_key")

        try:
            with open(jk_key, 'r') as f:
                api_key = f.read()
        except:
            api_key = click.prompt("Jenkins API Key")
            with open(jk_key, 'w') as f:
                f.write(api_key)

    if not api_user:
        cache_dir = appdirs.user_cache_dir("p3do")
        os.makedirs(cache_dir, exist_ok=True)
        jk_user = os.path.join(cache_dir, "jk_user")

        try:
            with open(jk_user, 'r') as f:
                api_user = f.read()
        except:
            api_user = click.prompt("Jenkins API User")
            with open(jk_user, 'w') as f:
                f.write(api_user)

    if not branch and no_autodetect:
        branch = "develop"
        logger.info("No branch specified and autodetect disabled. Using branch {}", branch)
    elif not branch and not no_autodetect:
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
        if res.returncode == 0:
            branch = res.stdout.decode('utf-8').strip(" \n")
            logger.info("No branch specified and autodetect enabled. Using current branch {} of git directory", branch)
        else:
            branch = "develop"
            logger.info("No branch specified and autodetect enabled. Not in a git directory. Using branch {}", branch)
    else: # branch given
        logger.info("Using branch {}", branch)

    url = jenkins.run_deploy("P3D-Build-Deploy-PoolParty-(parent-pom)", server, branch, api_user, api_key)
    print(f"{url}")


if __name__ == "__main__":
    cli()
