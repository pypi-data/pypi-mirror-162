"""Env."""

from __future__ import annotations

from logging import getLogger
from os import environ as osenviron
from re import compile as re_compile
from typing import Mapping, Pattern

from .yaml import yaml_implicit_type

logger = getLogger(__name__)


class Env:
    """Env."""

    YAML = "!env"
    PATTERN = re_compile(r"\$\{([^\}^\{]+)\}")

    @classmethod
    def as_yaml_type(
        cls,
        tag: str | None = None,
        *,
        env: Mapping[str, str] | None = None,
        pattern: Pattern | None = None,
    ):
        """As yaml type."""
        yaml_implicit_type(
            cls,
            tag or cls.YAML,
            pattern=pattern or cls.PATTERN,
            init=cls._yaml_init,
            env=env or osenviron,
        )

    @classmethod
    def _yaml_init(
        cls,
        loader,
        node,
        *,
        env: Mapping[str, str],
        pattern: Pattern,
    ):
        """From yaml."""
        value = loader.construct_scalar(node)
        match = pattern.findall(value)
        if not match:
            return value
        for group in match:
            variable = env.get(group, None)
            if variable is None:
                raise ValueError(f"No value for ${{{group}}}.")
            value = value.replace(f"${{{group}}}", variable)
        return value

    @classmethod
    def load(cls, path: str) -> Mapping[str, str]:
        """Env load."""
        with open(path, encoding="utf-8") as fin:
            return cls.loads(fin)

    @classmethod
    def loads(cls, stream) -> Mapping[str, str]:
        """Env loads."""
        result = {}
        while True:
            try:
                line = next(stream)
            except StopIteration:
                break
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            result[key] = value
        return result
