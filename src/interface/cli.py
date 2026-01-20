from pathlib import Path

import click

from src.infra.parser.sdf_stream_parser import SDFStreamParser
from src.infra.parser.verilog_stream_parser import VerilogStreamParser
from src.infra.repository.sqlite_graph_repository import SqliteGraphRepository
from src.usecase.import_sdf import ImportSDFUseCase
from src.usecase.import_verilog import ImportVerilogUseCase


@click.group()
def cli() -> None:
    """GLS Helper CLI Tool."""
    pass


@cli.command()
@click.argument("verilog_file", type=click.Path(exists=True, path_type=Path))
@click.option("--db", "-d", default="gls.db", help="Path to SQLite database")
def import_verilog(verilog_file: Path, db: str) -> None:
    """Import Gate Netlist (Verilog) into the database."""
    click.echo(f"Importing Verilog from {verilog_file} into {db}...")

    # Dependency Injection (Manual)
    repo = SqliteGraphRepository(db_path=db)
    repo.setup()  # Ensure tables exist
    parser = VerilogStreamParser()
    usecase = ImportVerilogUseCase(repo, parser)

    usecase.execute(verilog_file)
    click.echo("Done.")


@cli.command()
@click.argument("sdf_file", type=click.Path(exists=True, path_type=Path))
@click.option("--db", "-d", default="gls.db", help="Path to SQLite database")
def import_sdf(sdf_file: Path, db: str) -> None:
    """Import Standard Delay Format (SDF) into the database."""
    click.echo(f"Importing SDF from {sdf_file} into {db}...")

    # Dependency Injection (Manual)
    repo = SqliteGraphRepository(db_path=db)
    # Note: repo.setup() is not strictly needed if Verilog was imported first,
    # but safe to call to ensure DB structure.
    repo.setup()
    parser = SDFStreamParser()
    usecase = ImportSDFUseCase(repo, parser)

    usecase.execute(sdf_file)
    click.echo("Done.")


if __name__ == "__main__":
    cli()
