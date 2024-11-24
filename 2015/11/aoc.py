#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar, Final, Literal, final, override


@final
class Password:
    _DATUM: ClassVar = ord('a')

    def __init__(self, password: str) -> None:
        self.digits: Final = [ord(c) - self._DATUM for c in reversed(password)]

    @override
    def __str__(self) -> str:
        return ''.join(chr(self._DATUM + d) for d in reversed(self.digits))

    def increment(self) -> None:
        for i, digit in enumerate(self.digits):
            if digit == 25:
                self.digits[i] = 0
            else:
                self.digits[i] = digit + 1
                return
        raise OverflowError()


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    password: Password


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('-p', '--password', default='vzbxkghb', type=Password)
    args = parser.parse_args()
    return Arguments(part=args.part, password=args.password)


def validate(pwd: Password) -> bool:
    prev_1 = prev_2 = -1
    rule_1 = False
    pairs: dict[int, list[int]] = defaultdict(list)
    rule_2 = False

    for i, d in enumerate(pwd.digits):
        if d in {8, 11, 14}:
            return False

        if not rule_1 and d + 1 == prev_1 and d + 2 == prev_2:
            rule_1 = True

        if d == prev_1:
            for other_d, js in pairs.items():
                if d != other_d and any(j < i - 2 for j in js):
                    rule_2 = True
            else:
                pairs[d].append(i - 1)

        if rule_1 and rule_2:
            return True

        prev_2, prev_1 = prev_1, d

    return False


def find_next_valid_password(pwd: Password) -> None:
    while True:
        pwd.increment()
        if validate(pwd):
            return


def part_1(pwd: Password) -> Password:
    find_next_valid_password(pwd)
    return pwd


def part_2(pwd: Password) -> Password:
    find_next_valid_password(pwd)
    find_next_valid_password(pwd)
    return pwd


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(args.password))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
