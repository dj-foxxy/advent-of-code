#!/usr/bin/env python
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
import re
from typing import ClassVar, Final, Literal, NamedTuple, final, override


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


class Node(ABC):
    def get_value(self) -> int: ...


class BaseComponent(Node):
    @abstractmethod
    def get_int_value(self) -> int: ...

    @override
    def get_value(self) -> int:
        return self.get_int_value() & 0xFFFF


@final
class Wire(Node):
    _name_pattern: ClassVar = re.compile(r'\A[a-z]{1,2}\Z')

    def __init__(self, name: str) -> None:
        if self._name_pattern.match(name) is None:
            raise ValueError(f'invalid name {name!r}')
        self.name: Final = name
        self.input: BaseComponent = ZERO_COMPONENT
        self.outputs: Final[list[BaseComponent]] = []
        self._value: int | None = None
        self._evaluating = False

    @override
    def __str__(self) -> str:
        return f'{self.name}[{'?' if self._value is None else self._value}]'

    @override
    def get_value(self) -> int:
        if self._evaluating:
            raise RuntimeError()
        if self._value is None:
            self._evaluating = True
            try:
                self._value = self.input.get_value()
            finally:
                self._evaluating = False
        return self._value


    def set_value(self, value: int) -> None:
        self._value = value

    def reset(self) -> None:
        self._value = None


class ZeroComponent(BaseComponent):
    @override
    def get_int_value(self) -> int:
        raise RuntimeError()


ZERO_COMPONENT: Final = ZeroComponent()


class Component(BaseComponent):
    def __init__(self, output: Wire) -> None:
        self.output: Final = output
        output.input = self


@final
class Input(Component):
    def __init__(self, value: int, output: Wire) -> None:
        super().__init__(output)
        self.value = value

    @override
    def __str__(self) -> str:
        return f'{self.value} -> {self.output}'

    @override
    def get_int_value(self) -> int:
        return self.value


class Component1(Component):
    def __init__(self, input: Wire, output: Wire) -> None:
        super().__init__(output)
        self.input: Final = input
        self.input.outputs.append(self)


@final
class Join(Component1):
    @override
    def __str__(self) -> str:
        return f'JOIN({self.input}) -> {self.output}'

    @override
    def get_int_value(self) -> int:
        return self.input.get_value()


@final
class Not(Component1):
    @override
    def __str__(self) -> str:
        return f'NOT({self.input}) -> {self.output}'

    @override
    def get_int_value(self) -> int:
        return ~self.input.get_value()


class Component2(Component):
    def __init__(self, input_1: Wire, input_2: Wire, output: Wire) -> None:
        super().__init__(output)
        self.input_1: Final = input_1
        self.input_1.outputs.append(self)
        self.input_2: Final = input_2
        self.input_2.outputs.append(self)


@final
class Or(Component2):
    @override
    def __str__(self) -> str:
        return f'OR({self.input_1}, {self.input_2}) -> {self.output}'

    @override
    def get_int_value(self) -> int:
        return self.input_1.get_value() | self.input_2.get_value()


@final
class And(Component2):
    @override
    def __str__(self) -> str:
        return f'AND({self.input_1}, {self.input_2}) -> {self.output}'

    @override
    def get_int_value(self) -> int:
        return self.input_1.get_value() & self.input_2.get_value()


@final
class AndConstant(BaseComponent):
    def __init__(self, constant: int, input: Wire, output: Wire) -> None:
        self.constant: Final = constant
        self.input: Final = input
        self.input.outputs.append(self)
        self.output: Final = output
        self.output.input = self

    @override
    def __str__(self) -> str:
        return f'AND({self.constant}, {self.input}) -> {self.output}'

    @override
    def get_int_value(self) -> int:
        return self.constant & self.input.get_value()


class Component1o(Component):
    def __init__(self, input_1: Wire, operand: int, output: Wire) -> None:
        super().__init__(output)
        self.input: Final = input_1
        self.input.outputs.append(self)
        self.operand: Final = operand


@final
class LShift(Component1o):
    @override
    def __str__(self) -> str:
        return f'LSHIFT({self.input}, {self.operand}) -> {self.output}'

    @override
    def get_int_value(self) -> int:
        return self.input.get_value() << self.operand


@final
class RShift(Component1o):
    @override
    def __str__(self) -> str:
        return f'RSHIFT({self.input}, {self.operand}) -> {self.output}'

    @override
    def get_int_value(self) -> int:
        return self.input.get_value() >> self.operand


@final
class Circuit(NamedTuple):
    wires: Mapping[str, Wire]
    nodes: Sequence[Node]

    def reset(self) -> None:
        for wire in self.wires.values():
            wire.reset()


def parse_node(wires: dict[str, Wire], text: str) -> BaseComponent:
    tokens = text.split()

    def wire(i: int) -> Wire:
        name = tokens[i]
        try:
            return wires[name]
        except KeyError:
            wires[name] = wire = Wire(name)
            return wire

    if tokens[0] == 'NOT':
        return Not(wire(1), wire(3))
    match tokens[1]:
        case '->':
            token = tokens[0]
            output = wire(2)
            if token.isdigit():
                return Input(int(token), output)
            return Join(wire(0), output)
        case 'OR':
            return Or(wire(0), wire(2), wire(4))
        case 'AND':
            token = tokens[0]
            input_2 = wire(2)
            output = wire(4)
            if token.isdigit():
                return AndConstant(int(token), input_2, output)
            return And(wire(0), input_2, output)
        case 'LSHIFT' | 'RSHIFT' as token:
            factory = LShift if token == 'LSHIFT' else RShift
            return factory(wire(0), int(tokens[2]), wire(4))
        case _ as token:
            raise ValueError(f'invalid gate {token!r} in {text!r}')


def load_circuit(path: Path) -> Circuit:
    wires: dict[str, Wire] = {}
    with open(path) as file:
        nodes = [parse_node(wires, line) for line in file]
    return Circuit(dict(wires), nodes)


def part_1(circuit: Circuit) -> int:
    return circuit.wires['a'].get_value()


def part_2(circuit: Circuit) -> int:
    wire_a = circuit.wires['a']
    value_b = wire_a.get_value()
    circuit.reset()
    circuit.wires['b'].set_value(value_b)
    return wire_a.get_value()


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_circuit(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
