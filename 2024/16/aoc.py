#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass, field
from enum import Enum, auto, unique
import heapq
from math import inf
from pathlib import Path
from typing import ClassVar, Final, Literal, final, override


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


@final
@unique
class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    @override
    def __str__(self) -> str:
        match self:
            case Direction.UP:
                return '↑'
            case Direction.DOWN:
                return '↓'
            case Direction.LEFT:
                return '←'
            case Direction.RIGHT:
                return '→'

    def turns(self, other: 'Direction') -> int:
        match self:
            case Direction.UP:
                match other:
                    case Direction.UP:
                        return 0
                    case Direction.LEFT | Direction.RIGHT:
                        return 1
                    case Direction.DOWN:
                        return 2
            case Direction.DOWN:
                match other:
                    case Direction.DOWN:
                        return 0
                    case Direction.LEFT | Direction.RIGHT:
                        return 1
                    case Direction.UP:
                        return 2
            case Direction.LEFT:
                match other:
                    case Direction.LEFT:
                        return 0
                    case Direction.UP | Direction.DOWN:
                        return 1
                    case Direction.RIGHT:
                        return 2
            case Direction.RIGHT:
                match other:
                    case Direction.RIGHT:
                        return 0
                    case Direction.UP | Direction.DOWN:
                        return 1
                    case Direction.LEFT:
                        return 2


@final
class Leave:
    __slots__: ClassVar = ('tile', 'cost')

    def __init__(self, tile: 'Tile', cost: int) -> None:
        self.tile: Final = tile
        self.cost: Final = cost


class Tile:
    __slots__: ClassVar = ('x', 'y', 'enter')

    def __init__(self, x: int, y: int) -> None:
        self.x: Final = x
        self.y: Final = y
        self.enter: Final[dict[Direction, dict[Direction, Leave]]] = {}

    @override
    def __str__(self) -> str:
        lines = [f'({self.x}, {self.y})']
        for facing, leaves in self.enter.items():
            for direction, leave in leaves.items():
                lines.append(
                    f'  {facing}, {direction}, ({leave.tile.x}, {leave.tile.y}), {leave.cost}'
                )
        return '\n'.join(lines)


@final
class StartTile(Tile):
    pass


@final
class PathTile(Tile):
    pass


@final
class EndTile(Tile):
    pass


type Grid = list[list[Tile | None]]


def print_grid(grid: Grid) -> None:
    for row in grid:
        for tile in row:
            match tile:
                case StartTile():
                    print('S', end='')
                case PathTile():
                    print('.', end='')
                case EndTile():
                    print('E', end='')
                case None:
                    print('#', end='')
                case _:
                    raise ValueError()
        print()


@dataclass(frozen=True, slots=True)
class Input:
    grid: Grid
    start: StartTile
    end: EndTile

    def print_grid(self) -> None:
        print_grid(self.grid)


def link_tiles(
    tile: Tile,
    facing: Direction,
    to_tile: Tile,
    direction: Direction,
) -> None:
    enter = tile.enter.get(facing)
    if enter is None:
        tile.enter[facing] = enter = {}
    turns = facing.turns(direction)
    enter[direction] = Leave(to_tile, 1 + 1000 * turns)


