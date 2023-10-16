import click
from omoospace.commands.common import choose_omoospace, to_omoospace
from omoospace.common import console


@click.command('to', help="Switch to another omoospace.")
@click.argument("omoospace", required=False, default='.',
                type=click.Path(exists=True, file_okay=False))
def cli_to(omoospace):
    try:
        omoospace = to_omoospace(omoospace)
    except Exception as err:
        console.print(err, style="warning")
        try:
            omoospace = choose_omoospace()
        except Exception as err:
            console.print(err, style="warning")
