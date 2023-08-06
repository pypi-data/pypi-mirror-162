import functools
import operator
from abc import ABC, abstractmethod
from typing import Iterable, Union, Dict, List, Any, Optional, Sequence

JsonValue = Union[None, bool, int, float, str, List[Any], Dict[str, Any]]


def assert_list(value: JsonValue):
    if not isinstance(value, list):
        raise TypeError(f"Expected list, got {type(value)}: {value}")


def assert_dict(value: JsonValue):
    if not isinstance(value, dict):
        raise TypeError(f"Expected dict, got {type(value)}: {value}")


class Filter(ABC):
    @abstractmethod
    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        ...

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__


class Identity(Filter):
    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        yield val

    def __str__(self):
        return "."

    def __repr__(self):
        return "Identity()"


class Prop(Filter):
    def __init__(self, prop: str):
        self.prop = prop

    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        assert_dict(val)
        yield val.get(self.prop)

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.prop == other.prop

    def __str__(self):
        return f".{self.prop}"

    def __repr__(self):
        return f"Prop({self.prop})"


class Index(Filter):
    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        if isinstance(val, list):
            for v in val:
                yield v
        elif isinstance(val, dict):
            for v in val.values():
                yield v
        else:
            raise TypeError(f"Expected list or dict, got {type(val)}: {val}")

    def __str__(self):
        return ".[]"

    def __repr__(self):
        return "Index()"


class Literal(Filter):
    def __init__(self, literal: JsonValue):
        self.literal = literal

    def input(self, _: JsonValue) -> Iterable[JsonValue]:
        yield self.literal

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.literal == other.literal

    def __str__(self):
        return str(self.literal)

    def __repr__(self):
        return f"Literal({self.literal})"


class Empty(Filter):
    def input(self, _: JsonValue) -> Iterable[JsonValue]:
        yield from ()

    def __str__(self):
        return "empty"

    def __repr__(self):
        return "Empty()"


class Comma(Filter):
    def __init__(self, filters: List[Filter]):
        self.filters = filters

    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        for f in self.filters:
            for v in f.input(val):
                yield v

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.filters == other.filters

    def __str__(self):
        return ",".join(str(f) for f in self.filters)

    def __repr__(self):
        return f"Comma({self.filters})"


class Array(Filter):
    def __init__(self, filter: Optional[Filter] = None):
        self.filter = filter

    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        result = []
        if self.filter:
            for v in self.filter.input(val):
                result.append(v)
        yield result

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.filter == other.filter

    def __str__(self):
        return f"[{self.filter}]"

    def __repr__(self):
        return f"Array({self.filter!r})"


class Object(Filter):
    def __init__(self, filter_dict: Dict[str, Filter]):
        self.filter_dict = filter_dict

    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        result = {}
        for k, f in self.filter_dict.items():
            for v in f.input(val):
                result[k] = v
        yield result

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.filter_dict == other.filter_dict

    def __str__(self):
        return "{" + ",".join(f"{k}:{v}" for k, v in self.filter_dict.items()) + "}"

    def __repr__(self):
        return f"Object({self.filter_dict!r})"


class Pipe(Filter):
    def __init__(self, filters: List[Filter]):
        self.filters = filters

    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        yield from self._input_with_filters(val, self.filters)

    def _input_with_filters(
        self, val: JsonValue, filters: List[Filter]
    ) -> Iterable[JsonValue]:
        if not filters:
            yield val
            return
        [first, *rest] = filters
        for v in first.input(val):
            yield from self._input_with_filters(v, rest)

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.filters == other.filters

    def __str__(self):
        return " | ".join(str(f) for f in self.filters)

    def __repr__(self):
        return f"Pipe({self.filters!r})"


class Op:
    def __init__(self, op, sym: str):
        self.op = op
        self.sym = sym

    def __call__(self, *args, **kwargs):
        return self.op.__call__(*args, **kwargs)

    def __eq__(self, other) -> bool:
        return self.op is other.op

    def __str__(self):
        return self.sym


class BinOp(Filter):
    def __init__(self, left: Filter, right: Filter, op: Op):
        self.left = left
        self.right = right
        self.op = op

    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        for v1 in self.left.input(val):
            for v2 in self.right.input(val):
                yield self.op(v1, v2)

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.left == other.left
            and self.right == other.right
            and self.op == other.op
        )

    def __str__(self):
        return f"{self.left} {self.op} {self.right}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.left!r}, {self.right!r})"


class Add(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Add, self).__init__(left, right, Op(operator.add, "+"))


class Sub(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Sub, self).__init__(left, right, Op(operator.sub, "-"))


class Mul(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Mul, self).__init__(left, right, Op(operator.mul, "*"))


class Div(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Div, self).__init__(left, right, Op(operator.truediv, "/"))


class Mod(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Mod, self).__init__(left, right, Op(operator.mod, "%"))


class Eq(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Eq, self).__init__(left, right, Op(operator.eq, "=="))


class Ne(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Ne, self).__init__(left, right, Op(operator.ne, "!="))


class Gt(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Gt, self).__init__(left, right, Op(operator.gt, ">"))


class Ge(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Ge, self).__init__(left, right, Op(operator.ge, ">="))


class Lt(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Lt, self).__init__(left, right, Op(operator.lt, "<"))


class Le(BinOp):
    def __init__(self, left: Filter, right: Filter):
        super(Le, self).__init__(left, right, Op(operator.le, "<="))


class Fn(Filter, ABC):
    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()


class Sum(Fn):
    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        assert_list(val)
        if not val:
            yield None
        else:
            yield functools.reduce(operator.add, val)

    def __str__(self):
        return "sum"


class Length(Fn):
    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        if isinstance(val, (list, dict, str)):
            yield len(val)
        else:
            raise TypeError(f"{type(val)} {val} has no length")

    def __str__(self):
        return "length"


class Select(Fn):
    def __init__(self, filter: Filter):
        self.filter = filter

    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        for v in self.filter.input(val):
            if v is not None and v is not False:
                yield val

    def __str__(self):
        return f"select({self.filter})"


class Map(Fn):
    def __init__(self, filter: Filter):
        self.filter = filter

    def input(self, val: JsonValue) -> Iterable[JsonValue]:
        yield from Array(Pipe([Index(), self.filter])).input(val)

    def __str__(self):
        return f"map({self.filter})"
