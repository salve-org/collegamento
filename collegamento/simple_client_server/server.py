from logging import Logger
from time import sleep
from typing import Any

from .misc import (
    USER_FUNCTION,
    Request,
    RequestQueueType,
    Response,
    ResponseQueueType,
)


class SimpleServer:
    """Handles input from the user and returns output from special functions. Not an external API."""

    def __init__(
        self,
        commands: dict[str, USER_FUNCTION],
        response_queue: ResponseQueueType,
        requests_queue: RequestQueueType,
        logger: Logger,
        priority_commands: list[str] = [],
    ) -> None:
        self.logger: Logger = logger
        self.logger.info("Starting server setup")

        self.response_queue: ResponseQueueType = response_queue
        self.requests_queue: RequestQueueType = requests_queue
        self.all_ids: list[int] = []
        self.newest_ids: dict[str, int] = {}
        self.newest_requests: dict[str, Request | None] = {}
        self.priority_commands: list[str] = priority_commands

        self.commands: dict[str, USER_FUNCTION] = commands
        for command in self.commands:
            self.newest_ids[command] = 0
            self.newest_requests[command] = None

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
        self.newest_ids[command] = id
        self.newest_requests[command] = message  # type: ignore
        self.logger.debug("Request stored for parsing")

    def cancel_all_ids_except_newest(self) -> None:
        self.logger.info("Cancelling all old id's")

        # NOTE: It used to be list comprehension but that was ugly
        ids = []
        for request in list(self.newest_requests.values()):
            if request is not None:
                ids.append(request["id"])

        for request in self.all_ids:
            if request in ids:
                self.logger.debug(f"Id {request} is newest of its command")
                continue

            self.logger.debug(
                f"Id {request} is an old request, sending simple respone"
            )
            self.simple_id_response(request)

        self.all_ids = []
        self.logger.debug("All ids list reset")

    def handle_request(self, request: Request) -> None:
        command: str = request["command"]
        id: int = self.newest_ids[command]
        result: Any  # noqa: F842

        command = request["command"]
        response: Response = {
            "id": id,
            "type": "response",
            "cancelled": False,
            "command": command,
        }

        if command == "add-command":
            self.commands[request["name"]] = request["function"]  # type: ignore
            response["result"] = None
            response["cancelled"] = True
            self.logger.debug("Response created")
            self.response_queue.put(response)
            self.newest_ids[command] = 0
            self.logger.info(f"Response sent for request of command {command}")
            return

        if command not in self.commands:
            self.logger.warning(f"Command {command} not recognized")
            response["result"] = None
            response["cancelled"] = True
        else:
            self.logger.debug(f"Running user function for command {command}")
            response["result"] = self.commands[command](self, request)

        self.logger.debug("Response created")
        self.response_queue.put(response)
        self.newest_ids[command] = 0
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
        self.cancel_all_ids_except_newest()

        # Actual work
        requests_list: list[Request] = [
            request
            for request in self.newest_requests.values()
            if request is not None
        ]

        def sort_func(request: Request) -> tuple[bool, int]:
            command_index: int = 0
            in_priority_commands: bool = (
                request["command"] in self.priority_commands
            )

            if in_priority_commands:
                command_index = self.priority_commands.index(
                    request["command"]
                )

            return (
                not in_priority_commands,
                command_index,
            )  # It it sorts False before True

        requests_list = sorted(requests_list, key=sort_func)

        for request in requests_list:
            if request is None:
                continue
            command: str = request["command"]
            self.logger.info(f"Handling request of command {command}")
            self.handle_request(request)
            self.newest_requests[command] = None
            self.logger.debug("Request completed")
