from collections.abc import Iterator
from pathlib import Path

from domain.protocol.verilog_parser import VerilogParser
from src.domain.model.edge import Edge
from src.domain.model.node import Node


class VerilogStreamParser(VerilogParser):
    def parse_nodes(
        self, path_verilog_dir: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Node]]:
        yield (Node(""),)

    def parse_edges(
        self, path_verilog_dir: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Node]]:
        yield (Edge("", "", 0, 0),)
