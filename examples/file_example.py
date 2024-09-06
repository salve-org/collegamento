from time import sleep

from collegamento import FileClient, FileServer, Request, Response


def split_str(server: "FileServer", arg: Request) -> list[str]:
    file = arg["file"]  # type: ignore
    return file.split(" ")


def main():
    context = FileClient({"test": split_str})

    context.update_file("test", "test contents")
    sleep(1)
    context.request("test", file="test")

    sleep(1)

    output: Response = context.get_response("test")  # type: ignore
    print(output)

    context.kill_IPC()


if __name__ == "__main__":
    main()
