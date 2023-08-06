from enum import Enum
from typing import Any, Iterable, NamedTuple, Optional

from jqlite.context import Context
from jqlite.filters import (
    Filter,
    Literal,
    Prop,
    Index,
    Identity,
    Array,
    Comma,
    Mul,
    Div,
    Add,
    Sub,
    Gt,
    Ge,
    Lt,
    Le,
    Eq,
    Ne,
    Pipe,
    Empty,
    Object,
    Fn,
    Mod,
)


class TokenType(Enum):
    PUNCT = "punct"
    NUM = "num"
    STR = "str"
    IDENT = "ident"


class Token(NamedTuple):
    type: TokenType
    val: Any


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def lex(self) -> Iterable[Token]:
        while self.pos < len(self.text):
            char = self.text[self.pos]

            if char.isspace():
                self.pos += 1
                continue
            elif char in "!<>=+-*/" and self.text[self.pos + 1] == "=":
                self.pos += 2
                yield Token(TokenType.PUNCT, char + "=")
            elif char in ".,:[]{}()<>=+-*/%|":
                self.pos += 1
                yield Token(TokenType.PUNCT, char)
            elif char == '"':
                yield self._read_str()
            elif char.isdigit():
                yield self._read_num()
            elif char.isalpha():
                yield self._read_ident()
            else:
                raise ValueError(f"invalid character {char}")

    def _read_str(self):
        start = self.pos
        self.pos += 1
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            self.pos += 1
        self.pos += 1
        return Token(TokenType.STR, self.text[start + 1 : self.pos - 1])

    def _read_num(self):
        start = self.pos
        while self.pos < len(self.text) and (
            self.text[self.pos] == "." or self.text[self.pos].isdigit()
        ):
            self.pos += 1
        return Token(TokenType.NUM, float(self.text[start : self.pos]))

    def _read_ident(self):
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos].isalpha():
            self.pos += 1
        return Token(TokenType.IDENT, self.text[start : self.pos])


