#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, final


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


def iter_words(path: Path) -> Iterator[str]:
    with open(path) as file:
        for line in file:
            yield line.strip()


def is_nice_v1(word: str) -> bool:
    prev_c = ''
    has_double = False
    vowels = 0
    for c in word:
        if (
            (prev_c == 'a' and c == 'b')
            or (prev_c == 'c' and c == 'd')
            or (prev_c == 'p' and c == 'q')
            or (prev_c == 'x' and c == 'y')
        ):
            return False
        if c == prev_c:
            has_double = True
        if c in {'a', 'e', 'i', 'o', 'u'}:
            vowels += 1
        prev_c = c
    return has_double and vowels >= 3


def is_nice_v2(word: str) -> bool:
    c_1 = ''
    c_2 = ''
    c_3 = ''
    pairs: set[str] = set()
    rule_1 = rule_2 = False
    for c in word:
        if not rule_1:
            pairs.add(f'{c_3}{c_2}')
            if f'{c_1}{c}' in pairs:
                rule_1 = True
        if not rule_2 and c == c_2:
            rule_2 = True
        if rule_1 and rule_2:
            return True
        c_3, c_2, c_1 = c_2, c_1, c
    return False


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            is_nice = is_nice_v1
        case 2:
            is_nice = is_nice_v2
    nice_count = 0
    for word in iter_words(args.input_path):
        nice = is_nice(word)
        nice_count += nice
    print(nice_count)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
