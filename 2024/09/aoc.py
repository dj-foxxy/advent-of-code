#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


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


type Disk = list[int]

type Result = int


def load_input(path: Path) -> Disk:
    is_file = True
    file_id = 0
    disk: list[int] = []
    for token in map(int, path.read_text().rstrip()):
        if is_file:
            sector = file_id
            file_id += 1
        else:
            sector = -1
        for _ in range(token):
            disk.append(sector)
        is_file = not is_file
    return disk


def print_disk(disk: Disk) -> None:
    for sector in disk:
        print('.' if sector == -1 else chr(ord('0') + sector), end='')
    print()


def part_1(disk: Disk) -> Result:
    i = 0
    j = len(disk) - 1
    while True:
        while disk[i] != -1:
            i += 1
        while disk[j] == -1:
            j -= 1
        if i >= j:
            break
        disk[i], disk[j] = disk[j], disk[i]
    return sum(i * sector for i, sector in enumerate(disk) if sector != -1)


def part_2(input: Disk) -> Result:
    return 0


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
