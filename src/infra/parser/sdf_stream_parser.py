import re
from collections.abc import Iterable, Iterator
from itertools import islice
from pathlib import Path

from src.domain.model.edge import Edge
from src.domain.protocol.sdf_parser import SDFParser


class SDFStreamParser(SDFParser):
    _RE_INTERCONNECT = re.compile(
        r"\(INTERCONNECT\s+([\w/\[\]]+)\s+([\w/\[\]]+)\s+\(.*?::([\d\.\-]+)\)\s+\(.*?::([\d\.\-]+)\)"
    )

    def parse_delays(
        self, path_sdf: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Edge, ...]]:
        lines = self._read_lines(path_sdf)
        statements = self._yield_interconnect_blocks(lines)
        edges = self._extract_edges(statements)
        yield from self._batch_data(edges, batch_size)

    # --- Private Helpers ---

    def _read_lines(self, path: Path) -> Iterator[str]:
        with path.open(encoding="utf-8") as f:
            yield from f

    def _batch_data(self, data: Iterable, size: int) -> Iterator[tuple]:
        iterator = iter(data)
        while batch := tuple(islice(iterator, size)):
            yield batch

    def _yield_interconnect_blocks(self, lines: Iterator[str]) -> Iterator[str]:
        """
        Yields complete (INTERCONNECT ...) blocks.
        Ignores outer nesting (like DELAYFILE, CELL) and handles multi-line blocks.
        """
        buffer: list[str] = []
        balance = 0
        in_record = False

        # Regex to find parenthesis tokens to speed up parsing
        # We only care about parentheses to track nesting balance
        re_parens = re.compile(r"[()]")

        for line in lines:
            # Optimization: Skip irrelevant lines quickly if not currently parsing a block
            if not in_record and "(INTERCONNECT" not in line:
                continue

            pos = 0
            while pos < len(line):
                # 1. Find start of block if we are not in one
                if not in_record:
                    start = line.find("(INTERCONNECT", pos)
                    if start == -1:
                        break  # No more blocks on this line

                    in_record = True
                    balance = 0
                    pos = start
                    # Do not increment pos yet; the loop below needs to count the opening '('

                # 2. Scan parentheses to find the end of the block
                remainder = line[pos:]
                found_end = False
                end_relative_idx = 0

                # Iterate over all parens in the remainder of the line
                for match in re_parens.finditer(remainder):
                    char = match.group()
                    if char == "(":
                        balance += 1
                    else:
                        balance -= 1

                    if balance == 0:
                        # Found the matching closing parenthesis
                        end_relative_idx = match.end()
                        found_end = True
                        break

                if found_end:
                    # Append the part up to the closing paren
                    chunk = remainder[:end_relative_idx]
                    buffer.append(chunk)

                    yield "".join(buffer)

                    # Reset for next block
                    buffer = []
                    in_record = False
                    pos += end_relative_idx
                else:
                    # The block continues to the next line
                    buffer.append(remainder)
                    break  # Go to next line

    def _extract_edges(self, statements: Iterator[str]) -> Iterator[Edge]:
        """Parses complete statements to create Edge objects with delay."""
        for stmt in statements:
            match = self._RE_INTERCONNECT.search(stmt)
            if match:
                src, dst, rise, fall = match.groups()
                yield Edge(
                    src_node=src,
                    dst_node=dst,
                    delay_rise=float(rise),
                    delay_fall=float(fall),
                )
