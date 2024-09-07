"""Defines the Server class which is the butter to the bread that is the Client."""

from time import sleep

from beartype.typing import Any

from .utils import (
    USER_FUNCTION,
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
        priority_commands: list[str] = [],  # Only used by subclasses
    ) -> None:
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

        while True:
            self.run_tasks()
            sleep(0.0025)

    def simple_id_response(self, id: int, cancelled: bool = True) -> None:
        response: Response = {
            "id": id,
            "type": "response",
            "cancelled": cancelled,
        }
        self.response_queue.put(response)

    def parse_line(self, message: Request) -> None:
        id: int = message["id"]

        if message["type"] != "request":
            self.simple_id_response(id)
            return

        command: str = message["command"]

        if command == "add-command":
            request_name: str = message["name"]  # type: ignore

            request_tuple: tuple[USER_FUNCTION, bool] = message["function"]  # type: ignore
            self.commands[request_name] = request_tuple
            self.newest_requests[request_name] = []
            self.newest_ids[request_name] = []
            self.simple_id_response(id)
            return

        self.all_ids.append(id)

        if not self.commands[command][1]:
            self.newest_ids[command] = []
            self.newest_requests[command] = []

        self.newest_ids[command].append(id)
        self.newest_requests[command].append(message)

    def cancel_old_ids(self) -> None:
        accepted_ids: list[int] = [
            request["id"]
            for request_list in list(self.newest_requests.values())
            for request in request_list
        ]

        for request in self.all_ids:
            if request in accepted_ids:
                continue

            self.simple_id_response(request)

        self.all_ids = []

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

        if command not in self.commands:
            response["result"] = None
            response["cancelled"] = True
        else:
            response["result"] = self.commands[command][0](self, request)

        self.response_queue.put(response)
        self.newest_ids[command].remove(id)

    def run_tasks(self) -> None:
        if self.requests_queue.empty():
            return

        while not self.requests_queue.empty():
            self.parse_line(self.requests_queue.get())

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
            self.handle_request(request)
            self.newest_requests[command].remove(request)
