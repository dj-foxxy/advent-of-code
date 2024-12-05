#!/usr/bin/python
from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Literal, NamedTuple, final


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-p', '--part', default=1, choices=(1, 2), type=int)
    parser.add_argument('-i', '--input', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


type Rules = Mapping[int, Set[int]]

type Update = Sequence[int]


@final
class Input(NamedTuple):
    rules: Rules
    updates: Sequence[Update]


type Result = int


def load_input(path: Path) -> Input:
    rules: dict[int, set[int]] = defaultdict(set)
    with open(path) as file:
        for line in iter(file.readline, '\n'):
            before, after = map(int, line.split('|'))
            rules[after].add(before)
        updates = tuple(
            tuple(map(int, line.strip().split(','))) for line in file
        )
    return Input(
        {after: frozenset(befores) for after, befores in rules.items()},
        updates,
    )


def is_valid(update: Update, rules: Rules) -> bool:
    for i, after in enumerate(update[:-1]):
        befores = rules.get(after)
        if befores and {*update[i + 1 :]} & befores:
            return False
    return True


def part_1(input: Input) -> Result:
    return sum(
        update[len(update) // 2]
        for update in input.updates
        if is_valid(update, input.rules)
    )


def fix_update(update: Update, rules: Rules) -> Update:
    graph: TopologicalSorter[int] = TopologicalSorter()
    for page in update:
        graph.add(page, *rules.get(page, ()))
    order = {page: i for i, page in enumerate(graph.static_order())}
    update = sorted(update, key=lambda page: order[page])
    return update


def part_2(input: Input) -> Result:
    return sum(
        fix_update(update, input.rules)[len(update) // 2]
        for update in input.updates
        if not is_valid(update, input.rules)
    )


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
