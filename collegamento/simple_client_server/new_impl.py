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
from random import randint
from time import sleep

from beartype.typing import Any, Callable
from utils import (  # TODO: Relative import
    USER_FUNCTION,
    CollegamentoError,
    Request,
    RequestQueueType,
    Response,
    ResponseQueueType,
)


def command_sort_func(
    request: Request, priority_commands: list[str]
) -> tuple[bool, int]:
    command_index: int = 0
    in_priority_commands: bool = request["command"] in priority_commands

    if in_priority_commands:
        command_index = priority_commands.index(request["command"])

    return (
        not in_priority_commands,
        command_index,
    )  # It it sorts False before True


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
        self.newest_ids: dict[str, list[int]] = {}
        self.newest_requests: dict[str, list[Request]] = {}
        self.priority_commands: list[str] = priority_commands

        self.commands: dict[str, tuple[USER_FUNCTION, bool]] = commands
        for command, func_tuple in self.commands.items():
            self.newest_ids[command] = []
            self.newest_requests[command] = []

        self.logger.info("Server setup complete")

        while True:
            self.run_tasks()
            sleep(0.0025)

    def simple_id_response(self, id: int, cancelled: bool = True) -> None:
        self.logger.debug(f"Creating simple response for id {id}")
        response: Response = {
            "id": id,
            "type": "response",
            "cancelled": cancelled,
        }
        self.logger.debug(f"Sending simple response for id {id}")
        self.response_queue.put(response)
        self.logger.info(f"Simple response for id {id} sent")

    def parse_line(self, message: Request) -> None:
        self.logger.debug("Parsing Message from user")
        id: int = message["id"]

        if message["type"] != "request":
            self.logger.warning(
                f"Unknown type {type}. Sending simple response"
            )
            self.simple_id_response(id)
            self.logger.debug(f"Simple response for id {id} sent")
            return

        self.logger.info(f"Mesage with id {id} is of type request")
        self.all_ids.append(id)
        command: str = message["command"]  # type: ignore

        if not self.commands[command][1]:
            self.newest_ids[command] = []
            self.newest_requests[command] = []

        self.newest_ids[command].append(id)
        self.newest_requests[command].append(message)
        self.logger.debug("Request stored for parsing")

    def cancel_old_ids(self) -> None:
        self.logger.info("Cancelling all old id's")

        accepted_ids = [
            request["id"]
            for request_list in list(self.newest_requests.values())
            for request in request_list
        ]

        for request in self.all_ids:
            if request in accepted_ids:
                self.logger.debug(
                    f"Id {request} is an either the newest request or the command allows multiple requests"
                )
                continue

            self.logger.debug(
                f"Id {request} is an unwanted request, sending simple respone"
            )
            self.simple_id_response(request)

        self.all_ids = []
        self.logger.debug("All ids list cleaned up")

    def handle_request(self, request: Request) -> None:
        command: str = request["command"]
        id: int = request["id"]
        result: Any  # noqa: F842

        command = request["command"]
        response: Response = {
            "id": id,
            "type": "response",
            "cancelled": False,
            "command": command,
        }

        if command == "add-command":
            request_name: str = request["name"]  # type: ignore

            request_tuple: tuple[USER_FUNCTION, bool] = request["function"]  # type: ignore
            self.commands[request_name] = request_tuple
            response["result"] = None
            response["cancelled"] = True
            self.logger.debug("Response created")
            self.response_queue.put(response)
            self.newest_ids[command].remove(id)
            self.logger.info(f"Response sent for request of command {command}")
            return

        if command not in self.commands:
            self.logger.warning(f"Command {command} not recognized")
            response["result"] = None
            response["cancelled"] = True
        else:
            self.logger.debug(f"Running user function for command {command}")
            response["result"] = self.commands[command][0](self, request)

        self.logger.debug("Response created")
        self.response_queue.put(response)
        self.newest_ids[command].remove(id)
        self.logger.info(f"Response sent for request of command {command}")

    def run_tasks(self) -> None:
        if self.requests_queue.empty():
            return

        self.logger.debug("New request in queue")
        while not self.requests_queue.empty():
            self.logger.debug("Parsing request")
            self.parse_line(self.requests_queue.get())

        if not self.all_ids:
            self.logger.debug("All requests were notifications")

        self.logger.debug("Cancelling all old id's")
        self.cancel_old_ids()

        requests_list: list[Request] = [
            request
            for request_list in self.newest_requests.values()
            if request_list
            for request in request_list
        ]

        requests_list = sorted(
            requests_list,
            key=lambda request: command_sort_func(
                request, self.priority_commands
            ),
        )

        for request in requests_list:
            if request is None:
                continue
            command: str = request["command"]
            self.logger.info(f"Handling request of command {command}")
            self.handle_request(request)
            self.newest_requests[command].remove(request)
            self.logger.debug("Request completed")


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

        self.logger.info("Creating Server")
        self.request_queue: Queue
        self.response_queue: Queue
        self.main_process: Process
        self.create_server()
        self.logger.info("Initialization is complete")

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
                self.logger,
            ),
            daemon=True,
        )
        self.main_process.start()

    def log_exception(self, exception_str: str) -> None:
        """Logs an exception and raises a CollegamentoError - internal API"""
        self.logger.exception(exception_str)
        raise CollegamentoError(exception_str)

    def create_message_id(self) -> int:
        """Creates a Message id - internal API"""
        self.logger.info("Creating message for server")

        # In cases where there are many many requests being sent it may be faster to choose a
        # random id than to iterate through the list of id's and find an unclaimed one
        id = randint(1, self.id_max)  # 0 is reserved for the empty case
        while id in self.all_ids:
            id = randint(1, self.id_max)
        self.all_ids.append(id)

        self.logger.debug("ID for message created")

        if not self.main_process.is_alive():
            # No point in an id if the server's dead
            self.logger.critical(
                "Server was killed at some point, creating server"
            )
            self.create_server()

        return id

    def request(
        self,
        request_details: dict,
    ) -> int | None:
        """Sends the main_server a request of type command with given kwargs - external API"""
        self.logger.debug("Beginning request")

        # NOTE: this variable could've been a standalone line but I thought it would just be better
        # to use the walrus operator. No point in a language feature if its never used. Plus,
        # it also looks quite nice :D
        if (command := request_details["command"]) not in self.commands:
            self.logger.exception(
                f"Command {command} not in builtin commands. Those are {self.commands}!"
            )
            raise CollegamentoError(
                f"Command {command} not in builtin commands. Those are {self.commands}!"
            )

        self.logger.info("Creating request for server")

        id: int = self.create_message_id()

        # self.current_ids[command] = id
        # final_request: Request = {
        #     "id": id,
        #     "type": "request",
        #     "command": command,
        # }
        # final_request.update(request_details)  # type: ignore
        # self.logger.debug(f"Request created: {final_request}")

        # self.request_queue.put(final_request)
        # self.logger.info("Message sent")


    def kill_IPC(self):
        """Kills the internal Process and frees up some storage and CPU that may have been used otherwise - external API"""
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
