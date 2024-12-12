#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
import re
from typing import Final, Literal, Self, final, override


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-p', '--part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


type Result = int


@final
class Plot:
    def __init__(self, label: str, row: int, column: int) -> None:
        self.label: Final = label
        self.row: Final = row
        self.column: Final = column
        self.up: Plot | None = None
        self.down: Plot | None = None
        self.left: Plot | None = None
        self.right: Plot | None = None

    @override
    def __repr__(self) -> str:
        return str(self)

    @override
    def __str__(self) -> str:
        return self.label

    def corners(self) -> int:
        u = self.up
        d = self.down
        l = self.left
        r = self.right
        label = self.label
        corners = sum(
            (a is None or a.label != label) and (b is None or b.label != label)
            for a, b in ((u, r), (r, d), (d, l), (l, u))
        )

        for a, b, get_c in (
            (u, r, lambda u: u.right),
            (r, d, lambda r: r.down),
            (d, l, lambda d: d.left),
            (l, u, lambda l: l.up),
        ):
            if (
                a is not None
                and a.label == label
                and b is not None
                and b.label == label
                and ((c := get_c(a)) is None or c.label != label)
            ):
                corners += 1

        return corners

    def fences(self) -> int:
        return sum(
            side is None or side.label != self.label for side in self.sides()
        )

    def neighbors(self) -> list['Plot']:
        neighbors: list[Plot] = []
        for neighbor in self.sides():
            if neighbor is not None:
                neighbors.append(neighbor)
        return neighbors

    def sides(self) -> tuple['Plot | None', ...]:
        return (self.up, self.down, self.left, self.right)


@final
@dataclass(frozen=True, slots=True)
class Plots:
    grid: list[list[Plot]]
    width: int
    height: int


def load_input(path: Path) -> Plots:
    with open(path) as file:
        grid = [
            [
                Plot(label, row, column)
                for column, label in enumerate(line.rstrip())
            ]
            for row, line in enumerate(file)
        ]

    height = len(grid)
    width = len(grid[0])

    for r, row in enumerate(grid):
        for c, plot in enumerate(row):
            if r != 0:
                plot.up = grid[r - 1][c]
            if c != 0:
                plot.left = grid[r][c - 1]
            if r + 1 != height:
                plot.down = grid[r + 1][c]
            if c + 1 != width:
                plot.right = grid[r][c + 1]

    return Plots(grid, width, height)


def _find_region(plot: Plot, region: set[Plot]) -> None:
    region.add(plot)
    for neighbor in plot.neighbors():
        if neighbor.label == plot.label and neighbor not in region:
            _find_region(neighbor, region)


def find_region(plot: Plot) -> set[Plot]:
    region: set[Plot] = set()
    _find_region(plot, region)
    return region


def part_1(plots: Plots) -> Result:
    unseen = {plot for row in plots.grid for plot in row}
    cost = 0
    while unseen:
        region = find_region(unseen.pop())
        area = len(region)
        perimeter = sum(plot.fences() for plot in region)
        cost += area * perimeter
        unseen -= region
    return cost


def part_2(plots: Plots) -> Result:
    unseen = {plot for row in plots.grid for plot in row}
    cost = 0
    while unseen:
        region = find_region(unseen.pop())
        area = len(region)
        sides = sum(plot.corners() for plot in region)
        cost += area * sides
        unseen -= region
    return cost


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
