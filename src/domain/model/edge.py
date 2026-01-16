from dataclasses import dataclass


@dataclass(frozen=True)
class Edge:
    """Represents a connection between nodes with delay information."""

    src_node: str
    dst_node: str
    delay_rise: float = 0.0
    delay_fall: float = 0.0
