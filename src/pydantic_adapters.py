import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import pygame
from pydantic_core import CoreSchema, core_schema

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler


class PydanticAdapter[T, PDT](ABC):
    proxy_schema: CoreSchema
    to_json: bool = False

    @classmethod
    def __get_pydantic_core_schema__(  # ruff:ignore[bad-dunder-method-name]
        cls, source: type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        obj = cls()

        return core_schema.no_info_after_validator_function(
            obj._validate,
            core_schema.str_schema(strip_whitespace=True),
            serialization=core_schema.plain_serializer_function_ser_schema(
                obj._serialize, return_schema=cls.proxy_schema
            ),
        )

    @abstractmethod
    def _validate(self, value: str) -> T: ...

    @abstractmethod
    def _serialize(self, value: T) -> PDT: ...


class Vector2Adapter(PydanticAdapter[pygame.Vector2, list[float]]):
    proxy_schema = core_schema.list_schema(
        core_schema.float_schema(), min_length=2, max_length=2
    )

    def _validate(self, value: str) -> pygame.Vector2:  # ruff:ignore[no-self-use]
        return pygame.Vector2(json.loads(value))

    def _serialize(self, value: pygame.Vector2) -> list[float]:  # ruff:ignore[no-self-use]
        return list(value)


type Vector2 = Annotated[pygame.Vector2, Vector2Adapter()]


class SurfaceAdapter(PydanticAdapter[pygame.Surface, str]):
    proxy_schema = core_schema.str_schema(strip_whitespace=True)

    def _validate(self, value: str) -> pygame.Surface:
        self._value = value

        return pygame.image.load(Path("static", "images", value))

    def _serialize(self, value: pygame.Surface) -> str:  # ruff:ignore[unused-method-argument]
        return self._value


type Surface = Annotated[pygame.Surface, SurfaceAdapter()]
