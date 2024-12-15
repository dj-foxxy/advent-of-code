#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

verbose = False


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    steps: int
    verbose: bool


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-s', '--steps', default=100, type=int)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(
        part=args.part,
        input_path=input_path,
        steps=args.steps,
        verbose=args.verbose,
    )


type Lights = tuple[list[bool], ...]


def print_lights(lights: Lights) -> None:
    for row in lights:
        for light in row:
            print('#' if light else '.', end='')
        print()


def load_lights(path: Path) -> Lights:
    with open(path) as file:
        return tuple([token == '#' for token in line.rstrip()] for line in file)


def copy_lights(lights: Lights) -> Lights:
    return tuple([light for light in row] for row in lights)


type Result = int


def is_neighbor_on(
    lights: Lights,
    x: int,
    y: int,
    dx: int = 0,
    dy: int = 0,
) -> bool:
    y += dy

    if y < 0 or y >= len(lights):
        return False

    x += dx
    row = lights[y]

    return 0 <= x < len(row) and row[x]


def count_neighors_on(lights: Lights, x: int, y: int) -> int:
    return sum(
        is_neighbor_on(lights, x, y, dx, dy)
        for dx, dy in (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        )
    )


def run(lights: Lights, steps: int, corners_on: bool = False) -> Result:
    a = lights
    b = copy_lights(lights)
    del lights
    if corners_on:
        a[0][0] = a[0][-1] = a[-1][0] = a[-1][-1] = True
    if verbose:
        print_lights(a)
    for i in range(steps):
        for y, row in enumerate(a):
            for x, light in enumerate(row):
                neighors_on = count_neighors_on(a, x, y)
                if light:
                    b[y][x] = neighors_on == 2 or neighors_on == 3
                else:
                    b[y][x] = neighors_on == 3
        a, b = b, a
        if corners_on:
            a[0][0] = a[0][-1] = a[-1][0] = a[-1][-1] = True
        if verbose:
            print()
            print('Step', i + 1)
            print_lights(a)
    return sum(light for row in a for light in row)


def part_1(lights: Lights, steps: int) -> Result:
    return run(lights, steps)


def part_2(lights: Lights, steps: int) -> Result:
    return run(lights, steps, corners_on=True)


def main() -> None:
    global verbose
    args = parse_args()
    verbose = args.verbose
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_lights(args.input_path), args.steps))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
