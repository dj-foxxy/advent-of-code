#!/usr/bin/env python
from argparse import ArgumentParser
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, final


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    report_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    part: Literal[1, 2] = args.part
    report_path: Path = args.report
    return Arguments(part=part, report_path=report_path)


def load_report(path: Path) -> list[list[int]]:
    with open(path) as file:
        return [[int(value) for value in line.split(' ')] for line in file]


def compute_differences(values: list[int]) -> list[int]:
    return [values[i] - values[i - 1] for i in range(1, len(values))]


def create_differences_data(values: list[int]) -> list[list[int]]:
    data = [values]
    while any(data[-1]):
        data.append(compute_differences(data[-1]))
    return data


def iter_indexes(data: list[list[int]]) -> Iterable[int]:
    return range(len(data) - 2, -1, -1)


def extrapolate_forward(data: list[list[int]]) -> int:
    data[-1].append(0)
    for i in iter_indexes(data):
        data[i].append(data[i][-1] + data[i + 1][-1])
    return data[0][-1]


def sum_extrapolated_values(
    report: list[list[int]],
    extrapolate: Callable[[list[list[int]]], int],
) -> int:
    return sum(
        extrapolate(create_differences_data(values)) for values in report
    )


def part_1(report: list[list[int]]) -> int:
    return sum_extrapolated_values(report, extrapolate_forward)


def extrapolate_backward(data: list[list[int]]) -> int:
    for i in iter_indexes(data):
        data[i].insert(0, data[i][0] - data[i + 1][0])
    return data[0][0]


def part_2(report: list[list[int]]) -> int:
    return sum_extrapolated_values(report, extrapolate_backward)


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_report(args.report_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
