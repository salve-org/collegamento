from multiprocessing.queues import Queue as GenericQueueClass
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict
from enum import Flag, auto

from beartype.typing import Callable


class CollegamentoFlags(Flag):
    MULTI_REQUESTS = auto()
    POOL = MULTI_REQUESTS | auto()


class Message(TypedDict):
    """Base class for messages in and out of the server"""

    id: int
    type: str  # Can be "request" or "response"


class Request(Message):
    """Request from the IPC class to the server with command specific input"""

    command: str


class Response(Message):
    """Server responses to requests and notifications"""

    cancelled: bool
    command: NotRequired[str]
    result: NotRequired[Any]


USER_FUNCTION = Callable[["SimpleServer", Request], Any]  # type: ignore
COMMANDS_MAPPING = dict[
    str, USER_FUNCTION | tuple[USER_FUNCTION, bool]
]  # if bool is true the command allows multiple requests

if TYPE_CHECKING:
    ResponseQueueType = GenericQueueClass[Response]
    RequestQueueType = GenericQueueClass[Request]
# Else, this is CPython < 3.12. We are now in the No Man's Land
# of Typing. In this case, avoid subscripting "GenericQueue". Ugh.
else:
    ResponseQueueType = GenericQueueClass
    RequestQueueType = GenericQueueClass


class CollegamentoError(Exception): ...  # I don't like the boilerplate either