class Parser:
    """
    优先级:
        |
        ,
        = +=, -=, *=, /=
        > >= < <= == !=
        + -
        * /
        () atom
    """

    def __init__(self, text):
        lexer = Lexer(text)
        self.ctx = Context()
        self.tokens = list(lexer.lex())
        self.pos = 0

    def parse(self) -> Optional[Filter]:
        if not self._peek():
            return
        return self._parse_pipe()

    def _parse_pipe(self) -> Filter:
        filters = [self._parse_comma()]
        while self._peek() == Token(TokenType.PUNCT, "|"):
            self._next()
            filters.append(self._parse_comma())
        return Pipe(filters) if len(filters) > 1 else filters[0]

    def _parse_comma(self) -> Filter:
        filters = [self._parse_eq()]
        while self._peek() == Token(TokenType.PUNCT, ","):
            self._next()
            filters.append(self._parse_eq())
        return Comma(filters) if len(filters) > 1 else filters[0]

    def _parse_eq(self):
        result = self._parse_add()
        if self._peek() == Token(TokenType.PUNCT, ">"):
            self._next()
            result = Gt(result, self._parse_add())
        elif self._peek() == Token(TokenType.PUNCT, ">="):
            self._next()
            result = Ge(result, self._parse_add())
        elif self._peek() == Token(TokenType.PUNCT, "<"):
            self._next()
            result = Lt(result, self._parse_add())
        elif self._peek() == Token(TokenType.PUNCT, "<="):
            self._next()
            result = Le(result, self._parse_add())
        elif self._peek() == Token(TokenType.PUNCT, "=="):
            self._next()
            result = Eq(result, self._parse_add())
        elif self._peek() == Token(TokenType.PUNCT, "!="):
            self._next()
            result = Ne(result, self._parse_add())
        return result

    def _parse_add(self) -> Filter:
        result = self._parse_mul()
        while True:
            if self._peek() == Token(TokenType.PUNCT, "+"):
                self._next()
                result = Add(result, self._parse_mul())
            elif self._peek() == Token(TokenType.PUNCT, "-"):
                self._next()
                result = Sub(result, self._parse_mul())
            else:
                break
        return result

    def _parse_mul(self) -> Filter:
        result = self._parse_atom()
        while True:
            if self._peek() == Token(TokenType.PUNCT, "*"):
                self._next()
                result = Mul(result, self._parse_atom())
            elif self._peek() == Token(TokenType.PUNCT, "/"):
                self._next()
                result = Div(result, self._parse_atom())
            elif self._peek() == Token(TokenType.PUNCT, "%"):
                self._next()
                result = Mod(result, self._parse_atom())
            else:
                break
        return result

    def _parse_atom(self) -> Filter:
        token = self._peek()
        if token.val == "." and self._peek(1) and self._peek(1).type == TokenType.IDENT:
            prop = self.tokens[self.pos + 1].val
            self.pos += 2
            return Prop(prop)
        elif (
            token.val == "."
            and self._peek(1)
            and self._peek(1).val == "["
            and self._peek(2)
            and self._peek(2).val == "]"
        ):
            self.pos += 3
            return Index()
        elif token.val == ".":
            self.pos += 1
            return Identity()
        elif token == Token(TokenType.PUNCT, "["):
            self._next()
            if self._peek() == Token(TokenType(TokenType.PUNCT), "]"):
                result = Array()
            else:
                result = Array(self._parse_pipe())
            self._next()
            return result
        elif token == Token(TokenType.PUNCT, "{"):
            return self._parse_object()
        elif token.type == TokenType.IDENT:
            if token.val == "null":
                self._next()
                return Literal(None)
            elif token.val == "true":
                self._next()
                return Literal(True)
            elif token.val == "false":
                self._next()
                return Literal(False)
            else:
                return self._parse_fn_call()
        elif token.type == TokenType.NUM:
            self._next()
            return Literal(token.val)
        elif token.type == TokenType.STR:
            self._next()
            return Literal(token.val)
        else:
            raise ValueError(f"invalid token {self.tokens[self.pos]}")

    def _parse_fn_call(self) -> Fn:
        name = self._peek().val
        fn = self.ctx.get(name)
        if not fn:
            raise ValueError(f"{name} undefined")

        self._next()
        args = []
        if self._peek() == Token(TokenType.PUNCT, "("):
            self._next()
            if self._peek() == Token(TokenType.PUNCT, ")"):
                self._next()
            else:
                args.append(self._parse_pipe())
                while self._peek() == Token(TokenType.PUNCT, ";"):
                    self._next()
                    args.append(self._parse_pipe())
                self._next()
        else:
            pass
        return fn(*args)

    def _parse_object(self) -> Filter:
        result = {}
        self._expect(Token(TokenType.PUNCT, "{"))
        while True:
            if self._peek() == Token(TokenType.PUNCT, "}"):
                self._next()
                break
            elif self._peek().type == TokenType.STR:
                key = self._peek().val
                self._next()
                self._expect(Token(TokenType.PUNCT, ":"))
                result[key] = self._parse_atom()
                if self._peek() == Token(TokenType.PUNCT, ","):
                    self._next()
            else:
                raise ValueError(f"invalid token {self.tokens[self.pos]}")
        return Object(result)

    def _peek(self, n: int = 0) -> Optional[Token]:
        if self.pos + n >= len(self.tokens):
            return
        return self.tokens[self.pos + n]

    def _next(self) -> Optional[Token]:
        token = self._peek()
        if token:
            self.pos += 1
        return token

    def _expect(self, token: Token):
        t = self._next()
        if t != token:
            raise ValueError(f"Expect {token}, got {t}")


def parse(expr: str) -> Optional[Filter]:
    parser = Parser(expr)
    return parser.parse()
