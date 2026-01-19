import dataclasses
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

from src.domain.model.edge import Edge
from src.domain.protocol.sdf_parser import SDFParser


@dataclass(frozen=True)
class _ParseContext:
    """Tracks the state of parsing across lines (Immutable)."""

    buffer: tuple[str, ...] = ()
    balance: int = 0
    in_record: bool = False


class SDFStreamParser(SDFParser):
    _RE_INTERCONNECT = re.compile(
        r"\(INTERCONNECT\s+([\w/\[\]]+)\s+([\w/\[\]]+)\s+\(.*?::([\d\.\-]+)\)\s+\(.*?::([\d\.\-]+)\)"
    )
    _RE_PARENS = re.compile(r"[()]")

    def parse_delays(
        self, path_sdf: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Edge, ...]]:
        lines = self._read_lines(path_sdf)
        statements = self._yield_interconnect_blocks(lines)
        edges = self._extract_edges(statements)
        yield from self._batch_data(edges, batch_size)

    def _read_lines(self, path: Path) -> Iterator[str]:
        with path.open(encoding="utf-8") as f:
            yield from f

    def _batch_data(self, data: Iterable, size: int) -> Iterator[tuple]:
        iterator = iter(data)
        while batch := tuple(islice(iterator, size)):
            yield batch

    def _yield_interconnect_blocks(self, lines: Iterator[str]) -> Iterator[str]:
        """Orchestrates the extraction of INTERCONNECT blocks."""
        ctx = _ParseContext()
        for line in lines:
            if self._should_process(line, ctx):
                ctx, blocks = self._process_line(line, ctx)
                yield from blocks

    def _should_process(self, line: str, ctx: _ParseContext) -> bool:
        return ctx.in_record or "(INTERCONNECT" in line

    def _process_line(
        self, line: str, ctx: _ParseContext
    ) -> tuple[_ParseContext, list[str]]:
        """Driver loop: Iterates through the line delegating segment processing."""
        extracted = []
        pos = 0
        while pos < len(line):
            ctx, pos, block = self._process_segment(line, pos, ctx)
            if block:
                extracted.append(block)
        return ctx, extracted

    def _process_segment(
        self, line: str, pos: int, ctx: _ParseContext
    ) -> tuple[_ParseContext, int, str | None]:
        """Delegates based on whether we are inside a record or looking for one."""
        if not ctx.in_record:
            return self._find_and_start_block(line, pos, ctx)
        return self._accumulate_block_content(line, pos, ctx)

    def _find_and_start_block(
        self, line: str, pos: int, ctx: _ParseContext
    ) -> tuple[_ParseContext, int, str | None]:
        """Seeks the start of a block. If found, initializes context and proceeds."""
        start = self._seek_start(line, pos)
        if start == -1:
            return ctx, len(line), None
        new_ctx = dataclasses.replace(ctx, in_record=True, balance=0)
        return self._accumulate_block_content(line, start, new_ctx)

    def _accumulate_block_content(
        self, line: str, pos: int, ctx: _ParseContext
    ) -> tuple[_ParseContext, int, str | None]:
        """Reads content until block ends or line ends."""
        chunk, bal, done = self._scan_block_end(line[pos:], ctx.balance)
        next_ctx = dataclasses.replace(ctx, buffer=ctx.buffer + (chunk,), balance=bal)
        if done:
            return _ParseContext(), pos + len(chunk), "".join(next_ctx.buffer)
        return next_ctx, pos + len(chunk), None

    def _seek_start(self, line: str, pos: int) -> int:
        return line.find("(INTERCONNECT", pos)

    def _scan_block_end(self, text: str, current_balance: int) -> tuple[str, int, bool]:
        """Scans text for parentheses balance."""
        is_finished: bool = False
        balance = current_balance
        for match in self._RE_PARENS.finditer(text):
            balance += 1 if match.group() == "(" else -1
            if balance == 0:
                is_finished = True
                return text[: match.end()], balance, is_finished
        return text, balance, is_finished

    def _extract_edges(self, statements: Iterator[str]) -> Iterator[Edge]:
        for stmt in statements:
            if match := self._RE_INTERCONNECT.search(stmt):
                src, dst, rise, fall = match.groups()
                yield Edge(src, dst, float(rise), float(fall))
