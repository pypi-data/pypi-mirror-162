import profile
import click
import os
import sys
import subprocess

from xawsprofile import aws
from xawsprofile import __version__ as VERSION


@click.command(name="list", help="List all profiles.")
def list_profiles():
    profiles = list(aws.get_profiles().keys())
    sys.stdout.write("\n".join(profiles) + "\n")


def get_profiles(ctx, args, incomplete):
    options = aws.get_profiles().keys()
    # print(ctx, args, incomplete, options)
    return [incomplete]
    # return [c for c in options if incomplete in c]


@click.command(name="console", help="Open the web console using the current profile.")
@click.option(
    "--profile-name",
    required=False,
    help="Name of the profile to use.",
    shell_complete=get_profiles,
)
@click.option(
    "--stdout",
    required=False,
    default=False,
    type=bool,
    help="Print console url to stdout.",
)
def open_console(profile_name: str, stdout: bool):
    if profile_name:
        profiles = aws.get_profiles()
        profile_name = profiles.get(profile_name, None)
    aws.open_console(profile_name=profile_name, echo_to_stdout=stdout)


def shell_autocomplete(ctx, args, incomplete):
    options = ["bash", "zsh"]
    return [c for c in options if incomplete in c]


@click.command(name="completion", help="Initialize shell completion.")
@click.argument("shell", required=False, shell_complete=shell_autocomplete)
def completion(shell):
    env = {
        "_AWSPROFILE_COMPLETE": f"{shell}_source",
        "PATH": os.environ.get("PATH", ""),
    }
    output = subprocess.run(["awsprofile"], env=env, stdout=subprocess.PIPE)
    sys.stdout.write(output.stdout.decode())

    sys.stdout.write(
        """
_awsprofile()
{
    local cur="${COMP_WORDS[COMP_CWORD]}"
    opts=$(awsprofile list)
    COMPREPLY=( $(compgen -W "$opts" -- $cur) )
}
ap(){
    PROFILE=$1
    PROFILE_ALIAS=$2
    unset AWS_PROFILE
    eval $(awsprofile set "$PROFILE" --alias "$PROFILE_ALIAS")
    [[ -n "${AWS_PROFILE}" ]] && echo "Successfully Set Active AWS Profile (ENV: AWS_PROFILE) to ${PROFILE}"
}
_awsregion()
{
    local cur="${COMP_WORDS[COMP_CWORD]}"
    opts=$(awsprofile list-regions)
    COMPREPLY=( $(compgen -W "$opts" -- $cur) )
}
ar(){
    REGION=$1
    export AWS_DEFAULT_REGION=$REGION
}
complete -F _awsprofile ap
complete -F _awsregion ar"""
    )
    sys.stdout.flush()


@click.command(name="set", help="Set the current profile.")
@click.argument("name", shell_complete=get_profiles)
@click.option("--alias", required=False, help="Name of the alias to save this as.")
def set_profile(name, alias):
    profiles = aws.get_profiles()
    profile_name = profiles.get(name, None)
    if profile_name is None:
        sys.stderr.write(f"profile {name} or alias not found\n")
        exit(1)
    if alias:
        aws.save_alias(profile_name, alias)
    sys.stdout.write(f'export AWS_PROFILE="{profile_name}"')


@click.command(name="get", help="Get the full profile name.")
@click.argument("profile", shell_complete=get_profiles)
def get_profile(profile):
    profiles = aws.get_profiles()
    profile_name = profiles.get(profile, None)
    if profile_name is None:
        sys.stderr.write(f"profile {profile} or alias not found\n")
        exit(1)
    sys.stdout.write(profile_name)


def get_config_names(ctx, args, incomplete):
    options = ["cwd", "cwd-rule"]
    return [c for c in options if incomplete in c]


# awsprofile config cwd --match 'test-(.*)' --replace \1
@click.command(
    name="config", help="Manage profile configuration. Subcommands: cwd, cwd-rule"
)
@click.argument("config-name", shell_complete=get_config_names)
@click.option("--name", required=False, help="Name of the rule")
@click.option("--match", required=True, help="Regular expression to match profile name")
@click.option(
    "--replace", default=r"\1", help=r"Replace expression (\1, \2, etc for groups)"
)
@click.option(
    "--negate", flag_value=True, help="Use to negate the match (check for false)"
)
@click.option(
    "--visible", flag_value=True, default=True, help="Use to show/hide profiles"
)
def config_cli(config_name, name, match, replace, negate, visible):
    if config_name == "cwd":
        aws.save_current_naming(match, replace_with=replace)
    elif config_name == "cwd-rule":
        aws.save_naming_rule(
            name, match, replace_with=replace, visible=visible, negate=negate
        )
    else:
        click.echo("config %s not supported" % name, err=True)


@click.command(name="list-regions", help="List all the regions.")
def list_regions():
    sys.stdout.write("\n".join(aws.get_regions()) + "\n")


@click.command(name="locate-cwd-file", help="Locate the .awsprofile from the CWD.")
def locate_cwd_file():
    sys.stdout.write(aws.locate_config_file(".awsprofile"))


def version():
    return VERSION


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(VERSION)
    ctx.exit()


@click.group()
@click.help_option("--help", "-h")
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    help="Display the version.",
    expose_value=False,
    is_eager=True,
)
def main():
    pass


main.add_command(list_profiles)
main.add_command(set_profile)
main.add_command(completion)
main.add_command(list_regions)
main.add_command(config_cli)
main.add_command(locate_cwd_file)
main.add_command(get_profile)
main.add_command(open_console)
