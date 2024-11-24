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


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    return Arguments(part=args.part, input_path=args.input)


@dataclass(frozen=True, kw_only=True, slots=True)
class Ingredient:
    name: str
    capacity: int
    durability: int
    flavor: int
    texture: int
    calories: int


def load_input(path: Path) -> list[Ingredient]:
    ingredients: list[Ingredient] = []
    with open(path) as file:
        for line in file:
            tokens = line.split()

            def int_token(i: int) -> int:
                return int(tokens[i].rstrip(','))

            ingredients.append(
                Ingredient(
                    name=tokens[0].rstrip(':'),
                    capacity=int_token(2),
                    durability=int_token(4),
                    flavor=int_token(6),
                    texture=int_token(8),
                    calories=int_token(10),
                )
            )
    return ingredients


def foo(ingredients: list[Ingredient], teaspoons: int) -> int:
    for i in range(teaspoons):
        ingredients[0]




def part_1(ingredients: list[Ingredient]) -> int:
    print(ingredients)
    return 0


def part_2(ingredients: list[Ingredient]) -> int:
    return 0


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
