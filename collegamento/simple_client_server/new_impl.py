"""Defines the Client and Server class which provides a convenient and easy to use IPC interface.

>>> def test(*args):
...     return
>>> c = Client({"test": (test, True)})
>>> c.request({"command": "test"})
>>> from time import sleep
>>> sleep(1)
>>> assert c.get_response("test") is not None
>>> c.kill_IPC()
"""

from logging import Logger, getLogger
from multiprocessing import Process, Queue, freeze_support
from time import sleep

from beartype.typing import Any, Callable

from misc import (
    USER_FUNCTION,
    CollegamentoError,
    Request,
    RequestQueueType,
    Response,
    ResponseQueueType,
)  # TODO: Relative import


class Server:
    """A basic and multipurpose server that can be easily subclassed for your specific needs."""
    def __init__(
        self,
        commands: dict[str, tuple[USER_FUNCTION, bool]],
        requests_queue: RequestQueueType,
        response_queue: ResponseQueueType,
        logger: Logger,
        priority_commands: list[str] = [],  # Only used by subclasses
    ) -> None:
        self.logger: Logger = logger
        self.logger.info("Starting server setup")

        self.response_queue: ResponseQueueType = response_queue
        self.requests_queue: RequestQueueType = requests_queue
        self.all_ids: list[int] = []
        self.newest_ids: dict[str, int] = {}
        self.newest_requests: dict[str, Request | None] = {}
        self.priority_commands: list[str] = priority_commands

class Client:
    """An easy to use implementation for IPC in Python.

    The Client class is used to talk to the Server class and run commands as directed.

    The public API includes the following methods:
    - Client.add_command(name: str, command: USER_FUNCTION, multiple_requests: bool = False)
    - Client.request(request_details: dict) -> None | int
    - Client.get_response(command: str | int) -> Response | list[Response]
    - Client.kill_IPC()
    """

    def __init__(
        self,
        commands: dict[str, USER_FUNCTION | tuple[USER_FUNCTION, bool]] = {},
        id_max: int = 15_000,
        server_type: type = Server,
    ) -> None:
        """To initiate the Client class, you are not required to give any input.

        Should you choose to give input, the
        """
        self.logger: Logger = getLogger("IPC")
        self.logger.info("Initiating Client")

        self.all_ids: list[int] = []
        self.id_max = id_max

        # If the user searches by a command they give a str and get a single Response as
        # one can only search by command if it allows multiple Requests they give an int
        # which corresponds to a Requests from a command that allows multiple Requests
        # and it gives all Responses of that command
        self.current_ids: dict[str | int, int | str] = {}

        self.newest_responses: dict[str, list[Response]] = {}
        self.server_type = server_type

        self.logger.debug("Parsing commands")
        self.commands: dict[str, tuple[USER_FUNCTION, bool]] = {}

        for command, func in commands.items():
            # We don't check types or length because beartype takes care of that for us
            if not isinstance(func, tuple):
                self.commands[command] = (func, False)
                continue

            self.commands[command] = func

        self.request_queue: Queue
        self.response_queue: Queue
        self.main_process: Process
        self.logger.info("Creating Server")
        self.create_server()
        self.logger.info("Initialization is complete")

    def create_server(self):
        freeze_support()

        if hasattr(self, "main_process"):
            # If the old Process didn't finish instatiation we need to terminate the Process
            # so it doesn't try to access queues that no longer exist
            self.main_process.terminate()

        self.request_queue = Queue()
        self.response_queue = Queue()
        self.main_process = Process(
            target=self.server_type,
            args=(
                self.commands,
                self.request_queue,
                self.response_queue,
                self.logger,
            ),
            daemon=True,
        )
        self.main_process.start()

    def log_exception(self, exception_str: str) -> None:
        """Logs an exception and raises a CollegamentoError"""
        self.logger.exception(exception_str)
        raise CollegamentoError(exception_str)

    def kill_IPC(self):
        """Kills the internal Process and frees up some storage and CPU that may have been used otherwise"""
        self.main_process.terminate()

    def __del__(self):
        # Multiprocessing bugs arise if the Process is created, not saved, and not terminated
        self.main_process.terminate()


if __name__ == "__main__":
    from test_func import foo

    # Mini tests
    Client({"foo": (foo, True)})
    x = Client({"foo": foo})
    sleep(1)
    x.create_server()
    Client()
    Client().kill_IPC()
    Client().create_server()
    sleep(1)

    # from doctest import testmod
    # testmod()
