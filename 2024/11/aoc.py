#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Literal


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    blinks: int


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-p', '--part', default=1, choices=(1, 2), type=int)
    parser.add_argument('-b', '--blinks', type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(
        part=args.part,
        input_path=input_path,
        blinks=25 if args.part == 1 else 75,
    )


def load_stones(path: Path) -> list[int]:
    return [int(stone) for stone in path.read_text().split()]


@cache
def stones_after_blinks(stone: int, blinks: int) -> int:
    if not blinks:
        return 1

    blinks -= 1

    if not stone:
        return stones_after_blinks(1, blinks)

    stone_str = str(stone)
    mid_point, remainder = divmod(len(stone_str), 2)
    if not remainder:
        a = stones_after_blinks(int(stone_str[:mid_point]), blinks)
        b = stones_after_blinks(int(stone_str[mid_point:]), blinks)
        return a + b

    return stones_after_blinks(2024 * stone, blinks)


def main() -> None:
    args = parse_args()
    print(
        sum(
            stones_after_blinks(stone, args.blinks)
            for stone in load_stones(args.input_path)
        )
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
