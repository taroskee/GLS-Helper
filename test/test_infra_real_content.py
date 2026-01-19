from pathlib import Path

import pytest

from src.infra.parser.verilog_stream_parser import VerilogStreamParser


@pytest.fixture()
def parser() -> VerilogStreamParser:
    return VerilogStreamParser()


def test_verilog_parser_with_real_content(parser):
    paths_verilog = Path("test/input/infra/real_content").glob("*.v")

    batches = tuple(parser.parse_edges(paths_verilog, batch_size=100))
    edges_all = (e for batch in batches for e in batch)

    edge_a1 = next((e for e in edges_all if e.src_node == "u_cell_3491.A1"), None)
    assert edge_a1 is not None
    assert edge_a1.dst_node == "place_opt_HFSNET_2"

    edge_zn = next((e for e in edges_all if e.src_node == "u_cell_3491.ZN"), None)
    assert edge_zn is not None
    assert edge_zn.dst_node == "net1966"
