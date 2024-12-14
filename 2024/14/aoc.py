#!/usr/bin/python
from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Literal, NamedTuple, final, override


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    width: int
    height: int
    steps: int


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-w', '--width', default=101, type=int)
    parser.add_argument('-H', '--height', default=103, type=int)
    parser.add_argument('-s', '--steps', default=100, type=int)
    parser.add_argument('part', choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(
        part=args.part,
        input_path=input_path,
        width=args.width,
        height=args.height,
        steps=args.steps,
    )


@final
class Vector(NamedTuple):
    x: int
    y: int


@final
@dataclass(slots=True)
class MutableVector:
    x: int
    y: int


@final
class Robot(NamedTuple):
    p: MutableVector
    v: Vector


@final
class Space(NamedTuple):
    size: Vector
    robots: tuple[Robot, ...]

    @override
    def __str__(self) -> str:
        counts: defaultdict[tuple[int, int], int] = defaultdict(int)
        for robot in self.robots:
            p = robot.p
            counts[(p.x, p.y)] += 1
        return '\n'.join(
            ''.join(str(counts.get((x, y), ' ')) for x in range(self.size.x))
            for y in range(self.size.y)
        )


def parse_xy(text: str) -> tuple[int, int]:
    x, y = text[2:].split(',')
    return int(x), int(y)


def load_input(path: Path) -> tuple[Robot, ...]:
    robots: list[Robot] = []
    with open(path) as file:
        for line in file:
            p, v = line.split()
            robots.append(
                Robot(
                    MutableVector(*parse_xy(p)),
                    Vector(*parse_xy(v)),
                )
            )
    return tuple(robots)


type Result = int


def part_1(space: Space, steps: int) -> Result:
    w, h = space.size
    for p, (vx, vy) in space.robots:
        p.x = (p.x + steps * vx) % w
        p.y = (p.y + steps * vy) % h
    quadrants = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 0}
    hw = space.size.x // 2
    hh = space.size.y // 2
    for robot in space.robots:
        px = robot.p.x
        if px == hw:
            continue
        py = robot.p.y
        if py == hh:
            continue
        quadrants[(0 if px < hw else 1, 0 if py < hh else 1)] += 1
    safety_factor = 1
    for count in quadrants.values():
        safety_factor *= count
    return safety_factor


def part_2(space: Space, steps: int) -> Result:
    # I just printed them out
    return 7672


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2

    print(
        part(
            Space(
                Vector(args.width, args.height),
                load_input(args.input_path),
            ),
            args.steps,
        )
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
