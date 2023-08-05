import click

CTX_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    max_content_width=80,
)

# ┌────────────┐
# │ ENTRYPOINT │
# └────────────┘

main_epilog = """
You can use 'pymegen <command> --help' to show options for a specific command.

Global options can also be set as environment variables (e.g., DEBUG=1).

More info at https://github.com/iacchus/python-math-exercises-generator
"""

# On the help screen, sort commands by definition order, not alphabetically.
# See https://github.com/pallets/click/issues/513#issuecomment-504158316
class SortCommands(click.Group):
    def list_commands(self, ctx):
        return self.commands.keys()

@click.group(cls=SortCommands,
             options_metavar='[options]',
             subcommand_metavar='<command> [--help]',
             epilog=main_epilog,
             context_settings=CTX_SETTINGS)
@click.option('--debug/--no-debug',
              help='Turn on debugging',
              default=False, envvar='DEBUG')
def cli(debug):

    if debug:
        pass  # at least we know debug is on

    print("ok, debug is", debug)


# ┌────────────────┐
# │ COMMON OPTIONS │
# └────────────────┘


my_option = \
    click.option('-a', '--answer', type=click.IntRange(1, 60), default=7,
                 metavar='<my answer>',
                 help='Your answer to question..')


# ┌──────────┐
# │ COMMANDS │
# └──────────┘

add_epilog = "Adds two numbers"

@cli.command(options_metavar='[options]', epilog=add_epilog)
@my_option
def addition(answer):
    print("Your answer is", answer)

# ┌──────────┐
# │ __main__ │
# └──────────┘


if __name__ == "__main__":

    cli()
