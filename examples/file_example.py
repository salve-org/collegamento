from time import sleep

from collegamento import USER_FUNCTION, FileClient, Request, Response, FileServer


def split_str(server: "FileServer", arg: Request) -> list[str]:
    file = arg["file"]  # type: ignore
    return file.split(" ")


def main():
    commands: dict[str, USER_FUNCTION] = {"test": split_str}
    context = FileClient(commands)

    context.update_file("test", "test contents")
    sleep(1)
    context.request({"command": "test", "file": "test"})

    sleep(1)

    output: Response | None = context.get_response("test")
    print(output)

    context.kill_IPC()


if __name__ == "__main__":
    main()
