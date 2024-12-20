#!/usr/bin/python
from argparse import ArgumentParser
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal, final, override


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path
    start: int


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-s', '--start', default=0, type=int)
    parser.add_argument('part', default=1, choices=(1, 2), type=int)
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
    init_a: int = field(init=False)
    b: int
    init_b: int = field(init=False)
    c: int
    init_c: int = field(init=False)
    program: Final[list[int]]
    ip: int = 0
    output: Final[list[int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.init_a = self.a
        self.init_b = self.b
        self.init_c = self.c

    def reset(self, a: int | None = None) -> None:
        if a is None:
            a = self.init_a
        self.a = a
        self.b = self.init_b
        self.c = self.init_c
        self.ip = 0
        self.output.clear()

    def run(self) -> None:
        with suppress(Halt):
            while True:
                self.step()

    def reset_and_run(self, a: int | None = None) -> None:
        self.reset(a=a)
        self.run()

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


def load_input(path: Path) -> Machine:
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
    return Machine(a, b, c, memory)


def part_1(machine: Machine) -> str:
    machine.run()
    return ','.join(map(str, machine.output))


def find_a(m: Machine, i: int, a_lsb: int) -> int | None:
    if i == len(m.program):
        return a_lsb
    for a_msb in range(8):
        a = (a_msb << (8 + 3 * i)) | a_lsb
        m.reset_and_run(a)
        if m.output[: i + 1] == m.program[: i + 1]:
            if (a := find_a(m, i + 1, a)) is not None:
                return a


def part_2(machine: Machine) -> int:
    for a_lsb in range(2**12):
        machine.reset_and_run(a_lsb)
        if (
            machine.output[0] == machine.program[0]
            and (a := find_a(machine, 1, a_lsb)) is not None
        ):
            return a
    raise ValueError()


def main() -> None:
    args = parse_args()
    machine = load_input(args.input_path)
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(machine))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
