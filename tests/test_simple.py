from time import sleep

from collegamento import USER_FUNCTION, Request, Response, SimpleClient


def foo(bar: Request) -> bool:
    if bar["command"] == "test":
        return True
    return False


def test_Client_Server():
    commands: dict[str, USER_FUNCTION] = {"test": foo}
    context = SimpleClient(commands)

    context.request({"command": "test"})

    sleep(1)

    context.add_command("test1", foo)

    sleep(1)

    output: Response | None = context.get_response("test")

    assert output is not None  # noqa: E711
    assert output["result"] == True  # noqa: E712 # type: ignore

    context.request({"command": "test1"})

    sleep(1)

    output: Response | None = context.get_response("test1")
    assert output is not None  # noqa: E711
    assert output["result"] == False  # noqa: E712 # type: ignore

    assert context.all_ids == []

    context.kill_IPC()
