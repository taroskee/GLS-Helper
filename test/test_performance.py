import pytest
from src.domain.model.edge import Edge
from src.infra.parser.sdf_stream_parser import SDFStreamParser
from src.infra.repository.sqlite_graph_repository import SqliteGraphRepository
from src.usecase.import_sdf import ImportSDFUseCase


@pytest.fixture
def performance_setup(tmp_path):
    db_path = tmp_path / "perf.db"
    sdf_path = tmp_path / "perf.sdf"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    num_records = 100000

    edges = [
        Edge(src_node=f"u{i}.Q", dst_node=f"u{i + 1}.D", delay_rise=0.0, delay_fall=0.0)
        for i in range(num_records)
    ]
    repo.save_edges_batch(edges)

    # DB: u{i}.Q -> u{i+1}.D
    # SDF: (INTERCONNECT u{i}/Q u{i+1}/D ...)
    lines = [
        "(DELAYFILE",
        "  (CELL",
        '    (CELLTYPE "TOP")',
        "    (INSTANCE)",
        "    (DELAY",
        "      (ABSOLUTE",
    ]
    for i in range(num_records):
        line = f"        (INTERCONNECT u{i}/Q u{i + 1}/D (0.1::0.1) (0.1::0.1))"
        lines.append(line)
    lines.extend(["      )", "    )", "  )", ")"])
    sdf_path.write_text("\n".join(lines), encoding="utf-8")

    return repo, sdf_path, num_records


def test_benchmark_import_sdf(benchmark, performance_setup):
    repo, sdf_path, num_records = performance_setup
    parser = SDFStreamParser()
    usecase = ImportSDFUseCase(repo, parser)

    def run_import():
        usecase.execute(sdf_path, observer=None)

    benchmark(run_import)

    mean_time = benchmark.stats.stats.mean
    items_per_sec = num_records / mean_time

    threshold_seconds = 1.5

    assert mean_time < threshold_seconds, (
        f"Too slow! Average time: {mean_time:.4f}s ({items_per_sec:.0f} items/s). "
        f"Target is < {threshold_seconds}s"
    )
