#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum, auto, unique
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


def load_text(path: Path) -> str:
    return path.read_text()


@final
@unique
class State(Enum):
    START = auto()
    SLASH_1 = auto()
    HEX_1 = auto()
    HEX_2 = auto()


def part_1(text: str) -> int:
    state = State.START
    code_len = 0
    data_len = 0
    for c in text:
        if c == '\n':
            continue
        code_len += 1
        match c:
            case '\\':
                match state:
                    case State.START:
                        state = State.SLASH_1
                    case State.SLASH_1:
                        state = State.START
                        data_len += 1
                    case _:
                        raise ValueError()
            case '"':
                match state:
                    case State.START:
                        pass
                    case State.SLASH_1:
                        state = State.START
                        data_len += 1
                    case _:
                        raise ValueError()
            case 'x':
                match state:
                    case State.START:
                        data_len += 1
                    case State.SLASH_1:
                        state = State.HEX_1
                    case _:
                        raise ValueError()
            case _:
                match state:
                    case State.START:
                        data_len += 1
                    case State.HEX_1:
                        state = State.HEX_2
                    case State.HEX_2:
                        data_len += 1
                        state = State.START
                    case _:
                        raise ValueError()
    return code_len - data_len


def part_2(text: str) -> int:
    state = State.START
    code_len = 0
    encode_len = 0
    for c in text:
        if c == '\n':
            continue
        code_len += 1
        match c:
            case '\\':
                match state:
                    case State.START:
                        state = State.SLASH_1
                        encode_len += 2
                    case State.SLASH_1:
                        state = State.START
                        encode_len += 2
            case '"':
                match state:
                    case State.START:
                        encode_len += 3
                    case State.SLASH_1:
                        state = State.START
                        encode_len += 2
            case 'x':
                match state:
                    case State.START:
                        encode_len += 1
                    case State.SLASH_1:
                        state = State.START
                        encode_len += 1
            case _:
                encode_len += 1
    return encode_len - code_len

def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_text(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
