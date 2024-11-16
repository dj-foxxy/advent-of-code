#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NamedTuple, final


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
class Tile(NamedTuple):
    x: int
    y: int


@final
class Edge(NamedTuple):
    a: Tile
    b: Tile

from networkx import Graph, all_pairs_dijkstra_path_length, all_shortest_paths, single_source_dijkstra


def load_input(path: Path):
    graph: Graph[Tile] = Graph()
    x = -1
    y = -1

    def add_pipe(dx=0, dy=0) -> None:
        graph.add_edge(Tile(x, y), Tile(x + dx, y + dy))

    start: None | Tile = None

    with open(path) as file:
        for y, line in enumerate(file):
            for x, tile in enumerate(line):
                match tile:
                    case '|':
                        add_pipe(dy=-1)
                        add_pipe(dy=1)
                    case '-':
                        add_pipe(dx=-1)
                        add_pipe(dx=1)
                    case 'L':
                        add_pipe(dy=-1)
                        add_pipe(dx=1)
                    case 'J':
                        add_pipe(dy=-1)
                        add_pipe(dx=-1)
                    case '7':
                        add_pipe(dx=-1)
                        add_pipe(dy=1)
                    case 'F':
                        add_pipe(dx=1)
                        add_pipe(dy=1)
                    case 'S':
                        start = Tile(x, y)
                    case '.' | '\n':
                        pass
                    case _:
                        raise ValueError(f'invalid tile {tile!r}')
    if start is None:
        raise ValueError('start not found')


    lengths = single_source_dijkstra(graph, start)[0]
    result = max(lengths, key=lambda t: lengths[t])
    print(lengths[result])



    print(graph)


def part_1(input: list[list[int]]) -> int:
    return 0


def part_2(input: list[list[int]]) -> int:
    return 0


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_input(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
