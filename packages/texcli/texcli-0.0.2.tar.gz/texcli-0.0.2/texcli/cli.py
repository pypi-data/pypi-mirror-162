import sys


import click
import texcli.commands as cmd

@click.group()
def cli():
    pass


@cli.command()
@click.argument('output_filename')
def latex(output_filename):
    tex = ''.join(sys.stdin).replace('\n', ' ')
    cmd.latex(tex, output_filename)


