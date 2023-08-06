import sys

import click

import latex2image.commands as cmd


@click.command()
@click.option('--output', '-o', required=True)
@click.option('--dpi', type=int, default=300)
@click.option('--background', '-bg', 'bg', default='#FFFFFF')
@click.option('--foreground', '-fg', 'fg', default='#000000')
def cli(output, dpi, bg, fg):
    tex = ''.join(sys.stdin).replace('\n', ' ')
    try:
        cmd.latex(tex, output, dpi, bg, fg)
    except:
        click.echo('latex failed. Trying matplotlib as fallback...')
        try:
            cmd.latex_by_mpl(tex, output, dpi, bg, fg)
        except:
            click.echo('matplotlib fallback failed. Giving up.')
