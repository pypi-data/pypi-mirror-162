import sys


import click
import texcli.commands as cmd

@click.group()
def cli():
    pass


@cli.command()
@click.argument('output_filename')
@click.option('--dpi', type=int)
@click.option('--bg', default='white')
@click.option('--fg', default='black')
def latex(output_filename, dpi, bg, fg):
    tex = ''.join(sys.stdin).replace('\n', ' ')
    if not dpi:
        dpi = 300
    cmd.latex(tex, output_filename, dpi, bg, fg)


