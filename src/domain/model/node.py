from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    """Represents a node (pin or port) in the verilog."""

    name: str
