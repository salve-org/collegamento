from beartype.claw import beartype_this_package

beartype_this_package()

from .files_variant import FileClient, FileServer  # noqa: F401, E402
from .simple_client_server import (  # noqa: F401, E402
    COMMANDS_MAPPING,
    USER_FUNCTION,
    Client,
    CollegamentoError,
    Request,
    RequestQueueType,
    Response,
    ResponseQueueType,
    Server,
)
