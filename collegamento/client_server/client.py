"""Defines the Client and Server class which provides a convenient and easy to use IPC interface.

>>> def test(*args):
...     return
>>> c = Client({"test": (test, True)})
>>> c.request("test")
>>> c.request("test")
>>> from time import sleep
>>> sleep(1)
>>> res = c.get_response("test")
>>> res
[{...}, {...}]
>>> assert len(res) == 2
>>> c.kill_IPC()
"""

from multiprocessing import Process, Queue, freeze_support
from random import randint

from .server import Server
from .utils import (
    COMMANDS_MAPPING,
    USER_FUNCTION,
    CollegamentoError,
    Request,
    RequestQueueType,
    Response,
    ResponseQueueType,
)


class Client:
    """An easy to use implementation for IPC in Python.

    The Client class is used to talk to the Server class and run commands as directed.

    The public API includes the following methods:
    - Client.add_command(name: str, command: USER_FUNCTION, multiple_requests: bool = False)
    - Client.request(command: str, **kwargs) -> None | int
    - Client.get_response(command: str) -> Response | list[Response] | None
    - Client.kill_IPC()
    """

    def __init__(
        self,
        commands: COMMANDS_MAPPING = {},
        id_max: int = 15_000,
        server_type: type = Server,
    ) -> None:
        """See tests, examples, and the file variant code to see how to give input.

        The most common input is commands and id_max. server_type is only really useful for wrappers."""

        self.all_ids: list[int] = []
        self.id_max: int = id_max

        # int corresponds to str and str to int = int -> str & str -> int
        self.current_ids: dict[str | int, int | str] = {}

        self.newest_responses: dict[str, list[Response]] = {}
        self.server_type: type = server_type

        self.commands: dict[str, tuple[USER_FUNCTION, bool]] = {}

        for command, func in commands.items():
            # We don't check types or length because beartype takes care of that for us
            if not isinstance(func, tuple):
                self.commands[command] = (func, False)
                self.newest_responses[command] = []
                continue

            self.commands[command] = func
            self.newest_responses[command] = []

        self.request_queue: RequestQueueType
        self.response_queue: ResponseQueueType
        self.main_process: Process
        self.create_server()

    def create_server(self):
        """Creates a Server and terminates the old one if it exists - internal API"""
        freeze_support()

        if hasattr(self, "main_process"):
            # If the old Process didn't finish instatiation we need to terminate the Process
            # so it doesn't try to access queues that no longer exist
            self.main_process.terminate()

            self.check_responses()
            self.all_ids = []  # The remaining ones will never have been finished

        self.request_queue = Queue()
        self.response_queue = Queue()
        self.main_process = Process(
            target=self.server_type,
            args=(
                self.commands,
                self.request_queue,
                self.response_queue,
            ),
            daemon=True,
        )
        self.main_process.start()

    def create_message_id(self) -> int:
        """Creates a Message id - internal API"""

        # In cases where there are many many requests being sent it may be faster to choose a
        # random id than to iterate through the list of id's and find an unclaimed one
        # NOTE: 0 is reserved for when there's no curent id's (self.current_ids)
        id: int = randint(1, self.id_max)
        while id in self.all_ids:
            id = randint(1, self.id_max)
        self.all_ids.append(id)

        if not self.main_process.is_alive():
            # No point in an id if the server's dead
            self.create_server()

        return id

    def request(self, command: str, **kwargs) -> None:
        """Sends the main process a request of type command with given kwargs - external API"""

        if command not in self.commands:
            raise CollegamentoError(
                f"Command {command} not in builtin commands. Those are {self.commands}!"
            )

        id: int = self.create_message_id()

        final_request: Request = {
            "id": id,
            "type": "request",
            "command": command,
        }
        final_request.update(**kwargs)

        if self.commands[command][1]:
            self.current_ids[id] = command

        self.current_ids[command] = id

        self.request_queue.put(final_request)

    def parse_response(self, res: Response) -> None:
        """Parses main process output and discards useless responses - internal API"""
        id: int = res["id"]
        self.all_ids.remove(id)

        if "command" not in res:
            return

        command: str = res["command"]

        if command == "add-command":
            return

        self.newest_responses[command].append(res)
        self.current_ids[command] = 0

        if self.commands[command][1]:
            self.current_ids.pop(id)
            return

        if id != self.current_ids[command]:
            return

    def check_responses(self) -> None:
        """Checks all main process output by calling parse_line() on each response - internal API"""
        while not self.response_queue.empty():
            self.parse_response(self.response_queue.get())

    def get_response(self, command: str) -> Response | list[Response] | None:
        """Checks responses and returns the current response of type command if it has been returned - external API"""
        if command not in self.commands:
            raise CollegamentoError(
                f"Cannot get response of command {command}, valid commands are {self.commands}"
            )

        self.check_responses()
        response: list[Response] = self.newest_responses[command]
        self.newest_responses[command] = []
        if not len(response):
            return None

        # If we know that the command doesn't allow multiple requests don't give a list
        if not self.commands[command][1]:
            return response[0]  # Will only ever be one

        return response

    def add_command(
        self,
        name: str,
        command: USER_FUNCTION,
        multiple_requests: bool = False,
    ) -> None:
        if name == "add-command":
            raise CollegamentoError(
                "Cannot add command add-command as it is a special builtin"
            )

        id: int = self.create_message_id()
        final_request: Request = {
            "id": id,
            "type": "request",
            "command": "add-command",
        }
        command_tuple: tuple[USER_FUNCTION, bool] = (
            command,
            multiple_requests,
        )
        final_request.update(**{"name": name, "function": command_tuple})

        self.request_queue.put(final_request)
        self.commands[name] = command_tuple
        self.newest_responses[name] = []

    def kill_IPC(self):
        """Kills the internal Process and frees up some storage and CPU that may have been used otherwise - external API"""
        self.main_process.terminate()

    def __del__(self):
        # Multiprocessing bugs arise if the Process is created, not saved, and not terminated
        self.main_process.terminate()
