from multiprocessing.queues import Queue as GenericQueueClass
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

from beartype.typing import Callable


class Message(TypedDict):
    """Base class for messages in and out of the server"""

    id: int
    type: str  # Can be "request", "response", "notification"


class Request(Message):
    """Request from the IPC class to the server with command specific input"""

    command: str


class Notification(Message):
    """Notifies the server to store or update its storage of something"""

    contents: NotRequired[Any]


class Response(Message):
    """Server responses to requests and notifications"""

    cancelled: bool
    command: NotRequired[str]
    result: NotRequired[Any]


USER_FUNCTION = Callable[[Request], Any]

if TYPE_CHECKING:
    ResponseQueueType = GenericQueueClass[Response]
    RequestQueueType = GenericQueueClass[Request | Notification]
# Else, this is CPython < 3.12. We are now in the No Man's Land
# of Typing. In this case, avoid subscripting "GenericQueue". Ugh.
else:
    ResponseQueueType = GenericQueueClass
    RequestQueueType = GenericQueueClass


class CollegamentoError(Exception): ...  # I don't like the boilerplate either
