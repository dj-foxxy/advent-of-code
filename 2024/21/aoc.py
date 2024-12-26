#!/usr/bin/python
from argparse import ArgumentParser
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto, unique
from pathlib import Path
from typing import Final, Literal, final, override

verbose = False


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    verbose: bool


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(
        part=args.part,
        input_path=input_path,
        verbose=args.verbose,
    )


@final
@unique
class Action(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    ACTIVATE = auto()


def actions_str(actions: Iterable[Action | int]) -> str:
    parts: list[str] = []
    for action in actions:
        match action:
            case Action.UP:
                c = '^'
            case Action.DOWN:
                c = 'v'
            case Action.LEFT:
                c = '<'
            case Action.RIGHT:
                c = '>'
            case Action.ACTIVATE:
                c = 'A'
            case int():
                c = str(action)
        parts.append(c)
    return ''.join(parts)


type Code = tuple[int, int, int, Literal[Action.ACTIVATE]]


def parse_code(text: str) -> Code:
    if len(text) != 4 or text[3] != 'A':
        raise ValueError('invalid code')
    return (
        int(text[0]),
        int(text[1]),
        int(text[2]),
        Action.ACTIVATE,
    )


def load_codes(path: Path) -> tuple[Code, ...]:
    with open(path) as file:
        return tuple(parse_code(line.rstrip()) for line in file)


@final
class link:
    def __init__(
        self,
        name: Action | int,
        up: Action | int | None = None,
        right: Action | int | None = None,
    ) -> None:
        self.name: Final = name
        self.up: Final = up
        self.right: Final = right


@final
class Button:
    def __init__(self, id: Action | int) -> None:
        self.id: Final = id
        self.up: Button | None = None
        self.down: Button | None = None
        self.left: Button | None = None
        self.right: Button | None = None
        self.actions: Final[dict[Button, tuple[Action, ...]]] = {}

    @override
    def __repr__(self) -> str:
        return f'Button({self.id!r})'

    @override
    def __str__(self) -> str:
        def id(id: Action | int) -> str:
            return id.name[0] if isinstance(id, Action) else str(id)

        args = [id(self.id)]

        for tag, neighbor in (
            ('up', self.up),
            ('down', self.down),
            ('left', self.left),
            ('right', self.right),
        ):
            if neighbor is not None:
                args.append(f'{tag}={id(neighbor.id)}')

        return f'Button({', '.join(args)})'


type Keypad = dict[Action | int, Button]


def create_keypad(
    priority_1: Action,
    priority_2: Action,
    priority_3: Action,
    priority_4: Action,
    *links: link,
) -> Keypad:
    ids: set[Action | int] = set()

    for btn in links:
        ids.add(btn.name)
        if btn.up is not None:
            ids.add(btn.up)
        if btn.right is not None:
            ids.add(btn.right)

    keypad = {id: Button(id) for id in ids}

    for btn in links:
        b = keypad[btn.name]
        if btn.up is not None:
            u = keypad[btn.up]
            b.up = u
            u.down = b
        if btn.right is not None:
            r = keypad[btn.right]
            b.right = r
            r.left = b

    priorities = {
        priority_1: 0,
        priority_2: 1,
        priority_3: 2,
        priority_4: 3,
        Action.ACTIVATE: 4,
    }

    for source in keypad.values():
        frontier = [source]
        seen = {source}
        source.actions[source] = (Action.ACTIVATE,)
        while frontier:
            current = frontier.pop(0)
            for neighbor, move in (
                (current.up, Action.UP),
                (current.down, Action.DOWN),
                (current.left, Action.LEFT),
                (current.right, Action.RIGHT),
            ):
                if neighbor is not None and neighbor not in seen:
                    frontier.append(neighbor)
                    seen.add(neighbor)
                    actions = [
                        *source.actions[current][:-1],
                        move,
                        Action.ACTIVATE,
                    ]
                    p = [*actions]
                    actions.sort(key=lambda move: priorities[move])
                    print(actions_str(actions), actions_str(p))
                    source.actions[neighbor] = tuple(actions)
>>^A
    return keypad


"""
+---+---+---+
| 7 | 8 | 9 |
+---+---+---+
| 4 | 5 | 6 |
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
    | 0 | A |
    +---+---+
"""

numeric_keypad: Final = create_keypad(
    Action.RIGHT,
    Action.UP,
    Action.LEFT,
    Action.DOWN,
    link(0, up=2, right=Action.ACTIVATE),
    link(Action.ACTIVATE, up=3),
    link(1, up=4, right=2),
    link(2, up=5, right=3),
    link(3, up=6),
    link(4, up=7, right=5),
    link(5, up=8, right=6),
    link(6, up=9),
    link(7, right=8),
    link(8, right=9),
)


"""
    +---+---+
    | ^ | A |
+---+---+---+
| < | v | > |
+---+---+---+
"""
directional_keypad: Final = create_keypad(
    Action.DOWN,
    Action.RIGHT,
    Action.UP,
    Action.LEFT,
    link(Action.LEFT, right=Action.DOWN),
    link(Action.DOWN, up=Action.UP, right=Action.RIGHT),
    link(Action.RIGHT, up=Action.ACTIVATE),
    link(Action.UP, right=Action.ACTIVATE),
)


def find_actions(
    keypad: Keypad,
    button_ids: Iterable[Action | int],
) -> list[Action]:
    button = keypad[Action.ACTIVATE]
    actions: list[Action] = []
    for next_button_id in button_ids:
        next_button = keypad[next_button_id]
        actions.extend(button.actions[next_button])
        print(actions_str(button.actions[next_button]))
        button = next_button
    return actions


def find_code_complexity(code: Code) -> int:
    actions = code
    for keypad in (
        numeric_keypad,
        directional_keypad,
        directional_keypad,
    ):
        actions = find_actions(keypad, actions)
        if verbose:
            print(actions_str(actions))
    numeric_part = int(''.join(map(str, code[:-1])))
    complexity = len(actions) * numeric_part
    if verbose:
        print(f'{len(actions)} * {numeric_part} = {complexity}')
        print()
    return complexity


def parse_actions(text: str) -> list[Action]:
    actions: list[Action] = []
    for token in text:
        match token:
            case '^':
                a = Action.UP
            case 'v':
                a = Action.DOWN
            case '<':
                a = Action.LEFT
            case '>':
                a = Action.RIGHT
            case 'A':
                a = Action.ACTIVATE
            case _:
                raise ValueError()
        actions.append(a)
    return actions



def part_1(codes: tuple[Code, ...]) -> int:
    return sum(find_code_complexity(code) for code in codes)


def part_2(codes: tuple[Code, ...]) -> int:
    return 0


def check[T](value: T | None) -> T:
    if value is None:
        raise ValueError()
    return value


def simulate(keypad: Keypad, actions: Iterable[Action]):
    button = keypad[Action.ACTIVATE]
    output: list[Action | int] = []
    for action in actions:
        match action:
            case Action.UP:
                button = check(button.up)
            case Action.DOWN:
                button = check(button.down)
            case Action.LEFT:
                button = check(button.left)
            case Action.RIGHT:
                button = check(button.right)
            case Action.ACTIVATE:
                output.append(button.id)
    return output


def main() -> None:
    actions_1 = parse_actions('<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A')
    actions_2 = simulate(directional_keypad, actions_1)
    actions_3 = simulate(directional_keypad, actions_2)
    actions_4 = simulate(numeric_keypad, actions_3)
    print(actions_str(actions_4))
    print(actions_str(actions_3))
    print(actions_str(actions_2))
    print(actions_str(actions_1))
    print()


    global verbose
    args = parse_args()
    if args.verbose:
        verbose = True
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_codes(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
