"""Summary."""
import dataclasses
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Union

import jsons

from ergo.scope import Scope


@dataclass
class Message:
    data: Any = field(default=None)
    key: Optional[str] = None
    log: List = field(default_factory=list)
    scope: Scope = field(default_factory=Scope)
    error: Optional[Dict[str, str]] = None
    traceback: Optional[str] = None


def decodes(s: str) -> Message:
    return decode(**json.loads(s))


def decode(**kwargs) -> Message:
    # if kwargs includes `data`, assume this message was sent by an upstream component, and the other kwargs are
    #   metadata
    # otherwise, assume this message came from outside of ergo, and bind all kwargs to `data`.
    if "data" not in kwargs:
        kwargs = {"data": kwargs or None}
    return jsons.load(kwargs, cls=Message)


def encodes(data: Union[Message, Iterable[Message]]) -> str:
    return json.dumps(data, cls=ErgoEncoder)


class ErgoEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
