from time import sleep

from collegamento import USER_FUNCTION, FileClient, Request, Response


def func(test_arg: Request) -> bool:
    return True


def split_str(arg: Request) -> list[str]:
    file = arg["file"]  # type: ignore
    return file.split(" ")


def test_file_variants():
    commands: dict[str, USER_FUNCTION] = {"test": func}
    context = FileClient(commands)

    context.update_file("test", "test contents")
    context.request({"command": "test"})

    sleep(1)

    output: Response | None = context.get_response("test")
    assert output is not None  # noqa: E711
    assert output["result"] is True  # noqa: E712 # type: ignore

    context.add_command("test1", split_str)
    context.request({"command": "test1", "file": "test"})

    sleep(1)

    output: Response | None = context.get_response("test1")
    assert output is not None  # noqa: E711
    assert output["result"] == ["test", "contents"]  # noqa: E712 # type: ignore

    assert context.all_ids == []

    context.kill_IPC()


if __name__ == "__main__":
    test_file_variants()
