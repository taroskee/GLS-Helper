import re
from collections.abc import Iterator
from pathlib import Path

from domain.protocol.verilog_parser import VerilogParser
from src.domain.model.edge import Edge
from src.domain.model.node import Node


class VerilogStreamParser(VerilogParser):
    _RE_WIRE = re.compile(r"^\s*(?:wire|input|output)\s+(?:\[.*?\]\s*)?(\w+);")
    _RE_INST_START = re.compile(r"^\s*(\w+)\s+(\w+)\s*\(")
    _RE_PIN_CONNECTION = re.compile(r"\.(\w+)\s*\(\s*(\w+)\s*\)")

    def parse_nodes(
        self, path_verilog_dir: str, batch_size: int = 10000
    ) -> Iterator[list[Node]]:
        batch = []
        with open(path_verilog_dir, encoding="utf-8") as f:
            for line in f:
                match = self._RE_WIRE.search(line)
                if match:
                    name = match.group(1)
                    batch.append(Node(name))

                if len(batch) >= batch_size:
                    yield batch
                    batch = []

        if batch:
            yield batch

    def parse_edges(
        self, path_verilog_dir: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Node]]:
        batch = []
        current_inst_name = None

        with open(path_verilog_dir, encoding="utf-8") as f:
            for line in f:
                inst_match = self._RE_INST_START.search(line)
                if inst_match:
                    current_inst_name = inst_match.group(2)

                if current_inst_name:
                    for pin_match in self._RE_PIN_CONNECTION.finditer(line):
                        pin_name = pin_match.group(1)
                        net_name = pin_match.group(2)

                        full_pin_name = f"{current_inst_name}.{pin_name}"
                        batch.append(Edge(src_node=full_pin_name, dst_node=net_name))

                    if ";" in line:
                        current_inst_name = None

                if len(batch) >= batch_size:
                    yield batch
                    batch = []

        if batch:
            yield batch
