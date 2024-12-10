#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Iterable, Literal, final


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


def part_1(path: Path) -> Result:
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


@final
@dataclass(kw_only=True, slots=True)
class Span:
    start: int
    length: int
    file_id: int | None = None

    @property
    def is_file(self) -> bool:
        return self.file_id is not None

    @property
    def is_free(self) -> bool:
        return self.file_id is None


def print_disk_p2(disk: Iterable[Span]) -> None:
    disk = sorted(
        (span for span in disk if span.length),
        key=lambda span: span.start,
    )
    for span in disk:
        token = str(span.file_id) if span.is_file else '.'
        print(token * span.length, end='')
    print()


def part_2(path: Path) -> Result:
    file_id = iter(count())
    disk: list[Span] = []
    files: list[Span] = []
    frees: list[Span] = []
    start = 0
    is_file = True
    for length in map(int, path.read_text().rstrip()):
        span = Span(
            start=start,
            length=length,
            file_id=next(file_id) if is_file else None,
        )
        disk.append(span)
        (files if is_file else frees).append(span)
        start += length
        is_file = not is_file
    files.reverse()
    for file in files:
        for free in frees:
            if free.start < file.start and free.length >= file.length:
                span = Span(start=file.start, length=file.length)
                frees.append(span)
                disk.append(span)
                file.start = free.start
                free.start += file.length
                free.length -= file.length
                frees.sort(key=lambda span: span.start)
                break
    disk = sorted(
        (span for span in disk if span.length),
        key=lambda span: span.start,
    )
    i = 0
    checksum = 0
    for span in disk:
        if span.file_id is not None:
            for i in range(i, i + span.length):
                checksum += i * span.file_id
            i += 1
        else:
            i += span.length
    return checksum


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(args.input_path))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
