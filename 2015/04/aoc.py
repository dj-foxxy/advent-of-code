#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from hashlib import md5
from itertools import count
from pathlib import Path
from typing import Final, Literal, final


INPUT: Final = 'ckczppom'


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    return Arguments(part=args.part, input_path=args.input)


def find_n_leading_zeroes(key: bytes, n: int) -> int:
    prefix = '0' * n
    for i in count():
        result = md5(key + str(i).encode(), usedforsecurity=False)
        if result.hexdigest().startswith(prefix):
            return i
    raise AssertionError()


def part_1(key: bytes) -> int:
    return find_n_leading_zeroes(key, 5)


def part_2(key: bytes) -> int:
    return find_n_leading_zeroes(key, 6)


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(args.input_path.read_bytes().strip()))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
