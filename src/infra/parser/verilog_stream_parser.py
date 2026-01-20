import re
from collections.abc import Iterator
from pathlib import Path

from src.domain.model.edge import Edge
from src.domain.model.node import Node
from src.domain.protocol.progress_observer import ProgressObserver
from src.domain.protocol.verilog_parser import VerilogParser


class VerilogStreamParser(VerilogParser):
    _RE_WIRE = re.compile(r"^\s*(?:wire|input|output)\s+(?:\[.*?\]\s*)?(\w+)\s*;")
    _RE_ASSIGN = re.compile(r"^\s*assign\s+(\w+)\s*=\s*(\w+)\s*;")
    _RE_INST_START = re.compile(r"^\s*(\w+)\s+(\w+)\s*\(")
    _RE_PIN = re.compile(r"\.\s*(\w+)\s*\(\s*(\w+)\s*\)")
    _RE_INST_END = re.compile(r"\)\s*;")

    def parse_nodes(
        self,
        path: Path,
        batch_size: int = 10000,
        observer: ProgressObserver | None = None,
    ) -> Iterator[tuple[Node, ...]]:
        batch: list[Node] = []
        for line in self._read_lines(path):
            if observer:
                observer.update(len(line))

            if match := self._RE_WIRE.search(line):
                batch.append(Node(match.group(1)))

            if len(batch) >= batch_size:
                yield tuple(batch)
                batch = []

        if batch:
            yield tuple(batch)

    def parse_edges(
        self,
        path: Path,
        batch_size: int = 10000,
        observer: ProgressObserver | None = None,
    ) -> Iterator[tuple[Edge, ...]]:
        batch: list[Edge] = []
        current_inst_name: str | None = None

        for line in self._read_lines(path):
            if observer:
                observer.update(len(line))

            if match := self._RE_ASSIGN.search(line):
                batch.append(Edge(match.group(2), match.group(1), 0.0, 0.0))
                continue

            if match := self._RE_INST_START.search(line):
                current_inst_name = match.group(2)

            if current_inst_name:
                for match in self._RE_PIN.finditer(line):
                    pin_name = match.group(1)
                    net_name = match.group(2)
                    src_node = f"{current_inst_name}.{pin_name}"
                    dst_node = net_name
                    batch.append(Edge(src_node, dst_node, 0.0, 0.0))
            if self._RE_INST_END.search(line):
                current_inst_name = None

            if len(batch) >= batch_size:
                yield tuple(batch)
                batch = []

        if batch:
            yield tuple(batch)

    def _read_lines(self, path: Path) -> Iterator[str]:
        with path.open(encoding="utf-8") as f:
            yield from f
