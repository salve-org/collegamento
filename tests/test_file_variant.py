from time import sleep

from collegamento import FileClient, FileServer, Request, Response


def func(server: FileServer, request: Request) -> bool:
    return True


def split_str(server: FileServer, arg: Request) -> list[str]:
    file = arg["file"]  # type: ignore
    return file.split(" ")


def test_file_variants():
    context = FileClient({"test": func})

    context.update_file("test", "test contents")
    context.request({"command": "test"})

    sleep(1)

    output: list[Response] = context.get_response("test")
    assert output is not None  # noqa: E711
    assert output[0]["result"] is True  # noqa: E712 # type: ignore

    context.add_command("test1", split_str)
    context.request({"command": "test1", "file": "test"})

    sleep(1)

    output = context.get_response("test1")
    assert output is not None  # noqa: E711
    assert output[0]["result"] == ["test", "contents"]  # noqa: E712 # type: ignore

    assert context.all_ids == []

    context.kill_IPC()


if __name__ == "__main__":
    test_file_variants()
