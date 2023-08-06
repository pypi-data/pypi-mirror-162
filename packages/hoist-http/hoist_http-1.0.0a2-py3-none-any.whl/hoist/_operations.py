from typing import NamedTuple, Type, TypeVar, get_type_hints

from ._typing import Operations, Operator, Payload, Schema
from .exceptions import SchemaValidationError

T = TypeVar("T")


class _Print(NamedTuple):
    text: str


async def _print(payload: _Print):
    print(payload.text)


BASE_OPERATIONS: Operations = {"print": _print}


def verify_schema(schema: Schema, data: Payload) -> None:
    """Verify that a payload matches the schema."""
    for key, typ in schema.items():
        value = data.get(key)
        vtype = type(value) if value is not None else None

        if type(typ) is tuple:
            if vtype not in typ:
                raise SchemaValidationError(current=vtype, needed=typ)
            continue

        if vtype is not typ:
            raise SchemaValidationError(current=vtype, needed=typ)


async def call_operation(op: Operator[T], payload: Payload) -> None:
    """Call an operation."""
    hints = get_type_hints(op)
    cl: Type[T] = hints[tuple(hints.keys())[0]]

    verify_schema(get_type_hints(cl), payload)
    await op(cl(**payload))
