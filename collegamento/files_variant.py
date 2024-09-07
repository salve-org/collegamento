from typing import NotRequired

from .client_server import (
    COMMANDS_MAPPING,
    USER_FUNCTION,
    Client,
    CollegamentoError,
    Request,
    RequestQueueType,
    ResponseQueueType,
    Server,
)


class FileRequest(Request):
    # There may be commands that don't require a file but some might
    file: NotRequired[str]


def update_files(server: "FileServer", request: Request) -> None:
    file: str = request["file"]  # type: ignore

    if request["remove"]:  # type: ignore
        server.files.pop(file)
        return

    contents: str = request["contents"]  # type: ignore
    server.files[file] = contents


class FileClient(Client):
    """File handling variant of SImpleClient. Extra methods:
    - FileClient.update_file()
    - FileClient.remove_file()
    """

    def __init__(
        self, commands: COMMANDS_MAPPING, id_max: int = 15_000
    ) -> None:
        self.files: dict[str, str] = {}

        commands["FileNotification"] = (update_files, True)

        super().__init__(commands, id_max, FileServer)

    def create_server(self) -> None:
        """Creates the main_server through a subprocess - internal API"""

        super().create_server()

        for file, data in self.files.items():
            self.update_file(file, data)

    def request(self, command: str, **kwargs) -> None:
        file: str | None = kwargs.get("file")
        if file and file not in self.files:
            raise CollegamentoError(
                f"File {file} not in files! Files are {self.files.keys()}"
            )

        super().request(command, **kwargs)

    def update_file(self, file: str, current_state: str) -> None:
        """Updates files in the system - external API"""

        self.files[file] = current_state

        super().request(
            "FileNotification",
            file=file,
            remove=False,
            contents=self.files[file],
        )

    def remove_file(self, file: str) -> None:
        """Removes a file from the main_server - external API"""
        if file not in list(self.files.keys()):
            raise CollegamentoError(
                f"Cannot remove file {file} as file is not in file database!"
            )

        super().request("FileNotification", file=file, remove=True)


class FileServer(Server):
    """File handling variant of SimpleServer"""

    def __init__(
        self,
        commands: dict[str, tuple[USER_FUNCTION, bool]],
        requests_queue: RequestQueueType,
        response_queue: ResponseQueueType,
    ) -> None:
        self.files: dict[str, str] = {}

        super().__init__(
            commands,
            requests_queue,
            response_queue,
            ["FileNotification"],
        )

    def handle_request(self, request: Request) -> None:
        if "file" in request and request["command"] != "FileNotification":
            request["file"] = self.files[request["file"]]

        super().handle_request(request)
