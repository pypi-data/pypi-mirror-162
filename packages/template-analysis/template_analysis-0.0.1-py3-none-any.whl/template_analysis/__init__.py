from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Literal, Union


@dataclass(frozen=True)
class Unique:
    value: str
    id: int

    def to_template(self) -> TemplatePart:
        return Variable(self.id)

    def is_unique(self) -> Literal[True]:
        return True

    def to_string(self) -> str:
        return self.value


@dataclass(frozen=True)
class Match:
    value: str

    def to_template(self) -> TemplatePart:
        return PlainText(self.value)

    def is_unique(self) -> Literal[False]:
        return False

    def to_string(self) -> str:
        return self.value


@dataclass(frozen=True)
class Variable:
    id: int

    def to_format_string(self) -> str:
        return "{}"


@dataclass(frozen=True)
class PlainText:
    value: str

    def to_format_string(self) -> str:
        return self.value


Block = Union[Unique, Match]
TemplatePart = Union[PlainText, Variable]


@dataclass
class Template:
    parts: list[TemplatePart]

    def to_format_string(self) -> str:
        return "".join(part.to_format_string() for part in self.parts)


@dataclass(frozen=True)
class AnalyzerResult:
    template: Template
    args: list[list[str]]

    def to_format_string(self) -> str:
        return self.template.to_format_string()


@dataclass
class Analyzer:
    text: str
    pos: int
    count_unique: int
    blocks: list[Block]

    @classmethod
    def create(cls, text: str) -> Analyzer:
        return cls(text, pos=0, count_unique=0, blocks=[])

    def append(self, type: Literal["match", "unique"], size: int) -> None:
        start = self.pos
        stop = self.pos + size
        if type == "match":
            self.blocks.append(Match(self.text[start:stop]))
        elif type == "unique":
            self.blocks.append(
                Unique(self.text[start:stop], self.count_unique)
            )
            self.count_unique += 1
        self.pos += size

    def to_template(self) -> Template:
        return Template([block.to_template() for block in self.blocks])

    def to_args(self) -> list[str]:
        return [
            block.to_string() for block in self.blocks if block.is_unique()
        ]

    @classmethod
    def analyze(cls, strings: list[str]) -> AnalyzerResult:
        if len(strings) == 1:
            return AnalyzerResult(
                template=Template([PlainText(strings[0])]),
                args=[[]],
            )
        elif len(strings) == 2:
            return cls.analyze_two_strings(strings[0], strings[1])

        raise NotImplementedError(
            "Analyze more than two strings are not implemented yet."
        )

    @classmethod
    def analyze_two_strings(cls, string1: str, string2: str) -> AnalyzerResult:
        matcher = difflib.SequenceMatcher(None, string1, string2)
        blocks = matcher.get_matching_blocks()
        analyzer_a = cls.create(string1)
        analyzer_b = cls.create(string2)

        for block in blocks:
            while (unmatch_length := block.a - analyzer_a.pos) > 0:
                analyzer_a.append("unique", unmatch_length)
            analyzer_a.append("match", block.size)

            while (unmatch_length := block.b - analyzer_b.pos) > 0:
                analyzer_b.append("unique", unmatch_length)
            analyzer_b.append("match", block.size)

        template_a = analyzer_a.to_template()
        template_b = analyzer_b.to_template()
        vars_a = analyzer_a.to_args()[:]
        vars_b = analyzer_b.to_args()[:]

        assert template_a == template_b, (
            "Guessed templates are mismatch: " f"{template_a} != {template_b}"
        )

        return AnalyzerResult(template_a, [vars_a, vars_b])
