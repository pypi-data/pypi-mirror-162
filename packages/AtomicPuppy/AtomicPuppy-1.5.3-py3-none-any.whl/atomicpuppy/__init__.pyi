import json
from typing import Any, Callable, Dict, List, Optional, Union

from enum import Enum
from uuid import UUID

from requests import Response
from atomicpuppy.errors import (
    FatalError,
    HttpClientError,
    HttpNotFoundError,
    InvalidDataException,
    RejectedMessageException,
    StreamNotFoundError,
    UrlError,
)

class Event:
    id: UUID
    type: str
    data: Dict[str, str]
    stream: str
    sequence: Optional[int]
    metadata: Dict[str, str]
    correlation_id: Optional[str]
    published_sequence: Optional[int]
    published_stream: Optional[str]
    link_metadata: Optional[Dict[Any, Any]]
    def __init__(
        self,
        id: UUID,
        type: str,
        data: Dict[str, str],
        stream: str,
        sequence: Optional[int],
        metadata: Dict[str, str] = None,
        correlation_id: Optional[str] = None,
        published_sequence: Optional[int] = None,
        published_stream: Optional[str] = None,
        link_metadata: Optional[Dict[Any, Any]] = None,
    ): ...
    @property
    def location(self) -> str: ...
    def __str__(self) -> str: ...

class AtomicPuppy:
    def __init__(
        self,
        cfg_file: Union[Dict[str, Any], str],
        callback: Callable[[Event], None],
        loop=None,
        username=Optional[str],
        password=Optional[str],
    ):
        """
        cfg_file: dictionary or filename or yaml text
        """
        ...
    def set_exception_handler(self, handler) -> None: ...
    def start(self, run_once=False): ...
    def stop(self): ...

class EventFinder:
    def __init__(
        self,
        cfg_file: Union[Dict[str, Any], str],
        loop: None,
        username: Optional[str] = ...,
        password: Optional[str] = ...,
    ) -> None: ...
    async def find_backwards(
        self,
        stream: str,
        predicate: Callable[[Event], bool],
        predicate_label: str = ...,
    ): ...

class ExceptionCause(Enum):
    counter: str
    handler: str

class EventPublisher:
    def __init__(
        self, host: str, port: str, username=Optional[str], password=Optional[str]
    ): ...
    def post(self, event: Event, correlation_id: Optional[str] = None) -> Response: ...
    def post_multiple(self, events: List[Event]): ...
    def batch_create(self, events: List[Event]): ...

class EventStoreJsonEncoder(json.JSONEncoder):
    def default(self, o) -> str: ...

class EventCounter:
    def __setitem__(self, stream: str, event: Event) -> None: ...
    def __getitem__(self, stream: str) -> int: ...

class RedisCounter(EventCounter):
    def __init__(self, host: str, port: str, instance: str) -> None: ...
    def __getitem__(self, stream: str) -> int: ...
    def __setitem__(self, stream: str, val: int) -> None: ...
