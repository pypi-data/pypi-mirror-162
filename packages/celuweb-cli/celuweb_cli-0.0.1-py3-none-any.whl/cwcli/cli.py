import os
import click

@click.group()
def cli():
    pass

@click.command(name='new')
@click.option('--template', '-t', required=True, help="Selecciona el template (net, nodejs, react, flutter)")
def init(template):
    if(template == 'flutter'):
        os.system("git clone https://github.com/celuweb2/cw_flutter_scaffolding.git")
        click.echo(f"Proyecto creado {template}!")
    else: 
        click.echo(f"Comando invalido!")

cli.add_command(init)

if __name__ == '__main__':
    cli()