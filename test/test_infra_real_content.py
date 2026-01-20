from pathlib import Path

import pytest

from src.infra.parser.verilog_stream_parser import VerilogStreamParser


@pytest.fixture()
def parser() -> VerilogStreamParser:
    return VerilogStreamParser()


def test_verilog_parser_with_real_content(parser):
    path_verilog = Path("test/input/infra/real_content/CHIPTOP_Decoder_inst_design.v")

    node_batches = tuple(parser.parse_nodes(path_verilog, batch_size=100))
    nodes_all = [n for batch in node_batches for n in batch]

    assert len(nodes_all) > 0, "Nodes should be extracted!"
    assert any(n.name == "SAMPLE" for n in nodes_all)

    batches = tuple(parser.parse_edges(path_verilog, batch_size=100))
    edges_all = (e for batch in batches for e in batch)

    edge_a1 = next((e for e in edges_all if e.src_node == "u_cell_3491.A1"), None)
    assert edge_a1 is not None
    assert edge_a1.dst_node == "place_opt_HFSNET_2"

    edge_zn = next((e for e in edges_all if e.src_node == "u_cell_3491.ZN"), None)
    assert edge_zn is not None
    assert edge_zn.dst_node == "net1966"
