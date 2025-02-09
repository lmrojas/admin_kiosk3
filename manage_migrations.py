"""
Script para manejar las migraciones de todos los servicios
"""
import os
import click
from flask.cli import with_appcontext
from app import app, SERVICES

@click.group()
def cli():
    """Comandos para manejar migraciones de todos los servicios"""
    pass

@cli.command()
@with_appcontext
def init():
    """Inicializar migraciones para todos los servicios"""
    for service in SERVICES:
        directory = f'migrations/{service}'
        os.makedirs(directory, exist_ok=True)
        os.system(f'flask db init --directory {directory}')
        click.echo(f'✅ Migraciones inicializadas para {service}')

@cli.command()
@click.option('--message', '-m', default=None, help='Mensaje de la migración')
@with_appcontext
def migrate(message):
    """Generar migraciones para todos los servicios"""
    for service in SERVICES:
        directory = f'migrations/{service}'
        cmd = f'flask db migrate --directory {directory}'
        if message:
            cmd += f' -m "{message} - {service}"'
        os.system(cmd)
        click.echo(f'✅ Migración generada para {service}')

@cli.command()
@with_appcontext
def upgrade():
    """Aplicar migraciones pendientes en todos los servicios"""
    for service in SERVICES:
        directory = f'migrations/{service}'
        os.system(f'flask db upgrade --directory {directory}')
        click.echo(f'✅ Migración aplicada para {service}')

if __name__ == '__main__':
    cli() 