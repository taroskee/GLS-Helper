from pathlib import Path

import click

from src.infra.parser.sdf_stream_parser import SDFStreamParser
from src.infra.parser.verilog_stream_parser import VerilogStreamParser
from src.infra.repository.sqlite_graph_repository import SqliteGraphRepository
from src.usecase.import_sdf import ImportSDFUseCase
from src.usecase.import_verilog import ImportVerilogUseCase
from src.usecase.trace_path import TracePathUseCase


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

    repo = SqliteGraphRepository(db_path=db)
    repo.setup()
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

    repo = SqliteGraphRepository(db_path=db)
    repo.setup()
    parser = SDFStreamParser()
    usecase = ImportSDFUseCase(repo, parser)

    usecase.execute(sdf_file)
    click.echo("Done.")


@cli.command()
@click.argument("start_node")
@click.argument("end_node", required=False)
@click.option("--db", "-d", default="gls.db", help="Path to SQLite database")
def trace_path(start_node: str, end_node: str | None, db: str) -> None:
    """
    Trace the max delay path from START_NODE.
    If END_NODE is provided, finds path to that node.
    Otherwise, finds the critical path to any reachable node.
    """
    repo = SqliteGraphRepository(db_path=db)
    usecase = TracePathUseCase(repo)

    path = usecase.execute(start_node, end_node)

    target_msg = f"to {end_node}" if end_node else "(Critical Path)"

    if not path:
        click.echo(f"No path found from {start_node} {target_msg}.")
        return

    click.echo(f"Path found from {start_node} {target_msg}:")
    total_rise = 0.0
    total_fall = 0.0

    for i, edge in enumerate(path):
        click.echo(
            f"  {i + 1}. {edge.src_node} -> {edge.dst_node} "
            f"(Rise: {edge.delay_rise:.5f}, Fall: {edge.delay_fall:.5f})"
        )
        total_rise += edge.delay_rise
        total_fall += edge.delay_fall

    click.echo("-" * 40)
    click.echo(f"Total Edges: {len(path)}")
    click.echo(f"Total Delay: Rise={total_rise:.5f}, Fall={total_fall:.5f}")


if __name__ == "__main__":
    cli()
