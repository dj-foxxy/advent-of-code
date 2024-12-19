#!/usr/bin/python
from argparse import ArgumentParser
from contextlib import suppress
from dataclasses import dataclass, field
from itertools import count
from pathlib import Path
from typing import Final, Literal, final, override


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2, 3]
    input_path: Path
    start: int


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-s', '--start', default=0, type=int)
    parser.add_argument('part', default=1, choices=(1, 2, 3), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path, start=args.start)


@final
class Halt(BaseException):
    pass


@dataclass(slots=True)
class Machine:
    a: int
    b: int
    c: int
    program: Final[list[int]]
    ip: int = 0
    output: Final[list[int]] = field(default_factory=list)

    def state(self) -> tuple[int, ...]:
        return (self.a, self.b, self.c, self.ip, *self.output)

    def read(self, address: int) -> int:
        try:
            return self.program[address]
        except IndexError as error:
            raise Halt() from error

    def literal(self) -> int:
        return self.read(self.ip + 1)

    def combo(self) -> int:
        match self.literal():
            case 0 | 1 | 2 | 3 as literal:
                return literal
            case 4:
                return self.a
            case 5:
                return self.b
            case 6:
                return self.c
            case _ as value:
                raise ValueError(f'invalid combo operand {value!r}')

    def inc_ip(self) -> None:
        self.ip += 2

    def _dv(self) -> int:
        return self.a >> self.combo()

    def adv(self) -> None:
        self.a = self._dv()
        self.inc_ip()

    def bxl(self) -> None:
        self.b ^= self.literal()
        self.inc_ip()

    def bst(self) -> None:
        self.b = self.combo() % 8
        self.inc_ip()

    def jnz(self) -> None:
        if self.a:
            self.ip = self.literal()
        else:
            self.inc_ip()

    def bxc(self) -> None:
        self.literal()
        self.b ^= self.c
        self.inc_ip()

    def out(self) -> None:
        self.output.append(self.combo() % 8)
        self.inc_ip()

    def bdv(self) -> None:
        self.b = self._dv()
        self.inc_ip()

    def cdv(self) -> None:
        self.c = self._dv()
        self.inc_ip()

    def step(self) -> None:
        match self.read(self.ip):
            case 0:
                self.adv()
            case 1:
                self.bxl()
            case 2:
                self.bst()
            case 3:
                self.jnz()
            case 4:
                self.bxc()
            case 5:
                self.out()
            case 6:
                self.bdv()
            case 7:
                self.cdv()
            case _ as opcode:
                raise ValueError(f'invalid opcode {opcode!r}')


@final
class InvalidOutput(RuntimeError):
    pass


@final
class Part2Machine(Machine):
    @override
    def out(self) -> None:
        value = self.combo() % 8
        if value != self.program[len(self.output)]:
            raise InvalidOutput()
        self.output.append(value)
        self.inc_ip()


def load_input(path: Path, part: Literal[1, 2, 3]) -> Machine:
    with open(path) as file:
        line_iter = iter(file)

        def parse_key_value() -> str:
            return next(line_iter).split(':', maxsplit=1)[1]

        def parse_reg() -> int:
            return int(parse_key_value())

        a = parse_reg()
        b = parse_reg()
        c = parse_reg()
        next(line_iter)
        memory = list(map(int, parse_key_value().split(',')))
    cls = Part2Machine if part == 2 else Machine
    return cls(a, b, c, memory)


def part_1(machine: Machine) -> str:
    while True:
        try:
            machine.step()
        except Halt:
            break
    print(machine)
    return ','.join(map(str, machine.output))


def part_2(machine: Machine, start: int = 0) -> int:
    unfeasible_states: set[tuple[int, ...]] = set()
    states: list[tuple[int, ...]] = []
    a = -1
    b = machine.b
    c = machine.c
    try:
        for a in count(start=start):
            machine.a = a
            try:
                while True:
                    state = machine.state()
                    if state in unfeasible_states:
                        break
                    states.append(state)
                    machine.step()
            except Halt:
                if machine.output == machine.program:
                    return a
            except InvalidOutput:
                pass
            unfeasible_states.update(states)
            states.clear()
            if len(unfeasible_states) > 5e7:
                print('Clearing cache')
                unfeasible_states.clear()
            machine.b = b
            machine.c = c
            machine.output.clear()
            machine.ip = 0
    except KeyboardInterrupt:
        print('Stopped at', a - 1)
        raise
    raise AssertionError()


def part_3(m: Machine) -> None:
    base = 8 ** (len(m.program) - 1)
    b = m.b
    c = m.c
    for a in range(base, base + 2 ** 8):
        m.a = a
        print(m)
        with suppress(Halt):
            while True:
                m.step()
                print(m)
        print(a, m.output, m.program[0])
        if m.output[:1] == m.program[:1]:
            print(a)
            print(len(m.program), m.program)
            print(len(m.output), m.output)
            break
        m.b = b
        m.c = c
        m.output.clear()
        m.ip = 0


def main() -> None:
    args = parse_args()
    machine = load_input(args.input_path, args.part)
    match args.part:
        case 1:
            print(part_1(machine))
        case 2:
            print(part_2(machine, start=args.start))
        case 3:
            part_3(machine)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
