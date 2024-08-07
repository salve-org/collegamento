from logging import Logger
from multiprocessing.queues import Queue as GenericQueueClass
from typing import NotRequired

from .simple_client_server import (
    USER_FUNCTION,
    CollegamentoError,
    Request,
    SimpleClient,
    SimpleServer,
)


class FileRequest(Request):
    # There may be commands that don't require a file but some might
    file: NotRequired[str]


def update_files(server: "FileServer", request: Request) -> None:
    file: str = request["file"]  # type: ignore

    if request["remove"]:  # type: ignore
        server.logger.info(f"File {file} was requested for removal")
        server.files.pop(file)
        server.logger.info(f"File {file} has been removed")
    else:
        contents: str = request["contents"]  # type: ignore
        server.files[file] = contents
        server.logger.info(f"File {file} has been updated with new contents")


class FileClient(SimpleClient):
    """File handling variant of SImpleClient. Extra methods:
    - FileClient.update_file()
    - FileClient.remove_file()
    """

    def __init__(
        self, commands: dict[str, USER_FUNCTION], id_max: int = 15_000
    ) -> None:
        self.files: dict[str, str] = {}

        commands["FileNotification"] = update_files

        super().__init__(commands, id_max, FileServer)

        self.priority_commands = ["FileNotification"]

    def create_server(self) -> None:
        """Creates the main_server through a subprocess - internal API"""

        super().create_server()

        self.logger.info("Copying files to server")
        files_copy = self.files.copy()
        self.files = {}
        for file, data in files_copy.items():
            self.update_file(file, data)
        self.logger.debug("Finished copying files to server")

    def request(
        self,
        request_details: dict,
    ) -> None:
        if "file" in request_details:
            file = request_details["file"]
            if file not in self.files:
                self.logger.exception(
                    f"File {file} not in files! Files are {self.files.keys()}"
                )
                raise Exception(
                    f"File {file} not in files! Files are {self.files.keys()}"
                )

        super().request(request_details)

    def update_file(self, file: str, current_state: str) -> None:
        """Updates files in the system - external API"""

        self.logger.info(f"Updating file: {file}")
        self.files[file] = current_state

        self.logger.debug("Creating notification dict")
        file_notification: dict = {
            "command": "FileNotification",
            "file": file,
            "remove": False,
            "contents": self.files[file],
        }

        self.logger.debug("Notifying server of file update")
        super().request(file_notification)

    def remove_file(self, file: str) -> None:
        """Removes a file from the main_server - external API"""
        if file not in list(self.files.keys()):
            self.logger.exception(
                f"Cannot remove file {file} as file is not in file database!"
            )
            raise CollegamentoError(
                f"Cannot remove file {file} as file is not in file database!"
            )

        self.logger.info("Notifying server of file deletion")
        file_notification: dict = {
            "command": "FileNotification",
            "file": file,
            "remove": True,
        }
        self.logger.debug("Notifying server of file removal")
        super().request(file_notification)


class FileServer(SimpleServer):
    """File handling variant of SimpleServer"""

    def __init__(
        self,
        commands: dict[str, USER_FUNCTION],
        response_queue: GenericQueueClass,
        requests_queue: GenericQueueClass,
        logger: Logger,
    ) -> None:
        self.files: dict[str, str] = {}

        super().__init__(
            commands,
            response_queue,
            requests_queue,
            logger,
            ["FileNotification"],
        )

    def handle_request(self, request: Request) -> None:
        if "file" in request and request["command"] != "FileNotification":
            file = request["file"]
            request["file"] = self.files[file]

        super().handle_request(request)
