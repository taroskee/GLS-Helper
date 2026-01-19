import re
from collections.abc import Iterable, Iterator
from itertools import islice
from pathlib import Path

from src.domain.model.edge import Edge
from src.domain.model.node import Node
from src.domain.protocol.verilog_parser import VerilogParser


class VerilogStreamParser(VerilogParser):
    _RE_WIRE = re.compile(r"^\s*(?:wire|input|output)\s+(?:\[.*?\]\s*)?(\w+);")
    _RE_INST_START = re.compile(r"^\s*(\w+)\s+(\w+)\s*\(")
    _RE_PIN_CONNECTION = re.compile(r"\.(\w+)\s*\(\s*(\w+)\s*\)")

    def parse_nodes(
        self, path_verilog_dir: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Node, ...]]:
        lines = self._read_lines(path_verilog_dir)
        nodes = self._extract_nodes(lines)
        yield from self._batch_data(nodes, batch_size)

    def parse_edges(
        self, path_verilog_dir: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Edge, ...]]:
        lines = self._read_lines(path_verilog_dir)
        edges = self._extract_edges(lines)
        yield from self._batch_data(edges, batch_size)

    def _read_lines(self, path: Path) -> Iterator[str]:
        """Reads file line by line lazily."""
        with path.open(encoding="utf-8") as f:
            yield from f

    def _batch_data(self, data: Iterable, size: int) -> Iterator[tuple]:
        """Groups data into batches of specified size."""
        iterator = iter(data)
        while batch := tuple(islice(iterator, size)):
            yield batch

    def _extract_nodes(self, lines: Iterator[str]) -> Iterator[Node]:
        """Parses lines to find wire/input/output definitions."""
        for line in lines:
            if match := self._RE_WIRE.search(line):
                yield Node(match.group(1))

    def _extract_edges(self, lines: Iterator[str]) -> Iterator[Edge]:
        """Parses lines to find instance connections, maintaining state."""
        inst: str | None = None
        for line in lines:
            inst = self._update_inst_start(line, inst)
            yield from self._find_connections(line, inst)
            inst = self._update_inst_end(line, inst)

    def _update_inst_start(self, line: str, current: str | None) -> str | None:
        """Updates instance name if a new instance declaration starts."""
        if match := self._RE_INST_START.search(line):
            return match.group(2)
        return current

    def _update_inst_end(self, line: str, current: str | None) -> str | None:
        """Resets instance name if the declaration ends."""
        return None if ";" in line else current

    def _find_connections(self, line: str, inst: str | None) -> Iterator[Edge]:
        """Yields Edges found in the current line for the active instance."""
        if not inst:
            return
        for match in self._RE_PIN_CONNECTION.finditer(line):
            yield Edge(src_node=f"{inst}.{match.group(1)}", dst_node=match.group(2))
