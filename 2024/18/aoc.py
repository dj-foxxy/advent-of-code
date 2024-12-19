#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass, field
import heapq
from pathlib import Path
from typing import Final, Literal, final

from rich import print


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    count: int
    size: int


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-c', '--count', default=1024, type=int)
    parser.add_argument('-s', '--size', default=70, type=int)
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
        count=args.count,
        size=args.size,
    )


type Input = tuple[tuple[int, int], ...]


def parse_line(line) -> tuple[int, int]:
    x, y = line.rstrip().split(',')
    return int(x), int(y)


def load_input(path: Path) -> Input:
    with open(path) as file:
        return tuple(parse_line(line) for line in file)


@final
@dataclass(order=True, slots=True)
class Item:
    x: Final[int] = field(compare=False)
    y: Final[int] = field(compare=False)
    distance: int
    alive: bool = field(default=True, compare=True)


def find_path_length(size: int, obsticals: frozenset[tuple[int, int]]) -> int:
    heap: list[Item] = []
    items: dict[tuple[int, int], Item] = {}

    def push(x: int, y: int, distance: int) -> Item:
        item = Item(x, y, distance)
        heapq.heappush(heap, item)
        items[(x, y)] = item
        return item

    def pop() -> Item | None:
        while heap:
            item = heapq.heappop(heap)
            if item.alive:
                return item

    def update(x: int, y: int, distance: int) -> None:
        xy = (x, y)
        items[xy].alive = False
        item = Item(x, y, distance)
        heapq.heappush(heap, item)
        items[xy] = item

    push(0, 0, 0)

    while (item := pop()) is not None:
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            x = item.x + dx
            if x < 0 or x > size:
                continue
            y = item.y + dy
            if y < 0 or y > size:
                continue
            xy = (x, y)
            if xy in obsticals:
                continue
            neighbor = items.get(xy)
            distance = item.distance + 1
            if neighbor is None:
                push(x, y, distance)
            elif distance < neighbor.distance:
                update(x, y, distance)

    return items[(size, size)].distance


def part_1(input: Input, count: int, size: int) -> int:
    return find_path_length(size, frozenset(input[:count]))


def part_2(input: Input, size: int) -> str:
    for i in range(len(input)):
        obsticals = frozenset(input[:i])
        try:
            find_path_length(size, obsticals)
        except KeyError:
            return ','.join(map(str, input[i - 1]))
    raise ValueError()


def main() -> None:
    args = parse_args()
    input = load_input(args.input_path)
    match args.part:
        case 1:
            result = part_1(input, args.count, args.size)
        case 2:
            result = part_2(input, args.size)
    print(result)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
