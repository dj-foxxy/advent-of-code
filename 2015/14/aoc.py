#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, final


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    duration: int


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=Path)
    parser.add_argument('-d', '--duration', default=2503, type=int)
    args = parser.parse_args()
    return Arguments(
        part=args.part,
        input_path=args.input,
        duration=int(args.duration),
    )


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Reindeer:
    name: str
    fly_speed: int
    fly_duration: int
    rest_duration: int


def load_reindeers(path: Path) -> list[Reindeer]:
    with open(path) as file:
        return [
            Reindeer(
                name=tokens[0],
                fly_speed=int(tokens[3]),
                fly_duration=int(tokens[6]),
                rest_duration=int(tokens[13]),
            )
            for tokens in map(str.split, file)
        ]


def caculate_distance(reindeer: Reindeer, duration: int) -> int:
    period = reindeer.fly_duration + reindeer.rest_duration
    cycles, remainder = divmod(duration, period)
    return reindeer.fly_speed * (
        cycles * reindeer.fly_duration + min(remainder, reindeer.fly_duration)
    )


def part_1(reindeers: list[Reindeer], duration: int) -> int:
    return max(caculate_distance(reindeer, duration) for reindeer in reindeers)


def part_2(reindeers: list[Reindeer], duration: int) -> int:
    return 0


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_reindeers(args.input_path), args.duration))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