def load_input(path: Path) -> Input:
    grid: list[list[Tile | None]] = []
    start: StartTile | None = None
    end: EndTile | None = None
    with open(path) as file:
        for y, line in enumerate(file):
            row: list[Tile | None] = []
            for x, token in enumerate(line):
                match token:
                    case 'S':
                        start = node = StartTile(x, y)
                    case '.':
                        node = PathTile(x, y)
                    case 'E':
                        end = node = EndTile(x, y)
                    case '#':
                        node = None
                    case '\n':
                        continue
                    case _:
                        raise ValueError()
                row.append(node)
            grid.append(row)
    if start is None or end is None:
        raise ValueError()
    for row in grid:
        for tile in row:
            if tile is None:
                continue
            up = grid[tile.y - 1][tile.x]
            down = grid[tile.y + 1][tile.x]
            left = grid[tile.y][tile.x - 1]
            right = grid[tile.y][tile.x + 1]
            if up:
                facing = Direction.DOWN
                link_tiles(tile, facing, up, Direction.UP)
                if down:
                    link_tiles(tile, facing, down, Direction.DOWN)
                if left:
                    link_tiles(tile, facing, left, Direction.LEFT)
                if right:
                    link_tiles(tile, facing, right, Direction.RIGHT)
            if down:
                facing = Direction.UP
                link_tiles(tile, facing, down, Direction.DOWN)
                if up:
                    link_tiles(tile, facing, up, Direction.UP)
                if left:
                    link_tiles(tile, facing, left, Direction.LEFT)
                if right:
                    link_tiles(tile, facing, right, Direction.RIGHT)
            if left:
                facing = Direction.RIGHT
                link_tiles(tile, facing, left, Direction.LEFT)
                if up:
                    link_tiles(tile, facing, up, Direction.UP)
                if down:
                    link_tiles(tile, facing, down, Direction.DOWN)
                if right:
                    link_tiles(tile, facing, right, Direction.RIGHT)
            if right:
                facing = Direction.LEFT
                link_tiles(tile, facing, right, Direction.RIGHT)
                if up:
                    link_tiles(tile, facing, up, Direction.UP)
                if down:
                    link_tiles(tile, facing, down, Direction.DOWN)
                if left:
                    link_tiles(tile, facing, left, Direction.LEFT)
                    continue
    up = grid[start.y - 1][start.x]
    down = grid[start.y + 1][start.x]
    left = grid[start.y][start.x - 1]
    right = grid[start.y][start.x + 1]
    if up:
        link_tiles(start, Direction.RIGHT, up, Direction.UP)
    if down:
        link_tiles(start, Direction.RIGHT, down, Direction.DOWN)
    if left:
        link_tiles(start, Direction.RIGHT, left, Direction.LEFT)
    if right:
        link_tiles(start, Direction.RIGHT, right, Direction.RIGHT)
    return Input(grid, start, end)


@final
@dataclass(order=True)
class HeapItem:
    tile: Final[Tile] = field(compare=False)
    facing: Final[Direction] = field(compare=False)
    cost: Final[float] = inf
    is_dead: bool = field(default=False, compare=False)


def compute_costs(input: Input) -> dict[tuple[Tile, Direction], float]:
    heap: list[HeapItem] = []
    items: dict[tuple[Tile, Direction], HeapItem] = {}

    for row in input.grid:
        for tile in row:
            if tile is not None:
                for facing in tile.enter:
                    item = HeapItem(tile, facing)
                    heapq.heappush(heap, item)
                    items[(tile, facing)] = item

    def pop() -> HeapItem | None:
        while heap:
            item = heapq.heappop(heap)
            if not item.is_dead:
                return item

    def update(tile: Tile, facing: Direction, cost: float) -> None:
        key = (tile, facing)
        items[key].is_dead = True
        item = HeapItem(tile, facing, cost=cost)
        heapq.heappush(heap, item)
        items[key] = item

    update(input.start, Direction.RIGHT, 0)

    for item in iter(pop, None):
        tile = item.tile
        facing = item.facing
        cost = item.cost
        for direction, leave in tile.enter[facing].items():
            next_cost = cost + leave.cost
            if next_cost < items[(leave.tile, direction)].cost:
                update(leave.tile, direction, next_cost)

    return {tf: i.cost for tf, i in items.items()}


def part_1(input: Input) -> int:
    costs = compute_costs(input)
    cost = min(costs[(input.end, facing)] for facing in input.end.enter)
    return int(cost)


def find_shortest_path_tiles(
    start_tile: Tile,
    start_facing: Direction,
    end_tile: Tile,
    costs: dict[tuple[Tile, Direction], float],
):
    end_cost = min(costs[(end_tile, facing)] for facing in end_tile.enter)
    end_facings = frozenset(
        facing
        for facing in end_tile.enter
        if costs[(end_tile, facing)] == end_cost
    )
    path: set[Tile] = set()

    def find(tile: Tile, facing: Direction, cost: float):
        if cost != costs[(tile, facing)]:
            return False

        if tile == end_tile and facing in end_facings:
            path.add(tile)
            return True

        in_path = False

        for direction, leave in tile.enter[facing].items():
            next_cost = cost + leave.cost

            if next_cost == costs[(leave.tile, direction)] and find(
                leave.tile, direction, next_cost
            ):
                path.add(tile)
                in_path = True

        return in_path

    find(start_tile, start_facing, 0)
    assert start_tile in path
    assert end_tile in path
    return path


def part_2(input: Input) -> int:
    return len(
        find_shortest_path_tiles(
            input.start,
            Direction.RIGHT,
            input.end,
            compute_costs(input),
        )
    )


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
