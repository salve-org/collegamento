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

from multiprocessing import Process, Queue, freeze_support
from random import randint
from time import sleep

from .server import Server
from .utils import (
    COMMANDS_MAPPING,
    USER_FUNCTION,
    CollegamentoError,
    Request,
    Response,
)


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
        commands: COMMANDS_MAPPING = {},
        id_max: int = 15_000,
        server_type: type = Server,
    ) -> None:
        """To initiate the Client class, you are not required to give any input.

        Should you choose to give input, the options are as follows:
        TODO: update the docstring
        """

        self.all_ids: list[int] = []
        self.id_max = id_max

        # If the user searches by a command they give a str and get a single Response as
        # one can only search by command if it allows multiple Requests they give an int
        # which corresponds to a Requests from a command that allows multiple Requests
        # and it gives all Responses of that command
        self.current_ids: dict[str | int, int | str] = {}

        self.newest_responses: dict[str, list[Response]] = {}
        self.server_type = server_type

        self.commands: dict[str, tuple[USER_FUNCTION, bool]] = {}

        for command, func in commands.items():
            # We don't check types or length because beartype takes care of that for us
            if not isinstance(func, tuple):
                self.commands[command] = (func, False)
                self.newest_responses[command] = []
                continue

            self.commands[command] = func
            self.newest_responses[command] = []

        self.request_queue: Queue
        self.response_queue: Queue
        self.main_process: Process
        self.create_server()

    def create_server(self):
        """Creates a Server and terminates the old one if it exists - internal API"""
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
            ),
            daemon=True,
        )
        self.main_process.start()

    def create_message_id(self) -> int:
        """Creates a Message id - internal API"""

        # In cases where there are many many requests being sent it may be faster to choose a
        # random id than to iterate through the list of id's and find an unclaimed one
        id = randint(1, self.id_max)  # 0 is reserved for the empty case
        while id in self.all_ids:
            id = randint(1, self.id_max)
        self.all_ids.append(id)

        if not self.main_process.is_alive():
            # No point in an id if the server's dead
            self.create_server()

        return id

    def request(
        self,
        request_details: dict,
    ) -> None:
        """Sends the main process a request of type command with given kwargs - external API"""

        command = request_details["command"]
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
        final_request.update(request_details)

        if self.commands[command][1]:
            self.current_ids[id] = command

        self.current_ids[command] = id

        self.request_queue.put(final_request)

    def parse_response(self, res: Response) -> None:
        """Parses main process output and discards useless responses - internal API"""
        id = res["id"]
        self.all_ids.remove(id)

        if "command" not in res:
            return

        command = res["command"]

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

    def get_response(self, command: str) -> list[Response]:
        """Checks responses and returns the current response of type command if it has been returned - external API"""
        if command not in self.commands:
            raise CollegamentoError(
                f"Cannot get response of command {command}, valid commands are {self.commands}"
            )

        self.check_responses()
        response: list[Response] = self.newest_responses[command]
        self.newest_responses[command] = []
        # TODO: if we know that the command doesn't allow multiple requests don't give a list
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
        command_tuple = (command, multiple_requests)
        final_request.update({"name": name, "function": command_tuple})  # type: ignore

        self.request_queue.put(final_request)
        self.commands[name] = command_tuple
        self.newest_responses[name] = []

    def kill_IPC(self):
        """Kills the internal Process and frees up some storage and CPU that may have been used otherwise - external API"""
        self.main_process.terminate()

    def __del__(self):
        # Multiprocessing bugs arise if the Process is created, not saved, and not terminated
        self.main_process.terminate()


if __name__ == "__main__":
    from test_func import foo

    # Mini tests
    Client({"foo": foo})
    x = Client({"foo": (foo, True), "foo2": foo})

    x.request({"command": "foo"})
    x.request({"command": "foo"})
    x.request({"command": "foo2"})
    x.request(
        {"command": "foo2"}
    )  # If you see six "Foo called"'s, thats bad news bears
    x.add_command("foo3", foo)
    x.request({"command": "foo3"})
    x.add_command("foo4", foo, True)
    x.request({"command": "foo4"})
    x.request({"command": "foo4"})

    sleep(1)

    x.check_responses()  # Not necessary, we're just checking that doing
    # this first doesn't break get_response

    foo_r: list[Response] = x.get_response("foo")
    foo_two_r: list[Response] = x.get_response("foo2")
    foo_three_r: list[Response] = x.get_response("foo3")
    foo_four_r: list[Response] = x.get_response("foo4")

    assert len(foo_r) == 2
    assert len(foo_two_r) == 1
    assert len(foo_three_r) == 1
    assert len(foo_four_r) == 2

    x.check_responses()
    x.create_server()

    Client()
    Client({"foo": foo}).request({"command": "foo"})
    Client().kill_IPC()
    Client().create_server()

    sleep(1)

    # from doctest import testmod
    # testmod()
