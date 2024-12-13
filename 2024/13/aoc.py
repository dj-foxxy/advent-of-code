#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Final, Literal, NamedTuple, final, override


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


@final
class Point(NamedTuple):
    x: int
    y: int

    @override
    def __str__(self) -> str:
        return f'({self.x}, {self.y})'


@final
class Machine(NamedTuple):
    a: Point
    b: Point
    p: Point

    @override
    def __str__(self) -> str:
        return f'({self.a}, {self.b}, {self.p})'


type Machines = tuple[Machine, ...]


machine_pattern: Final = re.compile(
    r"""
        Button[ ]A:[ ]X\+([1-9][0-9]*),[ ]Y\+([1-9][0-9]*)\n
        Button[ ]B:[ ]X\+([1-9][0-9]*),[ ]Y\+([1-9][0-9]*)\n
        Prize:[ ]X=([1-9][0-9]*),[ ]Y=([1-9][0-9]*)\n+
    """,
    flags=re.VERBOSE,
)


def load_machines(path: Path) -> Machines:
    machines: list[Machine] = []
    for match in machine_pattern.finditer(path.read_text()):
        ax, ay, bx, by, px, py = map(int, match.groups())
        machines.append(Machine(Point(ax, ay), Point(bx, by), Point(px, py)))
    return tuple(machines)


type Result = int


def find_min_tokens_for_machine(machine: Machine, offset: int) -> int | None:
    (dx1, dy1), (dx2, dy2), (x1, y) = machine
    x1 += offset
    y += offset
    r = dy2 / dx2
    dx3 = dx1 * r
    x2 = x1 * r
    a = round((x2 - y) / (dx3 - dy1))
    b = round((x1 - (dx1 * a)) / dx2)
    if (dx1 * a + dx2 * b) == x1 and (dy1 * a + dy2 * b) == y:
        return a * 3 + b


def find_min_tokens(machines: Machines, offset: int = 0) -> int:
    def find(machine: Machine) -> int | None:
        return find_min_tokens_for_machine(machine, offset)

    return sum(tokens for tokens in map(find, machines) if tokens is not None)


def part_1(machines: Machines) -> Result:
    return find_min_tokens(machines, 0)


def part_2(machines: Machines) -> Result:
    return find_min_tokens(machines, 10000000000000)


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_machines(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
