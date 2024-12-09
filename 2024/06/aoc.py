#!/usr/bin/python
from argparse import ArgumentParser
from collections.abc import Iterator, MutableSequence, MutableSet, Sequence
from dataclasses import dataclass
from enum import Enum, auto, unique
from pathlib import Path
from typing import Final, Literal, final


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-p', '--part', default=1, choices=(1, 2), type=int)
    parser.add_argument('-i', '--input', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


type Grid = Sequence[MutableSequence[Cell]]


@final
@dataclass
class Facing:
    r: Literal[-1, 0, 1]
    c: Literal[-1, 0, 1]

    def __iter__(self) -> Iterator[Literal[-1, 0, 1]]:
        return iter((self.r, self.c))


NORTH: Final[Facing] = Facing(-1, 0)
EAST: Final[Facing] = Facing(0, 1)
SOUTH: Final[Facing] = Facing(1, 0)
WEST: Final[Facing] = Facing(0, -1)


@final
@unique
class FacingID(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()


def get_facing_id(facing: Facing) -> FacingID:
    print(facing, NORTH)
    if facing == NORTH:
        return FacingID.NORTH
    elif facing == EAST:
        return FacingID.EAST
    elif facing == SOUTH:
        return FacingID.SOUTH
    elif facing == WEST:
        return FacingID.WEST
    raise ValueError()


@final
@dataclass
class Guard:
    r: int
    c: int
    facing: Facing

    @property
    def facing_id(self) -> FacingID:
        print('L', self.facing)
        return get_facing_id(self.facing)


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class State:
    grid: Grid
    guard: Guard

    def print(self) -> None:
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                match cell:
                    case Cell.EMPTY:
                        if r == self.guard.r and c == self.guard.c:
                            facing = self.guard.facing
                            if facing == NORTH:
                                print('↑', end='')
                            elif facing == EAST:
                                print('→', end='')
                            elif facing == SOUTH:
                                print('↓', end='')
                            elif facing == WEST:
                                print('←', end='')
                        else:
                            print('·', end='')
                    case Cell.OBSTICAL:
                        print('#', end='')
                    case Cell.EXIT:
                        print('X', end='')
                    case Cell.FAKE_OBSTICAL:
                        print('O', end='')
            print()


type Result = int


@final
@unique
class Cell(Enum):
    EMPTY = auto()
    OBSTICAL = auto()
    EXIT = auto()
    FAKE_OBSTICAL = auto()


def load_input(path: Path) -> State:
    grid: list[list[Cell]] = []
    guard_r = guard_c = None
    with open(path) as file:
        for r, line in enumerate(file, start=1):
            row = [Cell.EXIT]
            for c, token in enumerate(line, start=1):
                match token:
                    case '.':
                        cell = Cell.EMPTY
                    case '#':
                        cell = Cell.OBSTICAL
                    case '^':
                        cell = Cell.EMPTY
                        guard_r = r
                        guard_c = c
                    case '\n':
                        continue
                    case _:
                        raise ValueError(f'invalid token: {token!r}')
                row.append(cell)
            row.append(Cell.EXIT)
            grid.append(row)

    def make_exit_row() -> list[Cell]:
        return [Cell.EXIT] * len(grid[0])

    grid.insert(0, make_exit_row())
    grid.append(make_exit_row())
    if guard_r is None or guard_c is None:
        raise ValueError('guard not found')
    return State(grid=grid, guard=Guard(guard_r, guard_c, Facing(-1, 0)))


def part_1(state: State) -> Result:
    grid = state.grid
    guard = state.guard
    facing_r, facing_c = guard.facing
    visited: set[tuple[int, int]] = {(guard.r, guard.c)}
    while True:
        next_guard_r = guard.r + facing_r
        next_guard_c = guard.c + facing_c
        cell = grid[next_guard_r][next_guard_c]
        if cell == Cell.OBSTICAL:
            match (facing_r, facing_c):
                case (-1, 0):
                    facing_r = 0
                    facing_c = 1
                case (0, 1):
                    facing_r = 1
                    facing_c = 0
                case (1, 0):
                    facing_r = 0
                    facing_c = -1
                case (0, -1):
                    facing_r = -1
                    facing_c = 0
                case _:
                    raise AssertionError()
        elif cell == Cell.EMPTY:
            guard.r = next_guard_r
            guard.c = next_guard_c
            visited.add((guard.r, guard.c))
        elif cell == Cell.EXIT:
            break
    return len(visited)


def is_loop(
    grid: Grid,
    gr: int,
    gc: int,
    fr: int,
    fc: int,
) -> bool:
    visited: MutableSet[tuple[int, int, int, int]] = {(gr, gc, fr, fc)}

    while True:
        ngr = gr + fr
        ngc = gc + fc
        cell = grid[ngr][ngc]
        if cell in {Cell.OBSTICAL, Cell.FAKE_OBSTICAL}:
            match (fr, fc):
                case (-1, 0):
                    fr = 0
                    fc = 1
                case (0, 1):
                    fr = 1
                    fc = 0
                case (1, 0):
                    fr = 0
                    fc = -1
                case (0, -1):
                    fr = -1
                    fc = 0
                case _:
                    raise AssertionError()
        elif cell == Cell.EMPTY:
            gr = ngr
            gc = ngc
            pose = (gr, gc, fr, fc)
            if pose in visited:
                return True
            visited.add(pose)
        elif cell == Cell.EXIT:
            return False


def part_2(state: State) -> Result:
    grid = state.grid
    guard = state.guard
    init_gr = gr = guard.r
    init_gc = gc = guard.c
    fr = guard.facing.r
    fc = guard.facing.c
    path: list[tuple[int, int, int, int]] = []

    def append_path() -> None:
        path.append((gr, gc, fr, fc))

    append_path()
    grid = state.grid

    first_turn = None

    while True:
        ngr = gr + fr
        ngc = gc + fc
        cell = grid[ngr][ngc]
        if cell == Cell.OBSTICAL:
            match (fr, fc):
                case (-1, 0):
                    fr = 0
                    fc = 1
                case (0, 1):
                    fr = 1
                    fc = 0
                case (1, 0):
                    fr = 0
                    fc = -1
                case (0, -1):
                    fr = -1
                    fc = 0
                case _:
                    raise AssertionError()
            if first_turn is None:
                first_turn = len(path)
        elif cell == Cell.EMPTY:
            gr = ngr
            gc = ngc
            append_path()
        elif cell == Cell.EXIT:
            break

    if first_turn is None:
        raise ValueError()

    obstical: MutableSet[tuple[int, int]] = set()

    for i, (gr, gc, fr, fc) in enumerate(path[first_turn:]):
        print(i + 1, len(path), len(obstical))
        ngr = gr + fr
        ngc = gc + fc
        cell = grid[ngr][ngc]
        if cell in {Cell.OBSTICAL, Cell.EXIT} or (ngr, ngc) in obstical:
            continue
        grid[ngr][ngc] = Cell.FAKE_OBSTICAL
        if is_loop(grid, init_gr, init_gc, -1, 0):
            obstical.add((ngr, ngc))
        grid[ngr][ngc] = Cell.EMPTY

    return len(obstical)


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
