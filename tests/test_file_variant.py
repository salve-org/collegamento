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
    context.update_file("test2", "test contents2")
    sleep(1)
    context.create_server()
    context.request("test")

    sleep(1)

    output: Response = context.get_response("test")  # type: ignore
    assert output is not None  # noqa: E711
    assert output["result"] is True  # noqa: E712 # type: ignore

    context.add_command("test1", split_str, True)
    context.request("test1", file="test")
    context.request("test1", file="test2")

    sleep(1)

    output: list[Response] = context.get_response("test1")  # type: ignore
    assert output is not None  # noqa: E711
    assert output[0]["result"] == ["test", "contents"]  # noqa: E712 # type: ignore
    assert output[1]["result"] == ["test", "contents2"]  # noqa: E712 # type: ignore

    assert context.all_ids == []

    context.kill_IPC()


if __name__ == "__main__":
    test_file_variants()
