#!/usr/bin/env python
from argparse import ArgumentParser
from collections.abc import Mapping
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Final, Literal, final


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


DETECTIONS: Final[Mapping[str, int]] = {
    'children': 3,
    'cats': 7,
    'samoyeds': 2,
    'pomeranians': 3,
    'akitas': 0,
    'vizslas': 0,
    'goldfish': 5,
    'trees': 3,
    'cars': 2,
    'perfumes': 1,
}


@dataclass(frozen=True, slots=True)
class Sue:
    number: int
    props: dict[str, int]


def load_input(path: Path) -> list[Sue]:
    sues: list[Sue] = []
    with open(path) as file:
        for line in file:
            head, tail = line.split(':', maxsplit=1)
            number = int(head.split()[1])
            props: dict[str, int] = {}
            for prop_str in tail.split(','):
                name, value_str = prop_str.split(':')
                props[name.strip()] = int(value_str)
            sues.append(Sue(number, props))
    return sues


def part_1(sues: list[Sue]) -> int:
    for sue in sues:
        if all(
            sue.props.get(name, value) == value
            for name, value in DETECTIONS.items()
        ):
            return sue.number
    raise ValueError()


def _detection_subset(*keys: str) -> Mapping[str, int]:
    return {key: DETECTIONS[key] for key in keys}


EQ_DETECTIONS: Final = _detection_subset(
    'children',
    'samoyeds',
    'akitas',
    'vizslas',
    'cars',
    'perfumes',
)

GT_DETECTIONS: Final = _detection_subset(
    'cats',
    'trees',
)

LT_DETECTIONS: Final = _detection_subset(
    'pomeranians',
    'goldfish',
)


def part_2_match(sue: Sue) -> bool:
    return (
        all(
            sue.props.get(key, value) == value
            for key, value in EQ_DETECTIONS.items()
        )
        and all(
            sue.props.get(key, math.inf) > value
            for key, value in GT_DETECTIONS.items()
        )
        and all(
            sue.props.get(key, -1) < value
            for key, value in LT_DETECTIONS.items()
        )
    )


def part_2(sues: list[Sue]) -> int:
    for sue in sues:
        if part_2_match(sue):
            return sue.number
    raise ValueError()


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
