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
    pass


@cli.command()
@click.argument("sdf_file", type=click.Path(exists=True, path_type=Path))
@click.option("--db", "-d", default="gls.db", help="Path to SQLite database")
def import_sdf(sdf_file: Path, db: str) -> None:
    pass


if __name__ == "__main__":
    cli()
