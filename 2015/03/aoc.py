#!/usr/bin/env python
from argparse import ArgumentParser
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, final


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


type Moves = Iterator[tuple[int, int]]


def load_moves(path: Path) -> Moves:
    for token in path.read_text():
        match token:
            case '^':
                yield 0, -1
            case 'v':
                yield 0, 1
            case '>':
                yield 1, 0
            case '<':
                yield -1, 0


def find_visited(moves: Iterable[tuple[int, int]]) -> set[tuple[int, int]]:
    x = 0
    y = 0
    visited: set[tuple[int, int]] = {(x, y)}
    for dx, dy in moves:
        x += dx
        y += dy
        visited.add((x, y))
    return visited


def part_1(moves: Moves) -> int:
    return len(find_visited(moves))


def part_2(moves: Moves) -> int:
    moves_1 = []
    moves_2 = []
    for move in moves:
        moves_1.append(move)
        moves_1, moves_2 = moves_2, moves_1
    return len(find_visited(moves_1) | find_visited(moves_2))


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_moves(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
