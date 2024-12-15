#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum, auto, unique
from pathlib import Path
from typing import Final, Literal, NamedTuple, final

verbose = False


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    verbose: bool


def parse_args() -> Arguments:
    parser = ArgumentParser()
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
        verbose=args.verbose,
    )


@final
@unique
class Cell(Enum):
    EMPTY = auto()
    ROBOT = auto()
    BOX = auto()
    LEFT_SIDE = auto()
    RIGHT_SIDE = auto()
    WALL = auto()


type Grid = list[list[Cell]]


def print_grid(grid: Grid) -> None:
    for row in grid:
        for cell in row:
            match cell:
                case Cell.EMPTY:
                    c = '.'
                case Cell.ROBOT:
                    c = '@'
                case Cell.BOX:
                    c = 'O'
                case Cell.LEFT_SIDE:
                    c = '['
                case Cell.RIGHT_SIDE:
                    c = ']'
                case Cell.WALL:
                    c = '#'
            print(c, end='')
        print()


@final
class Location(NamedTuple):
    x: int
    y: int


@final
@unique
class Move(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


@final
@dataclass(frozen=True, slots=True)
class Input:
    grid: Grid
    moves: list[Move]
    robot: Location

    def print_grid(self) -> None:
        print_grid(self.grid)


def load_input(path: Path, large: bool = False) -> Input:
    grid_text, moves_text = path.read_text().split('\n\n', maxsplit=1)
    grid: Grid = []
    robot_x: int | None = None
    robot_y: int | None = None
    for y, line in enumerate(grid_text.splitlines()):
        row: list[Cell] = []
        for x, token in enumerate(line):
            match token:
                case '.':
                    cells = (Cell.EMPTY, Cell.EMPTY) if large else (Cell.EMPTY,)
                case '@':
                    cells = (Cell.ROBOT, Cell.EMPTY) if large else (Cell.ROBOT,)
                    robot_x = (2 if large else 1) * x
                    robot_y = y
                case 'O':
                    if large:
                        cells = (Cell.LEFT_SIDE, Cell.RIGHT_SIDE)
                    else:
                        cells = (Cell.BOX,)
                case '#':
                    cells = (Cell.WALL, Cell.WALL) if large else (Cell.WALL,)
                case _:
                    raise ValueError()
            row.extend(cells)
        grid.append(row)
    if robot_x is None or robot_y is None:
        raise ValueError()
    moves: list[Move] = []
    for token in moves_text:
        match token:
            case '^':
                move = Move.UP
            case 'v':
                move = Move.DOWN
            case '<':
                move = Move.LEFT
            case '>':
                move = Move.RIGHT
            case '\n':
                continue
            case _:
                raise ValueError()
        moves.append(move)
    return Input(grid, moves, Location(robot_x, robot_y))


type Result = int


def is_move_feasible(
    grid: list[list[Cell]],
    x: int,
    y: int,
    dx: int,
    dy: int,
    is_other_side: bool = False,
) -> bool:
    dst_y = y + dy
    dst_x = x + dx

    if verbose:
        print(
            f'({x}, {y}, {grid[y][x]}, {is_other_side}) -> ({dst_x}, {dst_y}, {grid[dst_y][dst_x].name})'
        )

    if not is_other_side:
        match grid[y][x]:
            case Cell.LEFT_SIDE:
                if not is_move_feasible(
                    grid, x + 1, y, dx, dy, is_other_side=True
                ):
                    return False
                if dx == 1:
                    return True
            case Cell.RIGHT_SIDE:
                if not is_move_feasible(
                    grid, x - 1, y, dx, dy, is_other_side=True
                ):
                    return False
                if dx == -1:
                    return True

    match grid[dst_y][dst_x]:
        case Cell.EMPTY:
            return True
        case Cell.BOX | Cell.LEFT_SIDE | Cell.RIGHT_SIDE:
            return is_move_feasible(grid, dst_x, dst_y, dx, dy)
        case Cell.ROBOT:
            raise ValueError()
        case Cell.WALL:
            return False


def move_by(grid: Grid, x: int, y: int, dx: int, dy: int) -> None:
    dst_y = y + dy
    dst_x = x + dx
    dst_cell = grid[dst_y][dst_x]

    def swap() -> None:
        grid[dst_y][dst_x], grid[y][x] = grid[y][x], Cell.EMPTY

    match dst_cell:
        case Cell.EMPTY:
            swap()
        case Cell.BOX:
            move_by(grid, dst_x, dst_y, dx, dy)
            swap()
        case Cell.LEFT_SIDE:
            if dy:
                move_by(grid, dst_x + 1, dst_y, dx, dy)
            move_by(grid, dst_x, dst_y, dx, dy)
            swap()
        case Cell.RIGHT_SIDE:
            if dy:
                move_by(grid, dst_x - 1, dst_y, dx, dy)
            move_by(grid, dst_x, dst_y, dx, dy)
            swap()
        case Cell.ROBOT | Cell.WALL:
            raise ValueError(f'Cannot move {dst_cell}')


def make_try_move(dx: int = 0, dy: int = 0):
    def try_move(grid: list[list[Cell]], x: int, y: int) -> Location:
        if is_move_feasible(grid, x, y, dx, dy):
            move_by(grid, x, y, dx, dy)
            return Location(x + dx, y + dy)
        else:
            return Location(x, y)

    return try_move


try_move_up: Final = make_try_move(dy=-1)
try_move_down: Final = make_try_move(dy=1)
try_move_left: Final = make_try_move(dx=-1)
try_move_right: Final = make_try_move(dx=1)


def move_robot(grid: Grid, robot: Location, move: Move) -> Location:
    match move:
        case Move.UP:
            try_move = try_move_up
        case Move.DOWN:
            try_move = try_move_down
        case Move.LEFT:
            try_move = try_move_left
        case Move.RIGHT:
            try_move = try_move_right
    return try_move(grid, robot.x, robot.y)


def sum_box_gps_coordinates(grid: Grid) -> int:
    return sum(
        100 * y + x
        for y, row in enumerate(grid)
        for x, cell in enumerate(row)
        if cell in {Cell.BOX, Cell.LEFT_SIDE}
    )


def part_1(input: Input) -> Result:
    if verbose:
        input.print_grid()
    robot = input.robot
    for move in input.moves:
        if verbose:
            print()
            print(move.name, end=' ')
        robot = move_robot(input.grid, robot, move)
        if verbose:
            print(robot)
            input.print_grid()
    return sum_box_gps_coordinates(input.grid)


def part_2(input: Input) -> Result:
    return part_1(input)


def main() -> None:
    global verbose
    args = parse_args()
    verbose = args.verbose
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_input(args.input_path, large=args.part == 2)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
