#!/usr/bin/env python
from argparse import ArgumentParser
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, final


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input: list[int]


def parse_input(text: str) -> list[int]:
    return [int(digit) for digit in text]


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('-i', '--input', default='3113322113', type=parse_input)
    args = parser.parse_args()
    return Arguments(part=args.part, input=args.input)


def step(input: Iterable[int]) -> list[int]:
    it = iter(input)
    count = 1
    value = next(it)
    output: list[int] = []

    def append() -> None:
        output.append(count)
        output.append(value)

    for i in it:
        if i == value:
            count += 1
        else:
            append()
            count = 1
            value = i

    append()
    return output


def get_sequence_length_after_n_steps(sequence: list[int], steps: int) -> int:
    for _ in range(steps):
        sequence = step(sequence)
    return len(sequence)


def part_1(input: list[int]) -> int:
    return get_sequence_length_after_n_steps(input, 40)


def part_2(input: list[int]) -> int:
    return get_sequence_length_after_n_steps(input, 50)


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(args.input))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
