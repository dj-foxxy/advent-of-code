#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Final, Literal, final


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    return Arguments(part=args.part, input_path=args.input)


@final
class Node:
    def __init__(self, name: str) -> None:
        self.name: Final = name
        self.distances: Final[dict[Node, int]] = {}

    def __repr__(self) -> str:
        return f'Node({self.name!r})'

    def __str__(self) -> str:
        return self.name


def load_graph(path: Path) -> dict[str, Node]:
    nodes: dict[str, Node] = {}

    def get_node(name: str) -> Node:
        node = nodes.get(name)
        if node is None:
            nodes[name] = node = Node(name)
        return node

    with open(path) as file:
        for line in file:
            name_a, _, name_b, _, distance = line.split()
            node_a = get_node(name_a)
            node_b = get_node(name_b)
            node_a.distances[node_b] = node_b.distances[node_a] = int(distance)

    return nodes


def part_1(graph: dict[str, Node]) -> int:
    return min(
        sum(path[i - 1].distances[node] for i, node in enumerate(path[1:]))
        for path in permutations(graph.values())
    )


def part_2(graph: object) -> int:
    return 0


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_graph(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
