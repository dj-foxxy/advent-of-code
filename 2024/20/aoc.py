#!/usr/bin/python
from abc import ABC
from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum, auto, unique
from pathlib import Path
from typing import Final, Literal, final, override

from rich import print


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    min_saving: int


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-m', '--min-saving', default=100, type=int)
    parser.add_argument('part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(
        part=args.part, input_path=input_path, min_saving=args.min_saving
    )


@final
@unique
class Token(Enum):
    START = auto()
    TRACK = auto()
    END = auto()
    WALL = auto()


class Segment(ABC):
    def __init__(self, x: int, y: int, elapsed: int) -> None:
        self.x: Final = x
        self.y: Final = y
        self.elapsed: Final = elapsed


@final
class Start(Segment):
    def __init__(self, x: int, y: int, next: 'Track | End') -> None:
        super().__init__(x, y, 0)
        self.next: Final = next

    @override
    def __repr__(self) -> str:
        return f'S({self.elapsed})'

    __str__ = __repr__


@final
class Track(Segment):
    def __init__(
        self, x: int, y: int, elapsed: int, next: 'Track | End'
    ) -> None:
        super().__init__(x, y, elapsed)
        self.next: Final = next

    @override
    def __repr__(self) -> str:
        return f'T({self.elapsed})'

    __str__ = __repr__


@final
class End(Segment):
    @override
    def __repr__(self) -> str:
        return f'E({self.elapsed})'

    __str__ = __repr__


@final
@dataclass(slots=True)
class Course:
    segments: dict[tuple[int, int], Segment]
    coordinates: dict[Segment, tuple[int, int]] = field(init=False)
    start: Start

    def __post_init__(self) -> None:
        self.coordinates = {
            segment: xy for xy, segment in self.segments.items()
        }

    def __iter__(self) -> Iterator[Segment]:
        segment = self.start
        while True:
            yield segment
            if isinstance(segment, End):
                return
            segment = segment.next

    def find_skips(self, segment: Segment, radius: int) -> set[Segment]:
        radius += 1
        x, y = self.coordinates[segment]
        skips: set[Segment] = set()
        for dy in range(radius):
            for dx in range(radius - dy):
                distance = dy + dx
                if distance >= 2:
                    for x_sign, y_sign in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                        to_x = x + x_sign * dx
                        to_y = y + y_sign * dy
                        if (
                            (to := self.segments.get((to_x, to_y))) is not None
                            and to.elapsed > segment.elapsed
                            and to not in skips
                        ):
                            skips.add(to)
        return skips


def load_course(path: Path) -> Course:
    length = 0
    end_x: int | None = None
    end_y: int | None = None
    grid: list[list[Token]] = []
    with open(path) as file:
        for y, line in enumerate(file):
            row: list[Token] = []
            for x, c in enumerate(line):
                token: Token | None = None
                match c:
                    case 'S':
                        token = Token.START
                        length += 1
                    case '.':
                        token = Token.TRACK
                        length += 1
                    case 'E':
                        token = Token.END
                        end_x = x
                        end_y = y
                        length += 1
                    case '#':
                        token = Token.WALL
                    case '\n':
                        pass
                    case _:
                        raise ValueError(f'invalid cell: {c!r}')
                if token is not None:
                    row.append(token)
            grid.append(row)
    if end_x is None or end_y is None:
        raise ValueError('end not found')
    x = end_x
    y = end_y
    segment: Segment = End(x, y, length - 1)
    track: dict[tuple[int, int], Segment] = {(x, y): segment}

    def make_prev_segment(dx: int, dy: int) -> Segment | None:
        prev_x = x + dx
        prev_y = y + dy
        prev_xy = (prev_x, prev_y)
        if prev_xy in track:
            return None
        neighbor = grid[prev_y][prev_x]
        if neighbor == Token.WALL:
            return None
        if not isinstance(segment, (Track, End)):
            raise TypeError('wrong segment type as')
        if neighbor == Token.TRACK:
            return Track(prev_x, prev_y, segment.elapsed - 1, segment)
        if neighbor == Token.START:
            return Start(prev_x, prev_y, segment)

    start: Start | None = None
    while not isinstance(segment, Start):
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            if (prev_segment := make_prev_segment(dx, dy)) is not None:
                x += dx
                y += dy
                segment = prev_segment
                track[(segment.x, segment.y)] = segment
                if isinstance(segment, Start):
                    start = segment
                break
    if start is None:
        raise ValueError()
    return Course(track, start)


def count_savings(course: Course, radius: int) -> dict[int, int]:
    counts = defaultdict[int, int](int)
    for from_ in course:
        if isinstance(from_, (Start, Track)):
            for to in course.find_skips(from_, radius):
                saving = (
                    to.elapsed
                    - from_.elapsed
                    - abs(to.x - from_.x)
                    - abs(to.y - from_.y)
                )
                if saving >= 1:
                    counts[saving] += 1
    return dict(counts)


def count_savings_over_threshold(
    course: Course, radius: int, threshold: int
) -> int:
    return sum(
        count
        for saving, count in count_savings(course, radius).items()
        if saving >= threshold
    )


def part_1(course: Course, min_saving: int) -> int:
    return count_savings_over_threshold(course, 2, min_saving)


def part_2(course: Course, min_saving: int) -> int:
    return count_savings_over_threshold(course, 20, min_saving)


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_course(args.input_path), args.min_saving))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
