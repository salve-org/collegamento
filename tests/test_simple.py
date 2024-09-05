from time import sleep

from collegamento import (
    USER_FUNCTION,
    Request,
    Response,
    SimpleClient,
    SimpleServer,
)


def foo(server: "SimpleServer", bar: Request) -> bool:
    if bar["command"] == "test":
        return True
    return False


def main():
    commands: dict[str, tuple[USER_FUNCTION, bool]] = {
        "test": (foo, False),
        "testMulti": (foo, True),
    }
    context = SimpleClient(commands)  # type: ignore

    output = context.request({"command": "test"})
    assert output is None
    id1 = context.request({"command": "testMulti"})
    id2 = context.request({"command": "testMulti"})

    sleep(1)

    output1: Response | None = context.get_response(id1)
    output2: Response | None = context.get_response(id2)
    assert output1 and output2

    context.add_command("test2", foo)
    context.add_command("testMulti2", foo, True)

    output = context.request({"command": "test2"})
    assert output is None
    id2 = context.request({"command": "testMulti2"})
    id2 = context.request({"command": "testMulti2"})

    sleep(1)

    output1: Response | None = context.get_response(id1)
    output2: Response | None = context.get_response(id2)
    assert output1 and output2

    context.kill_IPC()


if __name__ == "__main__":
    main()
