import re
from collections.abc import Iterable, Iterator
from itertools import islice
from pathlib import Path

from src.domain.model.edge import Edge
from src.domain.protocol.sdf_parser import SDFParser


class SDFStreamParser(SDFParser):
    _RE_INTERCONNECT = re.compile(
        r"\(INTERCONNECT\s+([\w/]+)\s+([\w/]+)\s+\(.*?::([\d\.\-]+)\)\s+\(.*?::([\d\.\-]+)\)"
    )

    def parse_delays(
        self, path_sdf: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Edge, ...]]:
        yield (Edge("", ""),)

    def _read_lines(self, path: Path) -> Iterator[str]:
        with path.open(encoding="utf-8") as f:
            yield from f

    def _batch_data(self, data: Iterable, size: int) -> Iterator[tuple]:
        iterator = iter(data)
        while batch := tuple(islice(iterator, size)):
            yield batch

    def _yield_statements(self, lines: Iterator[str]) -> Iterator[str]:
        """
        Combines lines to yield complete parenthesized statements.
        Solves the issue where an entry is split across lines.
        """
        buffer = []
        balance = 0
        in_statement = False

        for line in lines:
            for char in line:
                if char == "(":
                    balance += 1
                    in_statement = True
                elif char == ")":
                    balance -= 1

            buffer.append(line.strip())

            if in_statement and balance == 0:
                yield " ".join(buffer)
                buffer = []
                in_statement = False

    def _extract_edges(self, statements: Iterator[str]) -> Iterator[Edge]:
        """Parses complete statements to create Edge objects with delay."""
        for stmt in statements:
            if "INTERCONNECT" not in stmt:
                continue

            match = self._RE_INTERCONNECT.search(stmt)
            if match:
                src, dst, rise, fall = match.groups()
                yield Edge(
                    src_node=src,
                    dst_node=dst,
                    delay_rise=float(rise),
                    delay_fall=float(fall),
                )
