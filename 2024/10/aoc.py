#!/usr/bin/python
from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Set
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, Literal, cast, final, override


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


type Height = Literal[-2, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

heights: Final[Set[Height]] = {-2, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9}


@final
class Cell:
    __slots__: ClassVar = ('height', 'neighors')

    def __init__(self, height: Height) -> None:
        self.height: Final = height
        self.neighors: Final[list[Cell]] = []

    @override
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.height})'

    @override
    def __str__(self) -> str:
        return str(self.height)


type Cells = tuple[Cell, ...]


def load_input(path: Path) -> Cells:
    grid: list[list[Cell]] = []
    with open(path) as file:
        for line in file:
            row: list[Cell] = []
            for token in line.rstrip():
                height = -2 if token == '.' else int(token)
                if height not in heights:
                    raise ValueError()
                row.append(Cell(cast(Height, height)))
            grid.append(row)
    rows = len(grid)
    cols = len(grid[0])
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if r > 0:
                cell.neighors.append(grid[r - 1][c])
            if c > 0:
                cell.neighors.append(grid[r][c - 1])
            if r < rows - 1:
                cell.neighors.append(grid[r + 1][c])
            if c < cols - 1:
                cell.neighors.append(grid[r][c + 1])
    return tuple(cell for row in grid for cell in row)


type Result = int


def count_peaks(cell: Cell) -> int:
    frontier = [cell]
    seen: set[Cell] = {cell}
    peaks = 0
    while frontier:
        cell = frontier.pop()
        if cell.height == 9:
            peaks += 1
        for neighor in cell.neighors:
            if neighor not in seen and neighor.height == cell.height + 1:
                frontier.append(neighor)
                seen.add(neighor)
    return peaks


def part_1(cells: Cells) -> Result:
    return sum(count_peaks(cell) for cell in cells if not cell.height)


def rate_trails(cell: Cell) -> int:
    frontier = [cell]
    seen: set[Cell] = {cell}
    ratings: dict[Cell, int] = defaultdict(int)
    ratings[cell] = 1
    rating = 0
    while frontier:
        cell = frontier.pop(0)
        if cell.height == 9:
            rating += ratings[cell]
            continue
        for neighor in cell.neighors:
            if neighor.height == cell.height + 1:
                ratings[neighor] += ratings[cell]
                if neighor not in seen:
                    frontier.append(neighor)
                    seen.add(neighor)
    return rating


def part_2(cells: Cells) -> Result:
    return sum(rate_trails(cell) for cell in cells if not cell.height)


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
