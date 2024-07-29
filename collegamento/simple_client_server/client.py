from logging import Logger, getLogger
from multiprocessing import Process, Queue, freeze_support
from random import randint

from .misc import (
    USER_FUNCTION,
    CollegamentoError,
    Notification,
    Request,
    RequestQueueType,
    Response,
    ResponseQueueType,
)
from .server import SimpleServer


class SimpleClient:
    """The IPC class is used to talk to the server and run commands. The public API includes the following methods:
    - SimpleClient.notify_server()
    - SimpleClient.request()
    - SimpleClient.add_command()
    - SimpleClient.kill_IPC()
    """

    def __init__(
        self,
        commands: dict[str, USER_FUNCTION],
        id_max: int = 15_000,
        server_type: type = SimpleServer,
    ) -> None:
        self.all_ids: list[int] = []
        self.id_max = id_max
        self.current_ids: dict[str, int] = {}
        self.newest_responses: dict[str, Response | None] = {}
        self.server_type: type[SimpleServer] = server_type

        self.commands = commands
        for command in self.commands:
            self.current_ids[command] = 0
            self.newest_responses[command] = None

        self.logger: Logger = getLogger("IPC")
        self.logger.info("Creating server")
        self.response_queue: ResponseQueueType = Queue()
        self.requests_queue: RequestQueueType = Queue()
        self.main_server: Process
        self.create_server()
        self.logger.info("Initialization is complete")

    def create_server(self) -> None:
        """Creates the main_server through a subprocess - internal API"""
        freeze_support()
        server_logger = getLogger("Server")
        self.main_server = Process(
            target=self.server_type,
            args=(
                self.commands,
                self.response_queue,
                self.requests_queue,
                server_logger,
            ),
            daemon=True,
        )
        self.main_server.start()
        self.logger.info("Server created")

    def create_message_id(self) -> int:
        """Creates a Message based on the args and kwawrgs provided. Highly flexible. - internal API"""
        self.logger.info("Creating message for server")
        id = randint(1, self.id_max)  # 0 is reserved for the empty case
        while id in self.all_ids:
            id = randint(1, self.id_max)
        self.all_ids.append(id)

        self.logger.debug("ID for message created")

        if not self.main_server.is_alive():
            # No point in an id if the server's dead
            self.logger.critical(
                "Server was killed at some point, creating server"
            )
            self.create_server()

        return id

    def notify_server(
        self,
        notification_dict: dict,
    ) -> None:
        self.logger.info("Creating notification for server")

        id: int = self.create_message_id()
        final_notification: Notification = {
            "id": id,
            "type": "notification",
        }
        final_notification.update(notification_dict)
        self.logger.debug(f"Notification created: {final_notification}")
        self.requests_queue.put(final_notification)
        self.logger.info("Message sent")

    def request(
        self,
        request_details: dict,
    ) -> None:
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

        self.current_ids[command] = id
        final_request: Request = {
            "id": id,
            "type": "request",
            "command": command,
        }
        final_request.update(request_details)  # type: ignore
        self.logger.debug(f"Request created: {final_request}")

        self.requests_queue.put(final_request)
        self.logger.info("Message sent")

    def parse_response(self, res: Response) -> None:
        """Parses main_server output line and discards useless responses - internal API"""
        self.logger.debug("Parsing server response")
        id = res["id"]
        self.all_ids.remove(id)

        if "command" not in res:
            self.logger.info("Response was notification response")
            return

        command = res["command"]

        if command == "add-command":
            return

        if id != self.current_ids[command]:
            self.logger.info("Response is from old request")
            return

        self.logger.info(f"Response is useful for command type: {command}")
        self.current_ids[command] = 0
        self.newest_responses[command] = res

    def check_responses(self) -> None:
        """Checks all main_server output by calling IPC.parse_line() on each response - internal API"""
        self.logger.debug("Checking responses")
        while not self.response_queue.empty():
            self.parse_response(self.response_queue.get())

    def get_response(self, command: str) -> Response | None:
        """Checks responses and returns the current response of type command if it has been returned - external API"""
        self.logger.info(f"Getting response for type: {command}")
        if command not in self.commands:
            self.logger.exception(
                f"Cannot get response of command {command}, valid commands are {self.commands}"
            )
            raise CollegamentoError(
                f"Cannot get response of command {command}, valid commands are {self.commands}"
            )

        self.check_responses()
        response: Response | None = self.newest_responses[command]
        self.newest_responses[command] = None
        self.logger.info("Response retrieved")
        return response

    def add_command(self, name: str, command: USER_FUNCTION) -> None:
        if name == "add-command":
            self.logger.exception(
                "Cannot add command add-command as it is a special builtin"
            )
            raise CollegamentoError(
                "Cannot add command add-command as it is a special builtin"
            )

        id: int = self.create_message_id()
        final_request: Request = {
            "id": id,
            "type": "request",
            "command": "add-command",
        }
        final_request.update({"name": name, "function": command})  # type: ignore
        self.logger.debug(f"Add Command Request created: {final_request}")

        self.requests_queue.put(final_request)
        self.logger.info("Message sent")
        self.commands[name] = command

    def kill_IPC(self) -> None:
        """Kills the main_server when salve_ipc's services are no longer required - external API"""
        self.logger.info("Killing server")
        self.main_server.kill()
