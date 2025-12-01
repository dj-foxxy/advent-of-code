#!/usr/bin/python
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, final, override

from rich import print


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


class Wire(ABC):
    def __init__(self, name: str) -> None:
        self.name: Final = name

    @override
    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.name!r})'

    @override
    def __str__(self) -> str:
        return self.name

    @abstractmethod
    def get_state(self) -> bool: ...


class FromGateWire(Wire):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._from_gate: Gate | None = None

    def get_from_gate(self) -> 'Gate':
        if self._from_gate is None:
            raise ValueError(
                f'{type(self).__name__} {self.name} does not have a from gate',
            )
        return self._from_gate

    def set_from_gate(self, gate: 'Gate') -> None:
        assert self._from_gate is None
        self._from_gate = gate


class ToGatesWire(Wire):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.to_gates: Final[set[Gate]] = set()


@final
class InputWire(ToGatesWire):
    def __init__(self, name: str, state: bool) -> None:
        super().__init__(name)
        self._state: Final = state

    @override
    def get_state(self) -> bool:
        return self._state


@final
class InternalWire(FromGateWire, ToGatesWire):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._state: bool | None = None

    @override
    def get_state(self) -> bool:
        if self._state is None:
            self._state = self.get_from_gate().get_state()
        return self._state


@final
class OutputWire(FromGateWire):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._state: bool | None = None

    @override
    def get_state(self) -> bool:
        if self._state is None:
            self._state = self.get_from_gate().get_state()
        return self._state


@dataclass(frozen=True, slots=True)
class Gate(ABC):
    input_1: Final[InputWire | InternalWire]
    input_2: Final[InputWire | InternalWire]
    output: Final[InternalWire | OutputWire]

    @abstractmethod
    def compute(self, input_1: bool, input_2: bool) -> bool: ...

    def get_state(self) -> bool:
        return self.compute(self.input_1.get_state(), self.input_2.get_state())


@final
class And(Gate):
    @override
    def compute(self, input_1: bool, input_2: bool) -> bool:
        return input_1 and input_2


@final
class Or(Gate):
    @override
    def compute(self, input_1: bool, input_2: bool) -> bool:
        return input_1 or input_2


@final
class XOr(Gate):
    @override
    def compute(self, input_1: bool, input_2: bool) -> bool:
        return input_1 != input_2


@final
@dataclass(frozen=True, slots=True)
class Input:
    input_wires: dict[str, InputWire]
    internal_wires: dict[str, InternalWire]
    output_wires: dict[str, OutputWire]
    gates: list[Gate]


def load_input(path: Path) -> Input:
    input_wires: dict[str, InputWire] = {}
    internal_wires: dict[str, InternalWire] = {}
    output_wires: dict[str, OutputWire] = {}
    gates: list[Gate] = []

    def get_non_output_wire(name: str) -> InputWire | InternalWire:
        if (wire := input_wires.get(name)) is not None:
            return wire
        if (wire := internal_wires.get(name)) is not None:
            return wire
        assert not name.startswith('z')
        wire = internal_wires[name] = InternalWire(name)
        return wire

    states = {'0': False, '1': True}

    with open(path) as file:
        for line in iter(file.readline, '\n'):
            name, state_str = line.rstrip().split(': ', maxsplit=1)
            assert name not in input_wires
            input_wires[name] = InputWire(name, states[state_str])

        for line in file:
            input_1_name, operator, input_2_name, _, output_name = line.split()
            input_1 = get_non_output_wire(input_1_name)
            input_2 = get_non_output_wire(input_2_name)

            if output_name.startswith('z'):
                assert output_name not in input_wires
                assert output_name not in internal_wires
                assert output_name not in output_wires
                output = output_wires[output_name] = OutputWire(output_name)
            elif (output := internal_wires.get(output_name)) is None:
                assert output_name not in input_wires
                assert output_name not in internal_wires
                assert output_name not in output_wires
                output = internal_wires[output_name] = InternalWire(output_name)

            match operator:
                case 'AND':
                    gate_factory = And
                case 'OR':
                    gate_factory = Or
                case 'XOR':
                    gate_factory = XOr
                case _:
                    raise ValueError()

            gate = gate_factory(input_1, input_2, output)
            input_1.to_gates.add(gate)
            input_2.to_gates.add(gate)
            output.set_from_gate(gate)
            gates.append(gate)

    return Input(input_wires, internal_wires, output_wires, gates)


type Result = int


def part_1(input: Input) -> Result:
    output_wires = sorted(
        input.output_wires.values(),
        key=lambda wire: wire.name,
        reverse=True,
    )
    return int(
        ''.join(
            str(int(output_wire.get_state())) for output_wire in output_wires
        ),
        2,
    )


def part_2(input: Input) -> Result:
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
