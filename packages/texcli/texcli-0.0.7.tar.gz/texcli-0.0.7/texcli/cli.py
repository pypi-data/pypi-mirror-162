import sys


import click
import texcli.commands as cmd

@click.group()
def cli():
    pass


@cli.command()
@click.argument('output_filename')
@click.option('--dpi', type=int)
@click.option('--background')
def latex(output_filename, dpi, background):
    tex = ''.join(sys.stdin).replace('\n', ' ')
    if not dpi:
        dpi = 300
    if not background:
        bgcolor = 'white'
    cmd.latex(tex, output_filename, dpi, background)


